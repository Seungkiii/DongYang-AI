from typing import List, Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from ..core.config import get_settings

settings = get_settings()

SYSTEM_TEMPLATE = """당신은 동양생명 보험 상담 전문가입니다.
주어진 보험 약관 내용을 바탕으로 사용자의 질문에 정확하고 친절하게 답변해주세요.

답변 시 다음 가이드라인을 따라주세요:
1. 약관에 명시된 내용만을 기반으로 답변하세요.
2. 확실하지 않은 내용은 "약관에서 해당 내용을 찾을 수 없습니다"라고 답변하세요.
3. 답변은 친절하고 이해하기 쉽게 작성하세요.
4. 중요한 조건이나 예외사항이 있다면 반드시 언급해주세요.

관련 약관 내용:
{context}

사용자 질문: {question}"""

class ChatEngine:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name=settings.gpt_model,
            temperature=0,
            api_key=settings.openai_api_key
        )
        
        self.prompt = ChatPromptTemplate.from_template(SYSTEM_TEMPLATE)
    
    def generate_answer(self, question: str, context_docs: List[Document]) -> Dict[str, Any]:
        """컨텍스트를 기반으로 질문에 대한 답변을 생성합니다."""
        context = "\n\n".join([doc.page_content for doc in context_docs])
        
        messages = self.prompt.format_messages(
            context=context,
            question=question
        )
        
        response = self.llm.invoke(messages)
        
        return {
            "answer": response.content,
            "contexts": [doc.page_content for doc in context_docs],
            "confidence": 0.8  # TODO: 실제 신뢰도 계산 구현
        } 