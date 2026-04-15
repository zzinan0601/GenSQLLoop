from graph.graph import build_graph

def main():
    graph = build_graph()

    question = input("데이터 요청을 입력하세요: ")

    initial_state = {
        "question"      : question,
        "schema"        : "",
        "current_query" : "",
        "execute_result": "",
        "error_message" : "",
        "feedback"      : "",
        "loop_count"    : 0,
        "is_good"       : False,
    }

    print("\n" + "="*50)

    current_node = None

    for token, metadata in graph.stream(initial_state, stream_mode="messages"):

        node = metadata.get("langgraph_node")

        # 쿼리 생성 노드만 토큰 실시간 출력
        if node != current_node:
            current_node = node
            if node == "generate":
                print(f"\n[SQL 생성 중...]\n")

        if node == "generate":
            print(token.content, end="", flush=True)

    print("\n" + "="*50)
    print("\n✅ 완료")


if __name__ == "__main__":
    main()
