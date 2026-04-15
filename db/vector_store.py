from langchain_community.embeddings import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 임베딩 모델 설정 (Ollama 로컬 임베딩)
embeddings = OllamaEmbeddings(
    model    = "nomic-embed-text",   # ollama pull nomic-embed-text
    base_url = "http://localhost:11434",
)

# Qdrant 설정
QDRANT_HOST       = "localhost"
QDRANT_PORT       = 6333
COLLECTION_NAME   = "schema_store"
EMBEDDING_DIM     = 768   # nomic-embed-text 기본 차원


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
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # 컬렉션 없으면 생성
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name = COLLECTION_NAME,
            vectors_config  = VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )
        print(f"[벡터DB] 컬렉션 '{COLLECTION_NAME}' 생성")

    texts     = []
    metadatas = []

    for schema in schema_list:
        text = f"테이블명: {schema['table_name']}\n설명: {schema['description']}\n{schema['ddl']}"
        texts.append(text)
        metadatas.append({"table_name": schema["table_name"]})

    QdrantVectorStore.from_texts(
        texts           = texts,
        embedding       = embeddings,
        metadatas       = metadatas,
        url             = f"http://{QDRANT_HOST}:{QDRANT_PORT}",
        collection_name = COLLECTION_NAME,
    )
    print(f"[벡터DB] {len(texts)}개 테이블 스키마 저장 완료")


# ── 스키마 조회 ────────────────────────────────────────
def retrieve_schema(question: str, top_k: int = 3) -> str:
    """
    질문과 관련된 상위 top_k개 테이블 스키마 반환
    """
    db = QdrantVectorStore.from_existing_collection(
        embedding       = embeddings,
        url             = f"http://{QDRANT_HOST}:{QDRANT_PORT}",
        collection_name = COLLECTION_NAME,
    )

    docs = db.similarity_search(question, k=top_k)

    if not docs:
        return "관련 스키마를 찾을 수 없습니다."

    schema_text = ""
    for doc in docs:
        schema_text += f"\n{doc.page_content}\n{'─'*40}"

    return schema_text
