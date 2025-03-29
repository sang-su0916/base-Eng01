# 📚 영어학원 문제풀이 시스템

영어학원에서 사용할 수 있는 문제풀이 자동화 웹 애플리케이션입니다.

## 🌟 주요 기능

### 👩‍🏫 선생님용 기능
- 문제 출제 (직접 입력, CSV 업로드, GitHub 연동)
- 학생별 문제 할당
- 결과 확인 및 피드백

### 👧 학생용 기능
- 문제 풀이
- 답안 제출
- 결과 확인

## 🚀 시작하기

### 설치 방법
1. 저장소 클론
```bash
git clone [repository-url]
cd base-Eng01
```

2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

4. 애플리케이션 실행
```bash
streamlit run app.py
```

### 사용 방법

#### 선생님용
1. 사이드바에서 "선생님" 선택
2. "문제 출제" 탭에서 문제 생성
3. "학생 관리" 탭에서 학생 등록 및 문제 할당
4. "결과 확인" 탭에서 학생들의 답안 확인

#### 학생용
1. 사이드바에서 "학생" 선택
2. 이름 입력
3. 할당된 문제 풀이
4. 답안 제출

## 📝 데이터 관리

### 문제 데이터
- `data/problems.json`: 문제 데이터 저장
- `data/problems.csv`: CSV 형식 문제 데이터

### 학생 데이터
- `data/students.json`: 학생 정보 저장
- `data/assignments.json`: 문제 할당 정보 저장

## 🔧 개발 환경
- Python 3.8+
- Streamlit
- pandas
- numpy

## 📚 라이선스
이 프로젝트는 MIT 라이선스를 따릅니다.

## 👥 기여하기
1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request

## 🚀 배포 방법

### Streamlit Cloud 배포
1. GitHub에 프로젝트를 푸시합니다.
2. [Streamlit Cloud](https://share.streamlit.io/)에 접속합니다.
3. GitHub 계정으로 로그인합니다.
4. "New app" 버튼을 클릭합니다.
5. 저장소, 브랜치, 메인 파일(app.py)을 선택합니다.
6. "Deploy!" 버튼을 클릭합니다.

### 로컬 실행
1. Python 3.8 이상을 설치합니다.
2. 가상환경을 생성하고 활성화합니다:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. 필요한 패키지를 설치합니다:
   ```bash
   pip install -r requirements.txt
   ```
4. 애플리케이션을 실행합니다:
   ```bash
   streamlit run app.py
   ```

## 🔧 환경 설정

### 필수 환경 변수
`.env` 파일을 생성하고 다음 변수들을 설정합니다:
```
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### Java 설치
LanguageTool을 사용하기 위해 Java를 설치해야 합니다:
- Windows: [Java JDK](https://adoptium.net/) 다운로드 및 설치
- Linux: `sudo apt-get install default-jdk`
- macOS: `brew install openjdk`

## 📝 주요 기능

### 👩‍🏫 선생님용 기능
- 문제 출제 시스템
- 학생별 문제 할당
- 결과 확인 및 피드백
- 통계 및 리포트

### 👧 학생용 기능
- 문제 풀이
- 자동 채점
- 첨삭 피드백
- 학습 진도 추적

## 🔒 보안
- API 키는 환경 변수로 관리
- 사용자 인증 시스템
- 데이터 암호화

## 📊 데이터 관리
- JSON 파일 기반 데이터 저장
- 자동 백업 시스템
- 데이터 마이그레이션 도구

## 🐛 알려진 이슈
- LanguageTool 관련 Java 설치 필요
- 일부 브라우저에서의 호환성 문제

## 📈 향후 계획
- 학생별 로그인 시스템
- Google Sheet 연동
- 통계 및 리포트 기능
- 모바일 앱 개발