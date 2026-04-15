# local-llm-sql

로컬 LLM(Ollama)으로 자연어 요청을 SQL 쿼리로 변환하고,
실행 결과가 에러이거나 0건이면 피드백을 반영해 자동으로 재작성하는 프로젝트

---

## 📁 프로젝트 구조

```
local-llm-sql/
│
├── main.py                  # 실행 진입점
├── init_schema.py           # 스키마 벡터DB 저장 (최초 1회)
├── requirements.txt
│
├── graph/
│   ├── state.py             # 상태 정의
│   ├── nodes.py             # 스키마조회 / 쿼리생성 / 실행 / 판단 노드
│   └── graph.py             # 그래프 조립
│
├── llm/
│   └── ollama_client.py     # Ollama LLM 연결
│
├── db/
│   ├── vector_store.py      # ChromaDB 스키마 저장/조회
│   └── sql_executor.py      # SQL 실행 (SQLAlchemy)
│
└── prompts/
    └── templates.py         # 프롬프트 템플릿
```

---

## ⚙️ 실행 흐름

```
질문 입력
    ↓
[스키마 조회]  벡터DB에서 질문과 관련된 테이블 스키마 검색
    ↓
[쿼리 생성]   스키마 + 피드백 참고하여 SQL 작성
    ↓
[쿼리 실행]   SQL 실행
    ↓
[판단]        에러 or 결과 0건?
    ├─ YES → 피드백 담아서 쿼리 생성으로 (최대 3회)
    └─ NO  → 최종 결과 출력
```

---

## 🔄 판단 기준

| 상황 | 피드백 내용 | 동작 |
|------|------------|------|
| SQL 에러 발생 | 에러 메시지 전달 | 쿼리 재생성 |
| 결과 0건 | 조건 완화 요청 | 쿼리 재생성 |
| 정상 결과 | - | 종료 |
| 3회 도달 | - | 강제 종료 |

---

## 🛠️ 사전 준비

### 1. Ollama 모델 준비
```bash
ollama pull qwen2.5:7b          # LLM (SQL 생성용)
ollama pull nomic-embed-text    # 임베딩 (스키마 검색용)
```

### 2. DB 연결 설정
`db/sql_executor.py` 에서 CONNECTION_STRING 수정
```python
# SQLite
CONNECTION_STRING = "sqlite:///./mydb.db"

# MSSQL
CONNECTION_STRING = "mssql+pyodbc://user:pw@server/db?driver=ODBC+Driver+17+for+SQL+Server"

# MySQL
CONNECTION_STRING = "mysql+pymysql://user:pw@host:3306/db"
```

### 3. 스키마 벡터DB 저장 (최초 1회)
`init_schema.py` 에 테이블 정보 입력 후 실행
```bash
python init_schema.py
```

---

## 📦 패키지 설치

```bash
pip install -r requirements.txt
```

### 폐쇄망 오프라인 설치
```bash
# 외부망에서 다운로드
pip download -r requirements.txt -d ./wheelhouse

# 내부망에서 설치
pip install --no-index --find-links=./wheelhouse -r requirements.txt
```

---

## ▶️ 실행

```bash
python main.py
```

---

## 💡 실행 예시

```
데이터 요청을 입력하세요: 최근 7일간 주문이 있는 사용자 목록 조회

==================================================

[스키마 조회] 벡터DB에서 관련 스키마 검색 중...
[스키마 조회] 완료 (users, orders 테이블)

[SQL 생성 중...]
SELECT u.id, u.name, u.email
FROM users u
WHERE u.id IN (
    SELECT DISTINCT user_id FROM orders
    WHERE ordered_at >= DATEADD(day, -7, GETDATE())
)

[쿼리 실행] SQL 실행 중...
[쿼리 실행] 결과: 0건

[판단] 0건 → loop 재시도

[SQL 생성 중...]
SELECT u.id, u.name, u.email
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.ordered_at >= date('now', '-7 days')

[쿼리 실행] 결과: 5건
[판단] 정상 결과 확인 → 종료

==================================================
✅ 완료
```

---

## 🔧 설정 변경

| 항목 | 파일 | 변수 |
|------|------|------|
| LLM 모델 변경 | `llm/ollama_client.py` | `model` |
| 임베딩 모델 변경 | `db/vector_store.py` | `model` |
| DB 연결 변경 | `db/sql_executor.py` | `CONNECTION_STRING` |
| 최대 루프 횟수 | `graph/nodes.py` | `MAX_LOOP` |
| 스키마 검색 개수 | `db/vector_store.py` | `top_k` |

---

## 📋 개발 환경

- OS : Windows
- IDE : VS Code
- Python : 3.10 이상 권장
- 네트워크 : 폐쇄망 (오프라인)
