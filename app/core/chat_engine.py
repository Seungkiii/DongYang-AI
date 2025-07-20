from typing import List, Dict, Any
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from langchain_openai import ChatOpenAI
from app.core.config import get_settings
from app.core.insurance_comparison import InsuranceComparisonService
from app.core.insurance_recommendation import InsuranceRecommendationService

settings = get_settings()

SYSTEM_TEMPLATE = """당신은 동양생명 보험 상담 전문가입니다.
주어진 보험 상품 정보와 약관 내용을 바탕으로 사용자의 질문에 전문적이고 상세하게 답변해주세요.

답변 시 다음 가이드라인을 따라주세요:
1. 제공된 보험 상품 정보를 최대한 활용하여 구체적으로 답변하세요.
2. 보험의 특징, 보장 내용, 가입 조건, 보험료 등을 상세히 설명하세요.
3. 사용자가 이해하기 쉽도록 친절하고 명확하게 설명하세요.
4. 여러 보험 상품이 관련된 경우, 각각의 특징을 비교하여 설명하세요.
5. 중요한 조건, 제한사항, 예외사항이 있다면 반드시 언급하세요.
6. 구체적인 정보가 부족한 경우에만 "해당 정보는 상품 설명서를 참고해 주세요"라고 안내하세요.

보험 상품 정보 및 약관 내용:
{context}

사용자 질문: {question}

답변을 작성할 때는 다음 형식을 참고하세요:
- 질문하신 보험에 대한 주요 특징
- 보장 내용 및 범위
- 가입 조건 및 제한사항
- 기타 중요 정보"""

COMPARISON_TEMPLATE = """당신은 동양생명 보험 상담 전문가입니다.
주어진 보험 상품 정보를 바탕으로 객관적이고 정확한 비교 분석을 제공해주세요.

비교 분석 시 다음 가이드라인을 따라주세요:
1. 각 보험의 주요 특징을 명확히 구분하여 설명하세요.
2. 보장 범위, 가입 조건, 보험료 등을 구체적으로 비교하세요.
3. 각 보험의 장단점을 객관적으로 분석하세요.
4. 고객의 상황에 따른 추천을 제공하세요.
5. 확실하지 않은 내용은 "해당 정보를 찾을 수 없습니다"라고 명시하세요.

비교할 보험 상품 정보:
{comparison_data}

사용자 질문: {question}"""

RECOMMENDATION_TEMPLATE = """당신은 동양생명 보험 상담 전문가입니다.
사용자의 정보와 요구사항을 바탕으로 가장 적합한 보험 상품을 추천해주세요.

추천 시 다음 가이드라인을 따라주세요:
1. 사용자의 나이, 목적, 보장 유형을 고려하여 추천하세요.
2. 각 보험의 특징과 장점을 명확히 설명하세요.
3. 왜 해당 보험이 적합한지 구체적인 이유를 제시하세요.
4. 가입 시 고려해야 할 사항들을 안내하세요.
5. 확실하지 않은 내용은 "해당 정보를 찾을 수 없습니다"라고 명시하세요.

추천 데이터:
{recommendation_data}

사용자 질문: {question}"""

