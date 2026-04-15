from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.nodes import schema_node, generate_node, execute_node, judge_node, should_loop


def build_graph():

    builder = StateGraph(GraphState)

    # 노드 등록
    builder.add_node("schema",   schema_node)
    builder.add_node("generate", generate_node)
    builder.add_node("execute",  execute_node)
    builder.add_node("judge",    judge_node)

    # 시작점
    builder.set_entry_point("schema")

    # 고정 엣지
    builder.add_edge("schema",   "generate")  # 스키마 조회 → 쿼리 생성
    builder.add_edge("generate", "execute")   # 쿼리 생성 → 실행
    builder.add_edge("execute",  "judge")     # 실행 → 판단

    # 분기: 판단 후 → 재생성 or 종료
    builder.add_conditional_edges(
        "judge",
        should_loop,
        {
            "generate" : "generate",  # 에러/0건 → 쿼리 재생성
            "end"      : END,         # 정상     → 종료
        }
    )

    return builder.compile()
