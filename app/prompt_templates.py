from langchain.prompts import PromptTemplate

ANSWER_PROMPT = PromptTemplate(
    template="""아래는 보험 약관에서 추출한 관련 내용입니다:

{context}

위 내용을 바탕으로 다음 질문에 답변해주세요: {question}

답변 시 다음 가이드라인을 따라주세요:
1. 정확한 정보만을 제공하세요.
2. 약관의 내용을 기반으로 명확하게 설명하세요.
3. 확실하지 않은 내용은 "약관에서 해당 내용을 찾을 수 없습니다"라고 답변하세요.
4. 답변은 친절하고 이해하기 쉽게 작성하세요.

답변:""",
    input_variables=["context", "question"]
)

CONDENSE_QUESTION_PROMPT = PromptTemplate(
    template="""주어진 대화 기록과 새로운 질문을 바탕으로, 새로운 질문을 독립적인 질문으로 재작성해주세요.

대화 기록: {chat_history}
새로운 질문: {question}

독립적인 질문:""",
    input_variables=["chat_history", "question"]
) 