class ChatEngine:
    def __init__(self, vector_store=None):
        self.llm = ChatOpenAI(
            model_name=settings.gpt_model,
            temperature=0,
            api_key=settings.openai_api_key
        )
        
        self.prompt = ChatPromptTemplate.from_template(SYSTEM_TEMPLATE)
        self.comparison_prompt = ChatPromptTemplate.from_template(COMPARISON_TEMPLATE)
        self.recommendation_prompt = ChatPromptTemplate.from_template(RECOMMENDATION_TEMPLATE)
        
        # 보험 비교 및 추천 서비스 초기화
        if vector_store:
            self.comparison_service = InsuranceComparisonService(vector_store)
            self.recommendation_service = InsuranceRecommendationService(vector_store)
        else:
            self.comparison_service = None
            self.recommendation_service = None
    
    def generate_answer(self, question: str, context_docs: List[Document]) -> Dict[str, Any]:
        """컨텍스트를 기반으로 질문에 대한 답변을 생성합니다."""
        context = "\n\n".join([doc.page_content for doc in context_docs])
        
        messages = self.prompt.format_messages(
            context=context,
            question=question
        )
        
        response = self.llm.invoke(messages)
        answer = response.content
        context_texts = [doc.page_content for doc in context_docs]

        # 신뢰도 계산 (안전한 방법)
        try:
            from app.core.confidence_utils import calculate_confidence_score
            confidence = calculate_confidence_score(
                question=question,
                answer=answer,
                context_docs=context_texts,
                context_count=len(context_docs)
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[신뢰도 계산 실패] {e}, 기본값 0.7 사용")
            confidence = 0.7  # 기본 신뢰도
        
        import logging
        logging.getLogger(__name__).info(f"[신뢰도] Q: {question} / Score: {confidence}")

        return {
            "answer": answer,
            "contexts": context_texts,
            "confidence": confidence
        }
    
    def generate_comparison_answer(self, question: str, insurance_names: List[str]) -> Dict[str, Any]:
        """보험 비교 답변을 생성합니다."""
        if not self.comparison_service:
            return {
                "answer": "보험 비교 서비스를 사용할 수 없습니다.",
                "contexts": [],
                "confidence": 0.0
            }
        
        try:
            # 보험 비교 데이터 생성
            comparison_result = self.comparison_service.compare_insurances(insurance_names)
            
            if "error" in comparison_result:
                return {
                    "answer": comparison_result["error"],
                    "contexts": [],
                    "confidence": 0.0
                }
            
            # 비교 프롬프트 생성
            comparison_data = comparison_result["comparison_prompt"]
            
            messages = self.comparison_prompt.format_messages(
                comparison_data=comparison_data,
                question=question
            )
            
            response = self.llm.invoke(messages)
            answer = response.content
            
            # 컨텍스트 정보 수집
            contexts = []
            for info in comparison_result["insurance_infos"]:
                contexts.append(f"{info['name']}: {info['content'][:200]}...")
            
            return {
                "answer": answer,
                "contexts": contexts,
                "confidence": 0.9,  # 비교 분석은 높은 신뢰도
                "comparison_data": comparison_result
            }
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"보험 비교 답변 생성 실패: {e}")
            return {
                "answer": f"보험 비교 중 오류가 발생했습니다: {str(e)}",
                "contexts": [],
                "confidence": 0.0
            }
    
    def generate_recommendation_answer(self, question: str) -> Dict[str, Any]:
        """보험 추천 답변을 생성합니다."""
        if not self.recommendation_service:
            return {
                "answer": "보험 추천 서비스를 사용할 수 없습니다.",
                "contexts": [],
                "confidence": 0.0
            }
        
        try:
            # 보험 추천 데이터 생성
            recommendation_result = self.recommendation_service.recommend_insurances(question)
            
            if not recommendation_result["recommendations"]:
                return {
                    "answer": "추천할 수 있는 보험 상품을 찾을 수 없습니다. 더 구체적인 정보를 제공해주세요.",
                    "contexts": [],
                    "confidence": 0.0
                }
            
            # 추천 프롬프트 생성
            recommendation_data = self.recommendation_service.create_recommendation_prompt(recommendation_result)
            
            messages = self.recommendation_prompt.format_messages(
                recommendation_data=recommendation_data,
                question=question
            )
            
            response = self.llm.invoke(messages)
            answer = response.content
            
            # 컨텍스트 정보 수집
            contexts = []
            for rec in recommendation_result["recommendations"]:
                contexts.append(f"{rec['insurance_name']} (점수: {rec['score']}): {rec['content'][:200]}...")
            
            return {
                "answer": answer,
                "contexts": contexts,
                "confidence": 0.9,  # 추천 분석은 높은 신뢰도
                "recommendation_data": recommendation_result
            }
            
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"보험 추천 답변 생성 실패: {e}")
            return {
                "answer": f"보험 추천 중 오류가 발생했습니다: {str(e)}",
                "contexts": [],
                "confidence": 0.0
            }