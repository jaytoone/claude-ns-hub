# PacketAnal 프로젝트 상태

## 현재 상태
- pcap 파일 업로드 + 분석 파이프라인 구현 완료 (2026-02-18)
- 데이터 송출 탐지 문서 추가 완료 (2026-02-19)

## 구현된 기능
- `api/pcap/`: pcap 파서(parser.py), 프로토콜 디코더(protocol_decoder.py), 신원추출(identity_extractor.py), 파이프라인(pipeline.py)
- `api/routers/pcap.py`: 10개 엔드포인트 (upload, sessions, packets, threats, http, dns, tls, identities)
- `api/models/pcap_session.py`: pcap_sessions 테이블
- `dashboard/src/pages/PcapAnalysis.jsx`: 업로드 + 결과 UI (이모지 없음)
- `uploads/pcap/`: 업로드 파일 저장 위치

## 추가된 문서 (docs/)
- `Data_Exfiltration_Detection.md`: 데이터 송출 탐지 솔루션 (ss, nethogs, bandwhich, auditd, tcpdump)
- `Exfil_Scan_Result_20260219.md`: 2026-02-19 스캔 결과 (전부 정상, 신뢰 조직만 연결)

## 핵심 설계
- pcap 파싱: scapy PcapReader (스트리밍, 메모리 효율적)
- agent_id = `pcap:{session_id}` 형태로 기존 packets 테이블 재사용
- HTTP/DNS/TLS 자동 디코딩, SNI 추출, 신원 추출(User-Agent, MAC OUI, 쿠키)
- 기존 SignatureDetector, AnomalyDetector와 연동

## 미해결 / 다음 작업
- TLS sslkeylog 파일 업로드로 HTTPS 복호화 (Phase 3)
- TCP 스트림 재조합 (flow_reconstructor.py 미구현)
- 포트 스캔 탐지가 위협을 생성하지 않음 (SignatureDetector "Context에 변수 없음" 경고)
