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