from typing import TypedDict

class GraphState(TypedDict):
    question       : str   # 사용자 질문 (어떤 데이터를 원하는가)
    schema         : str   # 벡터DB에서 조회한 관련 스키마
    current_query  : str   # 현재 생성된 SQL 쿼리
    execute_result : str   # 쿼리 실행 결과 (문자열)
    error_message  : str   # 실행 중 에러 메시지
    feedback       : str   # 판단 후 다음 loop에 전달할 피드백
    loop_count     : int   # 현재 루프 횟수
    is_good        : bool  # 판단 결과
