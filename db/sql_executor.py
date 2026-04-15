import sqlalchemy
from sqlalchemy import text

# ── DB 연결 설정 ───────────────────────────────────────
# 사용하는 DB에 맞게 connection_string 변경하세요
#
# SQLite  : "sqlite:///./mydb.db"
# MSSQL   : "mssql+pyodbc://user:pw@server/db?driver=ODBC+Driver+17+for+SQL+Server"
# MySQL   : "mysql+pymysql://user:pw@host:3306/db"
# Oracle  : "oracle+cx_oracle://user:pw@host:1521/sid"
# PostgreSQL : "postgresql+psycopg2://user:pw@host:5432/db"

CONNECTION_STRING = "sqlite:///./mydb.db"

engine = sqlalchemy.create_engine(CONNECTION_STRING)


# ── SQL 실행 ───────────────────────────────────────────
def execute_query(sql: str) -> dict:
    """
    SQL 실행 후 결과 반환

    반환 형식:
    {
        "success"  : True/False,
        "rows"     : [ {col: val, ...}, ... ],  # 성공 시
        "row_count": 0,
        "error"    : "에러메시지"                # 실패 시
    }
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows   = [dict(row._mapping) for row in result]

            return {
                "success"  : True,
                "rows"     : rows,
                "row_count": len(rows),
                "error"    : "",
            }

    except Exception as e:
        return {
            "success"  : False,
            "rows"     : [],
            "row_count": 0,
            "error"    : str(e),
        }