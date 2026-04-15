"""
최초 1회 실행하여 테이블 스키마를 벡터DB에 저장합니다.
schema_list에 실제 테이블 정보를 입력하세요.
"""
from db.vector_store import save_schemas

schema_list = [
    {
        "table_name" : "users",
        "description": "사용자 기본 정보 테이블",
        "ddl"        : """
CREATE TABLE users (
    id         INT          PRIMARY KEY,
    name       VARCHAR(50)  NOT NULL,
    email      VARCHAR(100) UNIQUE,
    created_at DATETIME     DEFAULT CURRENT_TIMESTAMP
)""",
    },
    {
        "table_name" : "orders",
        "description": "주문 내역 테이블",
        "ddl"        : """
CREATE TABLE orders (
    id         INT      PRIMARY KEY,
    user_id    INT      REFERENCES users(id),
    product    VARCHAR(100),
    amount     INT,
    ordered_at DATETIME DEFAULT CURRENT_TIMESTAMP
)""",
    },
    # 추가 테이블 계속 입력...
]

if __name__ == "__main__":
    save_schemas(schema_list)
    print("스키마 저장 완료. 이제 main.py를 실행하세요.")
