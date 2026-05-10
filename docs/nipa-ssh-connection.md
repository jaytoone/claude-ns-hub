# NIPA Backend.AI SSH 연결 가이드

## 연결 정보

- **Host**: `proxy3.nipa2025.ktcloud.com`
- **Port**: `10572`
- **User**: `work`
- **SSH Key**: `id_container` (Backend.AI 웹에서 다운로드)

## SSH 키 다운로드 방법

1. NIPA 웹사이트 접속: https://www.nipa2025.ktcloud.com/job
2. 로그인
3. 실행 중인 세션에서 "apps" 버튼 클릭
4. "SSH / SFTP" 버튼 클릭
5. "Download SSH Key" 클릭하여 `id_container` 파일 다운로드

## SSH 연결 명령어

### 1. SSH 키 권한 설정
```bash
chmod 600 /path/to/id_container
```

### 2. SSH 연결
```bash
ssh -i /path/to/id_container -p 10572 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null work@proxy3.nipa2025.ktcloud.com
```

### 3. SFTP 연결
```bash
sftp -i /path/to/id_container -P 10572 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null work@proxy3.nipa2025.ktcloud.com
```

### 4. SCP 파일 복사
```bash
scp -i /path/to/id_container -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 10572 -rp /path/to/source work@proxy3.nipa2025.ktcloud.com:~/
```

### 5. Rsync 동기화
```bash
rsync -av -e "ssh -i /path/to/id_container -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 10572" /path/to/source/ work@proxy3.nipa2025.ktcloud.com:~//
```

## vLLM 서버 정보

### 현재 실행 중인 vLLM 설정
```bash
python -m vllm.entrypoints.openai.api_server \
  --model zai-org/GLM-4.7 \
  --trust-remote-code \
  --tensor-parallel-size 8 \
  --max-model-len 32768 \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.95 \
  --max-num-seqs 32 \
  --port 8000 \
  --host 0.0.0.0 \
  --disable-log-requests \
  --disable-frontend-multiprocessing \
  --tool-call-parser glm47 \
  --reasoning-parser glm45 \
  --enable-auto-tool-choice
```

### 주요 설정 값
- **Model**: zai-org/GLM-4.7
- **Max Model Length**: 32768 tokens (← 제한 원인)
- **Tensor Parallel Size**: 8
- **Port**: 8000
- **GPU Memory Utilization**: 95%
- **Max Num Seqs**: 32

## 컨텍스트 제한 해결 방법

현재 `--max-model-len 32768`로 제한되어 있습니다.

### GLM-4.7의 실제 최대 컨텍스트
- **Input**: 200,000 tokens
- **Output**: 128,000 tokens

### vLLM 재시작 방법 (컨텍스트 확장)
1. SSH로 서버 접속
2. vLLM 프로세스 종료
3. `--max-model-len 200000`으로 재시작

```bash
# SSH 접속
ssh -i /path/to/id_container -p 10572 work@proxy3.nipa2025.ktcloud.com

# vLLM 프로세스 확인
ps aux | grep vllm

# 프로세스 종료 (PID 확인 후)
kill <PID>

# 재시작 (200k 컨텍스트)
python -m vllm.entrypoints.openai.api_server \
  --model zai-org/GLM-4.7 \
  --trust-remote-code \
  --tensor-parallel-size 8 \
  --max-model-len 200000 \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.95 \
  --max-num-seqs 32 \
  --port 8000 \
  --host 0.0.0.0 \
  --disable-log-requests \
  --disable-frontend-multiprocessing \
  --tool-call-parser glm47 \
  --reasoning-parser glm45 \
  --enable-auto-tool-choice
```

## 문서 작성일
2026-01-30

## 참고
- Backend.AI 공식 문서: https://webui.docs.backend.ai/en/latest/sftp_to_container/sftp_to_container.html
