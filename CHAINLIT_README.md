# 보험 약관 Q&A 챗봇 (Chainlit)

Solar 모델 기반의 보험 약관 질의응답 Chainlit 챗봇입니다.

## 🚀 시작하기

### 1. 의존성 설치

```bash
cd langchain_project
poetry install
```

### 2. 환경 설정

`.env` 파일에 다음을 설정합니다:

```env
# Upstage API (Solar 모델)
UPSTAGE_API_KEY=your_api_key_here

# Qdrant 설정 (기본값)
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

### 3. Qdrant 실행

벡터 데이터베이스가 필요합니다:

```bash
# Docker를 사용하는 경우
docker run -p 6333:6333 qdrant/qdrant

# 또는 Qdrant 서버 직접 실행
qdrant
```

### 4. 데이터 수집 (초기 설정)

보험 약관 문서를 벡터 데이터베이스에 저장합니다:

```bash
python source/ingest/ingest_all.py
```

### 5. 챗봇 실행

```bash
cd langchain_project
poetry run chainlit run source/app/run_chainlit.py -w
```

- `-w` 옵션: 파일 변경 시 자동 새로고침

브라우저에서 `http://localhost:8000`으로 접속합니다.

---

## 📋 기능

✅ **보험 약관 기반 답변**
- Qdrant 벡터 데이터베이스에서 관련 조항 검색
- Solar 모델 (Upstage)로 정확한 답변 생성

✅ **조문 인용**
- 정확한 조항 번호 제시
- 원문 인용으로 신뢰성 보장

✅ **웹 UI**
- Chainlit 기반 직관적인 인터페이스
- 실시간 대화형 상담

✅ **다중 보험 상품 지원**
- 상해보험
- 손해보험
- 질병보험
- 책임보험
- 화재보험

---

## 🏗️ 프로젝트 구조

```
langchain_project/
├── source/
│   ├── app/
│   │   ├── run_chainlit.py      # Chainlit 메인 파일 (웹 챗봇)
│   │   ├── run_qa.py            # CLI 기반 QA
│   │   └── run_graph.py         # LangGraph 워크플로우
│   ├── chains/
│   │   └── qa_chain.py          # QA 체인 구성
│   ├── config/
│   │   └── settings.py          # 설정 파일
│   ├── llm/
│   │   ├── llm.py               # Solar 모델 설정
│   │   └── prompt.py            # 프롬프트 템플릿
│   ├── vectorstore/
│   │   ├── retriever.py         # 문서 검색
│   │   └── formatter.py         # 문서 포맷팅
│   └── ingest/
│       └── ingest_all.py        # 데이터 수집
├── .chainlit/
│   └── config.json              # Chainlit 설정
└── pyproject.toml               # 의존성 관리
```

---

## 🔧 커스터마이징

### 프롬프트 변경

[source/llm/prompt.py](source/llm/prompt.py)에서 `INSURANCE_PROMPT` 수정:

```python
INSURANCE_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    # 커스텀 프롬프트
    ...
    """
)
```

### 검색 결과 수 조정

[source/config/settings.py](source/config/settings.py)에서 `TOP_K` 값 변경:

```python
TOP_K = 10  # 기본값: 5
```

### UI 커스터마이징

[.chainlit/config.json](.chainlit/config.json) 수정

---

## 📚 사용 기술

- **LangChain** v1.2.3 - LLM 체이닝
- **Chainlit** v1.5.0+ - 웹 UI
- **Upstage Solar** - LLM 모델
- **Qdrant** - 벡터 데이터베이스
- **Hugging Face** - 임베딩 모델
- **Python** 3.11+

---

## 🎯 사용 예시

**사용자 입력:**
```
화재보험에서 화재로 인한 손해는 어떻게 보상되나요?
```

**챗봇 응답:**
```
📋 **답변:**

제3조(보상하는 손해)에 따라 화재로 인한 손해는 보장 대상입니다.
- 보장 여부: 네, 보장됩니다
- 근거 조항: 제3조(보상하는 손해)
- 조문 인용: [구체적인 조문 내용]

📚 **참고 약관:**

출처: 화재보험_가공.xml
[관련 약관 전문]
```

---

## 🐛 문제 해결

### Qdrant 연결 오류
- Qdrant 서버가 실행 중인지 확인
- `QDRANT_HOST`, `QDRANT_PORT` 설정 확인

### API 키 오류
- `.env` 파일에 `UPSTAGE_API_KEY` 설정 확인
- Upstage API 키 유효성 확인

### 메모리 부족
- `TOP_K` 값 줄이기
- 배치 처리로 처리량 제한

---

## 📝 라이센스

이 프로젝트는 학습 목적으로 작성되었습니다.

---

## 🤝 기여

개선 사항이나 버그 보고는 언제든지 환영합니다.
