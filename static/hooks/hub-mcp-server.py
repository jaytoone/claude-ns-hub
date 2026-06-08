#!/usr/bin/env python3
"""
NS Hub MCP Server — stdio JSON-RPC 2.0 transport
Exposes hub task dispatch/completion tools to Claude Code sessions.

Usage:
  python3 hub-mcp-server.py --proj MOAT --hub-url http://100.x.x.x:9001

Claude Code connects via --mcp-config pointing to a JSON file that references this script.
The session calls get_pending_task() at start, report_task_complete() on finish.
"""
import argparse
import json
import sys
import urllib.request
import datetime


def _hub_request(url: str, method: str = "GET", body: dict = None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode() if body else None,
        headers={"Content-Type": "application/json"} if body else {},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


TOOLS = [
    {
        "name": "get_pending_task",
        "description": (
            "Fetch the next queued task (stone) assigned to this exec session from the hub. "
            "Call this at the start of your session to know what to work on. "
            "Returns task_id, text (full task description), conversation history, and metadata."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "report_task_complete",
        "description": (
            "Report that you have completed a task (stone). "
            "Call this after finishing work on a task. "
            "The hub will mark the task as pending_confirmation and notify the user."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The stone/milestone ID (e.g. 'M1090')",
                },
                "summary": {
                    "type": "string",
                    "description": "One-line past-tense summary of what was done (max 120 chars)",
                },
                "star_relation": {
                    "type": "string",
                    "description": "One sentence describing how this completion advances the parent goal",
                },
                "status": {
                    "type": "string",
                    "enum": ["pending_confirmation", "skipped"],
                    "description": "Use 'pending_confirmation' for completed work, 'skipped' if task was not actionable",
                },
            },
            "required": ["task_id", "summary"],
        },
    },
    {
        "name": "reply_to_stone",
        "description": (
            "Post a reply comment to a stone (Q&A mode). "
            "Use when conversation[-1].role == 'user' — the user asked a follow-up question. "
            "Do NOT change status. Post ≤3 lines answering the question."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Stone/milestone ID"},
                "message": {"type": "string", "description": "Reply text, ≤3 lines"},
            },
            "required": ["task_id", "message"],
        },
    },
    {
        "name": "get_task_details",
        "description": "Get full details of a specific task including conversation history and sub-stones.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Stone/milestone ID"},
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "get_session_overview",
        "description": (
            "Get a full status overview for this session: queued tasks, stones awaiting your reply, "
            "stones needing clarification, and paused stones. "
            "Call this at session start to understand the complete landscape of work."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
]


def handle_get_pending_task(proj_id: str, hub_url: str) -> dict:
    try:
        data = _hub_request(f"{hub_url}/api/northstar/{proj_id}/milestones")
        milestones = data if isinstance(data, list) else data.get("milestones", [])
        queued = [
            m for m in milestones
            if m.get("status") == "queued"
            and not m.get("held")
            and not m.get("done")
            and str(m.get("text", "")).strip()
        ]
        if not queued:
            return {
                "has_task": False,
                "message": "No queued tasks. Session is idle.",
                "queued_count": 0,
            }
        stone = queued[0]
        return {
            "has_task": True,
            "task_id": stone.get("id"),
            "text": stone.get("text", ""),
            "conversation": stone.get("conversation", []),
            "queued_count": len(queued),
            "substar": stone.get("substar_id"),
            "added_at": stone.get("user_added_at"),
        }
    except Exception as e:
        return {"error": str(e), "has_task": False}


