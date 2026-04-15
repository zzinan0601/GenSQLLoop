from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# 임베딩 모델 설정 (Ollama 로컬 임베딩)
embeddings = OllamaEmbeddings(
    model    = "nomic-embed-text",   # ollama pull nomic-embed-text
    base_url = "http://localhost:11434",
)

# 벡터DB 경로 (로컬 저장)
VECTOR_DB_PATH = "./chroma_schema_db"

# ── 스키마 저장 (최초 1회 실행) ────────────────────────
def save_schemas(schema_list: list[dict]):
    """
    schema_list 형식:
    [
        {
            "table_name": "users",
            "ddl": "CREATE TABLE users (id INT, name VARCHAR(50), ...)",
            "description": "사용자 정보 테이블"
        },
        ...
    ]
    """
    texts    = []
    metadatas = []

    for schema in schema_list:
        # 검색에 활용할 텍스트 (테이블명 + 설명 + DDL)
        text = f"테이블명: {schema['table_name']}\n설명: {schema['description']}\n{schema['ddl']}"
        texts.append(text)
        metadatas.append({"table_name": schema["table_name"]})

    db = Chroma.from_texts(
        texts      = texts,
        embedding  = embeddings,
        metadatas  = metadatas,
        persist_directory = VECTOR_DB_PATH,
    )
    db.persist()
    print(f"[벡터DB] {len(texts)}개 테이블 스키마 저장 완료")


# ── 스키마 조회 ────────────────────────────────────────
def retrieve_schema(question: str, top_k: int = 3) -> str:
    """
    질문과 관련된 상위 top_k개 테이블 스키마 반환
    """
    db = Chroma(
        persist_directory = VECTOR_DB_PATH,
        embedding_function = embeddings,
    )

    docs = db.similarity_search(question, k=top_k)

    if not docs:
        return "관련 스키마를 찾을 수 없습니다."

    schema_text = ""
    for doc in docs:
        schema_text += f"\n{doc.page_content}\n{'─'*40}"

    return schema_text
