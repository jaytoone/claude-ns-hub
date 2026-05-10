# Tool Hints: ml-training
**Trigger**: NIPA server, training monitoring, PyTorch/HuggingFace tasks

## Native tools first (Bash via SSH)
```bash
ssh nipa 'tail -100 /path/to/train.log'   # training log
ssh nipa 'nvidia-smi'                      # GPU status
ssh nipa 'ps aux | grep torchrun'          # process check
```

## Key file paths (NIPA server)
- Training script: `scripts/train_hf_multifile_full.py`
- Config: `configs/train_config_full_05b.yaml`
- Data: `/home/work/vidraft/data/raw/`

## Known env traps
- llama-server: remove `-fa on` flag (causes SIGABRT)
- WandB DDP: `start_method="thread"` required
- WandB project format: `nave94-vidraft/<name>`
- SelfEvalHead zero-gradient: `enable_self_eval: false` + `strict=False`

## MCP tools (remote terminal if needed)
- `mcp__claude-flow__terminal_create` — create remote terminal session
- `mcp__claude-flow__terminal_execute` — execute command
