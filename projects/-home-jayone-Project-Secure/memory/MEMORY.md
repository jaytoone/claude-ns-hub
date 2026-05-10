# Secure Project Memory

## Project: PacketAnal v1.5.2
- 내부망 보안 위협 실시간 탐지/분석 시스템
- Stack: Python 3.11, FastAPI, SQLAlchemy, Scapy, SQLite, React 18
- Git repo: master branch

## 수집 환경 (3개)
| # | 환경 | 식별 | 수집 방식 |
|---|------|------|-----------|
| 1 | 원격 노트북 | `toomu@100.121.173.91` (Tailscale) | deploy_agent.ps1 + dumpcap → SSH sync |
| 2 | 로컬 Windows | `192.168.0.2` / `192.168.0.125` DESKTOP-8HIUJU8 | dumpcap.exe → **D:\PacketAnal\** (C: 아님, 56e8ddf) rolling .pcapng ~97MB |
| 3 | 로컬 WSL2 | 동일 물리 PC | scripts/start_capture.sh → agent/capture.py |

**AnyDesk 침해 이슈 귀속: 환경 #2 (로컬 Windows)**
- 비인가 설치: 2023-12-12, Machine ID: 3a65b87877582afbfa241ee33d710e2c
- 공격자 자발적 제거 (PacketAnal 탐지 후)
- 현재 상태: 클린

## Key Paths
- Backend: `api/` (FastAPI)
- Capture agent: `agent/capture.py`
- PCAP analysis: `api/pcap/` (pipeline, parser, protocol_decoder, identity_extractor)
- Threat detection: `api/analyzer/` (signature, anomaly, exfiltration, ja3_fingerprinter, beaconing_detector)
- Alert system: `api/alert/notifier.py` (JSONL log + Windows toast)
- Forensics: `api/forensics/`
- DB models: `api/models/packet.py`
- Sync script: `scripts/sync_remote_captures.sh` (환경 #1 원격 동기화)
- Alert watcher: `scripts/watch_alerts.py`

## v1.5 암호화 트래픽 탐지 (2026-03-22)
- `api/analyzer/ja3_fingerprinter.py` - JA3 MD5 + SSLBL 피드 (105 해시)
- `api/analyzer/beaconing_detector.py` - CV<0.3 시계열 C2 탐지, IPv4+IPv6 사설대역
- `api/pcap/protocol_decoder.py` - _parse_client_hello() JA3 필드 추출
- pipeline.py 통합, 54/54 탐지율 100%

## v1.5.1 Alert Notification System (2026-03-22)
- `api/alert/notifier.py` - CRITICAL/HIGH만, 5분 중복억제, JSONL 일별 로그
- Windows toast: WSL2→PowerShell 브릿지, CRITICAL만 팝업
- `scripts/watch_alerts.py` - 실시간 ANSI 컬러 감시 CLI
- alert log: `data/alerts/alert_YYYYMMDD.jsonl`

## Windows 192.168.0.2 TCP 스택 특이사항 (2026-04-17 발견)
- 동적 ephemeral 포트 범위: **1024–15000** (기본 49152-65535 아님 — Hyper-V/WSL2/Docker 영향)
- TermService(RDP 3389) **Stopped + Disabled** (commit db02ebf)
- 결과: 3389/3515 등 저번호 포트가 **정상 ephemeral 할당** 대상 → RDP 오탐 다수 발생
- 2026-04-17: remote_access_detector.py에 src_port∈{80,443,53,25,8080,8443} 가드 추가 (`_EPHEMERAL_REPLY_SERVICE_PORTS`)
- 회귀 테스트: tests/unit/test_remote_access_detector.py (6 pass)

## AnyDesk 침해 사고 (2026-03-22 최종)
- 환경: #2 로컬 Windows (192.168.0.125)
- 설치일: 2023-12-12 (ProgramData\recordings CreationTime)
- 운영: 약 2년 3개월 (비인가)
- 14.56.30.202 = CRD 릴레이 (오탐 수정됨, AnyDesk 아님)
- 현재: AnyDesk 제거됨, persistence 없음, 시스템 클린
- 포렌식: C:\Users\Jayone\Desktop\AnyDesk_Evidence_20260322\ (삭제됨)
