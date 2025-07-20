from langchain.prompts import PromptTemplate

# --- 보험 도메인 FAQ/가이드라인 ---
INSURANCE_FAQ = """
Q: 암 보험은 어떤 보장을 하나요?
A: 암 보험은 암 진단 시 진단비, 입원비, 수술비 등을 보장합니다.

Q: 실손 보험과 종신 보험의 차이점은?
A: 실손 보험은 실제 발생한 의료비를 보장하고, 종신 보험은 사망 시 보험금을 지급합니다.

Q: 보험 가입 후 바로 보장이 되나요?
A: 대부분의 보험은 면책기간(예: 90일) 후 보장이 시작됩니다.
"""

FORBIDDEN_ANSWER_GUIDE = """
- 약관에 없는 내용, 확실하지 않은 정보는 제공하지 마세요.
- 투자, 세금, 법률, 미래 예측, 특정 상품 추천 등은 하지 마세요.
- 허위/과장/불확실/위험한 조언은 금지.
"""

REQUIRED_ANSWER_GUIDE = """
1. 정확한 정보만을 제공하세요.
2. 약관의 내용을 기반으로 명확하게 설명하세요.
3. 확실하지 않은 내용은 "약관에서 해당 내용을 찾을 수 없습니다"라고 답변하세요.
4. 답변은 친절하고 이해하기 쉽게 작성하세요.
"""



CONDENSE_QUESTION_PROMPT = PromptTemplate(
    template="""주어진 대화 기록과 새로운 질문을 바탕으로, 새로운 질문을 독립적인 질문으로 재작성해주세요.

대화 기록: {chat_history}
새로운 질문: {question}

독립적인 질문:""",
    input_variables=["chat_history", "question"]
)

INTENT_EXTRACTION_PROMPT = PromptTemplate(
    template="""사용자의 질문을 분석하여 의도(intent)와 필요한 매개변수(parameters)를 JSON 형식으로 추출하세요.

의도는 다음 중 하나입니다: "insurance_info", "insurance_comparison", "insurance_recommendation", "general_chat".

매개변수는 의도에 따라 다음과 같습니다:
- insurance_info: {"insurance_name": "[보험 상품명]"}
- insurance_comparison: {"insurance_names": ["[보험 상품명1]", "[보험 상품명2]", ...]}
- insurance_recommendation: {"age": [나이], "purpose": "[보험 가입 목적]", "coverage_type": "[원하는 보장 유형]"}
- general_chat: {}

예시:
질문: 암 보험에 대해 알려줘
응답: {"intent": "insurance_info", "parameters": {"insurance_name": "암 보험"}}

질문: 종신 보험이랑 정기 보험 비교해줘
응답: {"intent": "insurance_comparison", "parameters": {"insurance_names": ["종신 보험", "정기 보험"]}}

질문: 30대 직장인인데 노후 대비 보험 추천해줘
응답: {"intent": "insurance_recommendation", "parameters": {"age": 30, "purpose": "노후 대비", "coverage_type": "종합"}}

질문: 안녕하세요
응답: {"intent": "general_chat", "parameters": {}}

질문: {question}
응답:""",
    input_variables=["question"]
) 