def handle_report_task_complete(
    proj_id: str, hub_url: str,
    task_id: str, summary: str,
    star_relation: str = "", status: str = "pending_confirmation"
) -> dict:
    try:
        patch = {
            "status": status,
            "model_used": "claude-mcp",
            "pending_confirm_at": datetime.datetime.now().isoformat(),
            "append_message": {"role": "claude", "text": summary[:120]},
        }
        if star_relation:
            patch["star_relation"] = star_relation
        result = _hub_request(
            f"{hub_url}/api/northstar/{proj_id}/milestones/{task_id}",
            method="PATCH",
            body=patch,
        )
        return {"ok": result.get("ok", False), "task_id": task_id, "status": status}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def handle_get_session_overview(proj_id: str, hub_url: str) -> dict:
    try:
        data = _hub_request(f"{hub_url}/api/northstar/{proj_id}/milestones")
        milestones = data if isinstance(data, list) else data.get("milestones", [])

        def _awaits_user(m):
            conv = m.get("conversation") or []
            return bool(conv) and conv[-1].get("role") == "user"

        queued = [
            m for m in milestones
            if m.get("status") == "queued" and not m.get("held") and not m.get("done")
        ]
        pending_replies = [
            m for m in milestones
            if _awaits_user(m)
        ]
        clarifications = [
            m for m in milestones
            if m.get("status") == "needs_clarification" and not (m.get("clarification_answer") or "").strip()
        ]
        paused = [
            m for m in milestones
            if m.get("status") in ("queued", "pending") and _awaits_user(m)
        ]

        def _stone_summary(m):
            conv = m.get("conversation") or []
            last_user = next((e.get("text", "")[:100] for e in reversed(conv) if e.get("role") == "user"), "")
            return {
                "task_id": m.get("id"),
                "text_preview": (m.get("text") or "")[:120],
                "is_qa": _awaits_user(m),
                "last_user_message": last_user or None,
            }

        return {
            "queued": [_stone_summary(m) for m in queued],
            "pending_replies": [_stone_summary(m) for m in pending_replies],
            "clarifications": [
                {"task_id": m.get("id"), "question": (m.get("clarification_question") or "")[:120]}
                for m in clarifications
            ],
            "paused_count": len(paused),
            "summary": f"{len(queued)} queued, {len(pending_replies)} pending reply, {len(clarifications)} clarification(s)",
        }
    except Exception as e:
        return {"error": str(e)}


def handle_reply_to_stone(proj_id: str, hub_url: str, task_id: str, message: str) -> dict:
    try:
        patch = {
            "append_message": {"role": "claude", "text": message},
        }
        result = _hub_request(
            f"{hub_url}/api/northstar/{proj_id}/milestones/{task_id}",
            method="PATCH",
            body=patch,
        )
        return {"ok": result.get("ok", False), "task_id": task_id}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def handle_get_task_details(proj_id: str, hub_url: str, task_id: str) -> dict:
    try:
        data = _hub_request(f"{hub_url}/api/northstar/{proj_id}/milestones")
        milestones = data if isinstance(data, list) else data.get("milestones", [])
        stone = next((m for m in milestones if m.get("id") == task_id), None)
        if not stone:
            return {"error": f"Task {task_id} not found"}
        return stone
    except Exception as e:
        return {"error": str(e)}


def send(obj: dict):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proj", required=True)
    parser.add_argument("--hub-url", required=True)
    args = parser.parse_args()

    proj_id = args.proj
    hub_url = args.hub_url.rstrip("/")

    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            msg = json.loads(raw_line)
        except Exception:
            continue

        msg_id = msg.get("id")
        method = msg.get("method", "")
        params = msg.get("params", {})

        # MCP initialization handshake
        if method == "initialize":
            send({
                "jsonrpc": "2.0", "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "ns-hub", "version": "1.0.0"},
                },
            })

        elif method == "initialized":
            pass  # notification, no response

        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}})

        elif method == "tools/call":
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            try:
                if tool_name == "get_pending_task":
                    result = handle_get_pending_task(proj_id, hub_url)
                elif tool_name == "get_session_overview":
                    result = handle_get_session_overview(proj_id, hub_url)
                elif tool_name == "reply_to_stone":
                    result = handle_reply_to_stone(proj_id, hub_url,
                        task_id=tool_args.get("task_id", ""),
                        message=tool_args.get("message", ""),
                    )
                elif tool_name == "report_task_complete":
                    result = handle_report_task_complete(
                        proj_id, hub_url,
                        task_id=tool_args.get("task_id", ""),
                        summary=tool_args.get("summary", ""),
                        star_relation=tool_args.get("star_relation", ""),
                        status=tool_args.get("status", "pending_confirmation"),
                    )
                elif tool_name == "get_task_details":
                    result = handle_get_task_details(proj_id, hub_url, tool_args.get("task_id", ""))
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                send({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
                        "isError": "error" in result,
                    },
                })
            except Exception as e:
                send({
                    "jsonrpc": "2.0", "id": msg_id,
                    "result": {
                        "content": [{"type": "text", "text": json.dumps({"error": str(e)})}],
                        "isError": True,
                    },
                })

        elif method == "ping":
            send({"jsonrpc": "2.0", "id": msg_id, "result": {}})

        # Ignore unknown notifications (no id = notification)
        elif msg_id is not None:
            send({
                "jsonrpc": "2.0", "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            })


if __name__ == "__main__":
    main()
