# 로컬에서만 사용하기 (간단 가이드)

공유하지 않고 본인 컴퓨터에서만 사용하시는 경우, 이 가이드만 따라하시면 됩니다.

**참고**: SSH 서버에서 실행하는 경우 [SSH_SERVER_GUIDE.md](SSH_SERVER_GUIDE.md)를 참고하세요.

## 🚀 실행 방법 (3단계)

### Step 1: 패키지 설치

터미널을 열고 프로젝트 폴더에서 실행:

```bash
cd /home/yjjang/unstructure
pip install -r requirements.txt
```

**시간**: 약 5-10분 정도 걸립니다.

### Step 2: 앱 실행

```bash
streamlit run app.py
```

### Step 3: 브라우저 접속

자동으로 브라우저가 열리거나, 다음 주소를 직접 입력:

```
http://localhost:8501
```

**끝!** 이제 사용 가능합니다. 🎉

---

## 📌 자주 묻는 질문

### Q: localhost:8501이 뭔가요?

- **localhost**: "내 컴퓨터"를 뜻합니다
- **8501**: 포트 번호 (Streamlit이 사용하는 기본 포트)
- 즉, "내 컴퓨터의 8501번 포트에서 실행 중인 앱"이라는 의미입니다

### Q: 다른 포트로 실행하고 싶어요

```bash
streamlit run app.py --server.port 8080
```

그럼 `http://localhost:8080`으로 접속하면 됩니다.

### Q: 앱을 끄려면?

터미널에서 `Ctrl + C`를 누르면 됩니다.

### Q: 컴퓨터를 껐다 켜도 되나요?

네, 괜찮습니다. 다시 실행하려면:

```bash
cd /home/yjjang/unstructure
streamlit run app.py
```

---

## 🧪 테스트 방법

### 텍스트 파일 테스트

1. 앱이 실행된 브라우저에서
2. 왼쪽 사이드바 **"샘플 텍스트 테스트"** 버튼 클릭
3. 또는 파일 업로드로 `.txt` 파일 선택

### 이미지 파일 테스트

1. 앱에서 **"파일 업로드"**
2. `.jpg`, `.png` 파일 선택
3. 결과 확인

### 새로운 파일로 테스트

```bash
# 새 텍스트 파일 만들기
nano test.txt
# 또는
gedit test.txt

# 내용 입력 후 저장
# 앱에서 업로드하여 테스트
```

---

## 🐛 문제 해결

### "포트가 이미 사용 중" 오류

```bash
# 다른 포트로 실행
streamlit run app.py --server.port 8502
```

### "모듈을 찾을 수 없습니다" 오류

```bash
# 패키지 재설치
pip install --upgrade -r requirements.txt
```

### 패키지 설치가 너무 오래 걸려요

정상입니다! 특히 PyTorch는 2GB 이상이라 시간이 걸립니다.
인터넷 연결을 확인하고 기다리세요.

---

## ✅ 체크리스트

- [ ] `pip install -r requirements.txt` 완료
- [ ] `streamlit run app.py` 실행 성공
- [ ] 브라우저에서 `localhost:8501` 접속 확인
- [ ] 텍스트 파일 업로드 테스트
- [ ] 이미지 파일 업로드 테스트

---

## 📝 요약

**배포는 선택사항입니다!** 

로컬에서만 사용하시면:
- ✅ GitHub, Hugging Face 계정 불필요
- ✅ 인터넷 공개 불필요
- ✅ 파일만 업로드하면 바로 사용 가능
- ✅ 본인 컴퓨터에서만 실행


