from graph.state import GraphState
from llm.ollama_client import llm
from db.vector_store import retrieve_schema
from db.sql_executor import execute_query
from prompts.templates import GENERATE_PROMPT, GENERATE_IMPROVE_PROMPT

MAX_LOOP = 3


# ── 스키마 조회 노드 ───────────────────────────────────
def schema_node(state: GraphState) -> GraphState:

    question = state["question"]
    print("\n[스키마 조회] 벡터DB에서 관련 스키마 검색 중...")

    schema = retrieve_schema(question)
    print(f"[스키마 조회] 완료\n{schema}")

    return {
        **state,
        "schema"        : schema,
        "current_query" : "",
        "execute_result": "",
        "error_message" : "",
        "feedback"      : "",
        "loop_count"    : 0,
        "is_good"       : False,
    }


# ── 쿼리 생성 노드 ─────────────────────────────────────
def generate_node(state: GraphState) -> GraphState:

    question      = state["question"]
    schema        = state["schema"]
    current_query = state.get("current_query", "")
    feedback      = state.get("feedback", "")
    loop_count    = state.get("loop_count", 0)

    print(f"\n[쿼리 생성] {loop_count + 1}회차 SQL 생성 중...")

    # 첫 시도 or 재시도 프롬프트 선택
    if not current_query:
        prompt = GENERATE_PROMPT.format(
            schema   = schema,
            question = question,
        )
    else:
        prompt = GENERATE_IMPROVE_PROMPT.format(
            schema        = schema,
            question      = question,
            current_query = current_query,
            feedback      = feedback,
        )

    response = llm.invoke(prompt)

    # SQL 정리 (혹시 ```sql 블록 포함 시 제거)
    sql = response.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()

    print(f"[쿼리 생성] 생성된 SQL:\n{sql}")

    return {
        **state,
        "current_query" : sql,
        "loop_count"    : loop_count + 1,
    }


# ── 쿼리 실행 노드 ─────────────────────────────────────
def execute_node(state: GraphState) -> GraphState:

    current_query = state["current_query"]
    print(f"\n[쿼리 실행] SQL 실행 중...")

    result = execute_query(current_query)

    if not result["success"]:
        print(f"[쿼리 실행] 에러 발생: {result['error']}")
        return {
            **state,
            "execute_result": "",
            "error_message" : result["error"],
        }

    print(f"[쿼리 실행] 결과: {result['row_count']}건")
    return {
        **state,
        "execute_result": str(result["rows"]),
        "error_message" : "",
    }


# ── 판단 노드 ──────────────────────────────────────────
def judge_node(state: GraphState) -> GraphState:

    error_message  = state.get("error_message", "")
    execute_result = state.get("execute_result", "")
    loop_count     = state["loop_count"]

    # 최대 횟수 도달 → 강제 종료
    if loop_count >= MAX_LOOP:
        print(f"[판단] 최대 루프({MAX_LOOP}회) 도달 → 종료")
        return {**state, "is_good": True, "feedback": ""}

    # 에러 발생 시
    if error_message:
        feedback = f"SQL 실행 중 에러가 발생했습니다: {error_message}"
        print(f"[판단] 에러 → loop 재시도")
        return {**state, "is_good": False, "feedback": feedback}

    # 결과 0건 시
    if execute_result == "[]" or execute_result == "":
        feedback = "쿼리가 실행됐지만 결과가 0건입니다. 조건이 너무 엄격하거나 잘못된 컬럼/테이블을 참조하고 있을 수 있습니다."
        print(f"[판단] 0건 → loop 재시도")
        return {**state, "is_good": False, "feedback": feedback}

    # 정상 결과
    print(f"[판단] 정상 결과 확인 → 종료")
    return {**state, "is_good": True, "feedback": ""}


# ── 분기 함수 ──────────────────────────────────────────
def should_loop(state: GraphState) -> str:
    if state["is_good"]:
        return "end"
    return "generate"   # 쿼리 생성 노드로 되돌아감
