# Qdrant DB 데이터 적재 방법

> 전체 보험 XML 데이터를 Qdrant DB에 적재하는 완벽한 가이드

## 📌 전체 실행 순서

```bash
# 1. 가상환경 활성화
poetry shell
# 또는
source .venv/bin/activate

# 2. ingest 폴더 이동
cd langchain_project/ingest

# 3. 보험 파일 선택
python select_insurance_files.py

# 4. Qdrant 적재
python ingest_all.py

# 5. Qdrant Web UI 접속
http://localhost:6333/dashboard
```

---

## 0️⃣ 사전 준비

### ✅ 가상환경 활성화
프로젝트 루트에서 **반드시** Poetry 가상환경을 활성화합니다.
```bash
poetry shell
```

> ⚠️ **주의**: VS Code 커널도 동일한 가상환경으로 맞춰야 합니다.

### ✅ Qdrant 실행 확인

Docker에서 Qdrant이 실행 중인지 확인:
```bash
docker ps | grep qdrant
```

실행되지 않으면 실행:
```bash
docker run -d \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_data:/qdrant/storage \
  qdrant/qdrant
```

---

## 1️⃣ ingest 폴더 이동

```bash
cd langchain_project/ingest
```

폴더 구조 예시:
```
ingest/
 ├─ select_insurance_files.py
 ├─ ingest_all.py
 └─ vectorstore.py
```

---

## 2️⃣ 보험 XML 파일 선택

### 📄 파일 위치
`langchain_project/ingest/select_insurance_files.py`

### 🔧 수정해야 할 부분

**경로 변경**:
```python
RAW_DIR = Path("/Users/본인경로/01.유리")
```

예시:
```python
RAW_DIR = Path("/Users/yein/workspace/01.유리")
```

> 👉 `01.유리` 폴더는 원본 XML 파일이 모두 들어 있는 폴더입니다.

### ▶ 실행

```bash
python select_insurance_files.py
```

### ✅ 결과

조건에 맞는 보험 XML 파일만 `data_selected/` 폴더로 복사됩니다.

---

## 3️⃣ 전체 데이터 Qdrant 적재

### 📄 실행 파일
`langchain_project/ingest/ingest_all.py`

### 📝 역할

이 스크립트는 아래 작업을 자동으로 수행합니다:
1. `data_selected/` 하위 XML 파일 로드
2. XML → 관/조 단위 전처리
3. 텍스트 Chunk 분리
4. Embedding 생성
5. Qdrant 컬렉션 생성 및 데이터 적재

### ▶ 실행

```bash
python ingest_all.py
```

### ⏳ 실행 중 출력 예시

```
Processing: 001_화재보험.xml
Processing: 002_자동차보험.xml
Embedding chunks: 124
Upserting to Qdrant...
```

---

## 4️⃣ Qdrant 적재 확인

### 🔍 Qdrant Web UI

브라우저에서 접속:
```
http://localhost:6333/dashboard
```

### 확인 포인트

- ✅ Collection 생성 여부
- ✅ Points 수가 0이 아닌지
- ✅ Vector size 정상 여부

---

## 5️⃣ 자주 발생하는 문제 & 체크리스트

### ❌ 컬렉션은 생기는데 데이터가 0개인 경우

- `data_selected/` 폴더에 파일이 실제로 존재하는지 확인
- XML 파싱 실패 로그 확인
- `vectorstore.py`에서 `add_documents()` 호출 여부 확인

### ❌ 경로 관련 에러

- `Path(__file__).resolve().parent` 기준 경로인지 확인
- 상대경로/절대경로 혼용 여부 점검

### ❌ Embedding 에러

- Upstage / HuggingFace 키 환경변수 확인
```bash
echo $UPSTAGE_API_KEY
```

---

## 📎 참고

1. **AI HUB - 약관 - 원천데이터**
   - 사용 가능한 XML 파일: 총 1,069개
   - 적재 성공: 1,072개 (잘못된 파일 3개 삭제)

2. **적재 결과**
   - 실패한 XML 파일: 49개
   - 최종 적재 완료: **총 80,161 documents**

3. **Qdrant Web UI 접속**
   - `http://localhost:6333/dashboard#/collections/insurance_docs`

---

## 6️⃣ 요약

| 단계 | 작업 | 파일 | 명령어 |
|------|------|------|--------|
| 0️⃣ | 사전 준비 | - | `poetry shell` |
| 1️⃣ | 폴더 이동 | - | `cd langchain_project/ingest` |
| 2️⃣ | 파일 선택 | `select_insurance_files.py` | `python select_insurance_files.py` |
| 3️⃣ | 데이터 적재 | `ingest_all.py` | `python ingest_all.py` |
| 4️⃣ | 적재 확인 | - | `http://localhost:6333/dashboard` |

