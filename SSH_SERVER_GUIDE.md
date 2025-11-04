# SSH 서버에서 실행하기 가이드

SSH로 서버에 접속해서 작업하는 경우입니다.

**참고**: 로컬 컴퓨터에서만 사용하는 경우 [LOCAL_USE_ONLY.md](LOCAL_USE_ONLY.md)를 참고하세요.

## 🔍 현재 상황

- **서버**: `/home/yjjang/unstructure` (서버의 경로)
- **패키지 설치**: 서버에 설치됨
- **앱 실행**: 서버에서 실행됨
- **접속**: SSH 터널링 필요

---

## 🚀 실행 방법

### Step 1: 서버에서 패키지 설치

SSH 연결된 터미널에서:

```bash
# 이미 서버에 있으니 바로 실행
cd /home/yjjang/unstructure
pip install -r requirements.txt
```

**⚠️ 주의**: 
- 서버 관리 권한이 필요할 수 있습니다
- 가상환경 사용을 권장합니다

### Step 2: 서버에서 앱 실행 (백그라운드)

```bash
# 서버에서 실행 (백그라운드로)
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

또는 더 안전하게 (세션 종료 후에도 유지):

```bash
# nohup 사용
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
```

### Step 3: SSH 포트 포워딩 (로컬 컴퓨터에서)

**로컬 컴퓨터**에서 새로운 터미널을 열고:

```bash
ssh -L 8501:localhost:8501 사용자명@서버주소
```

예시:
```bash
ssh -L 8501:localhost:8501 yjjang@server.example.com
```

### Step 4: 로컬 브라우저에서 접속

로컬 컴퓨터의 브라우저에서:

```
http://localhost:8501
```

---

## 🔄 방법 2: SSH 터널링을 먼저 설정하기

### 로컬 컴퓨터에서 (먼저 실행)

```bash
# SSH 터널 생성 (백그라운드)
ssh -N -L 8501:localhost:8501 사용자명@서버주소
```

**옵션 설명**:
- `-N`: 명령 실행 안 함 (터널만 생성)
- `-L 8501:localhost:8501`: 로컬 8501 포트를 서버의 8501 포트로 연결
- 백그라운드 실행: 끝에 `&` 추가

### 서버에서 앱 실행

SSH로 서버 접속한 터미널에서:

```bash
cd /home/yjjang/unstructure
streamlit run app.py --server.port 8501
```

### 로컬 브라우저에서 접속

로컬 컴퓨터 브라우저에서:
```
http://localhost:8501
```

---

## 🎯 방법 3: 서버의 실제 IP/도메인으로 접속 (방화벽 허용 시)

### 서버에서 실행

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 서버 IP 확인

```bash
hostname -I
# 또는
ip addr show
```

### 로컬에서 브라우저 접속

```
http://서버IP주소:8501
```

**⚠️ 주의**: 
- 서버 방화벽에서 8501 포트 허용 필요
- 보안상 위험할 수 있으니 외부 공개 시 주의

---

## 📋 추천 방법 (가장 안전)

### 1. 가상환경 생성 (서버에서)

```bash
cd /home/yjjang/unstructure
python3 -m venv venv
source venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. SSH 터널링 (로컬 컴퓨터에서, 별도 터미널)

```bash
ssh -N -L 8501:localhost:8501 사용자명@서버주소 &
```

### 4. 앱 실행 (서버에서)

```bash
source venv/bin/activate
streamlit run app.py
```

### 5. 접속 (로컬 브라우저)

```
http://localhost:8501
```

---

## 🛑 앱 중지하기

### 실행 중인 Streamlit 종료

서버에서:

```bash
# 프로세스 찾기
ps aux | grep streamlit

# 종료 (PID는 위에서 확인한 번호)
kill PID번호

# 또는 강제 종료
pkill -f streamlit
```

### SSH 터널 종료

로컬 컴퓨터에서:

```bash
# 터널 프로세스 찾기
ps aux | grep "ssh -L"

# 종료
kill PID번호
```

---

## 🔧 문제 해결

### Q: "포트가 이미 사용 중" 오류

서버에서 다른 포트 사용:

```bash
streamlit run app.py --server.port 8502
```

그리고 SSH 터널링도 변경:

```bash
ssh -L 8502:localhost:8502 사용자명@서버주소
```

### Q: "Connection refused" 오류

- 서버에서 앱이 실행 중인지 확인
- SSH 터널링이 올바르게 설정되었는지 확인
- 방화벽 설정 확인

### Q: 세션 끊어져도 계속 실행하고 싶어요

```bash
# screen 또는 tmux 사용
screen -S streamlit
streamlit run app.py
# Ctrl+A, D로 detach

# 다시 연결
screen -r streamlit
```

또는:

```bash
# tmux 사용
tmux new -s streamlit
streamlit run app.py
# Ctrl+B, D로 detach

# 다시 연결
tmux attach -t streamlit
```

---

## 📝 요약

1. **서버에 패키지 설치**: `pip install -r requirements.txt`
2. **서버에서 앱 실행**: `streamlit run app.py`
3. **로컬에서 SSH 터널링**: `ssh -L 8501:localhost:8501 사용자명@서버`
4. **로컬 브라우저 접속**: `http://localhost:8501`

이렇게 하면 서버에서 실행하지만 로컬 브라우저로 접속할 수 있습니다!

## 🔗 MinIO VPN 접속

서버에서 실행하는 프로그램이 VPN이 필요한 MinIO에 접속해야 하는 경우:
- [MINIO_SETUP.md](MINIO_SETUP.md) 참고 

