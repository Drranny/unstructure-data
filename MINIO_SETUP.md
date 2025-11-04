# MinIO VPN 접속 설정 가이드

서버에서 실행하는 프로그램이 VPN이 필요한 MinIO에 접속하는 방법입니다.

## 📋 MinIO 정보

- **API 포트**: `192.168.106.12:9000` (S3 API 접속용)
- **Console 포트**: `192.168.106.12:9001` (웹 UI 접속용)
- **Bucket**: `2024-fabric`
- **API Access Key**: `fabric`
- **API Secret Key**: `fabric12##`
- **⚠️ Console 로그인**: API Access Key와 다를 수 있음 (관리자에게 확인)

## 🚀 빠른 설정 (로컬에서 4개 터미널 실행)

### 터미널 1: Console Reverse Port Forwarding
```bash
ssh -R 9001:192.168.106.12:9001 yjjang@220.149.241.207
```

### 터미널 2: Console Local Port Forwarding (로컬 접속용)
```bash
ssh -L 9001:localhost:9001 yjjang@220.149.241.207
```

### 터미널 3: API Reverse Port Forwarding
```bash
ssh -R 9000:192.168.106.12:9000 yjjang@220.149.241.207
```

### 터미널 4: API Local Port Forwarding (로컬 접속용)
```bash
ssh -L 9000:localhost:9000 yjjang@220.149.241.207
```

**백그라운드 실행**: 각 명령어 끝에 `-N -f` 추가
```bash
ssh -R 9001:192.168.106.12:9001 -N -f yjjang@220.149.241.207
```

## 🌐 접속 방법

### 로컬 브라우저
- **MinIO Console**: http://localhost:9001
  - 로그인: `fabric` / `fabric12##` (API Access Key와 동일할 수도, 다를 수도 있음)
  - 안 되면: MinIO 관리자에게 Console 계정 확인

### 서버에서 Python
```python
from minio import Minio

client = Minio(
    "localhost:9000",  # API 포트
    access_key="fabric",
    secret_key="fabric12##",
    secure=False
)

# 버킷 리스트
buckets = client.list_buckets()
for bucket in buckets:
    print(bucket.name)

# 객체 리스트
objects = client.list_objects("2024-fabric", recursive=True)
for obj in objects:
    print(obj.object_name)
```

## ⚠️ 주의사항

1. **VPN 연결 유지**: 로컬에서 VPN이 켜져 있어야 함
2. **SSH 터널 유지**: 4개 터널이 모두 실행 중이어야 함
3. **Console 로그인**: API Access Key로 안 되면 별도 관리자 계정 필요

## 🔍 문제 해결

### Console 로그인이 안 되는 경우
- API Access Key (`fabric` / `fabric12##`)와 다를 수 있음
- MinIO 관리자에게 Console 계정 정보 확인

### API 접속이 안 되는 경우
```bash
# 서버에서 테스트
curl http://localhost:9000
python3 -c "from minio import Minio; client = Minio('localhost:9000', 'fabric', 'fabric12##', False); print([b.name for b in client.list_buckets()])"
```

### 포트 포워딩 확인
```bash
# 서버에서 포트 확인
netstat -tuln | grep 9000
netstat -tuln | grep 9001
```

