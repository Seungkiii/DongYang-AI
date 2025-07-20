from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import time
import json
from app.core.chat_engine import ChatEngine
from app.core.vector_store import VectorStore
from app.core.config import get_settings
from app.core.insurance_comparison import InsuranceComparisonService
from app.core.insurance_recommendation import InsuranceRecommendationService
from app.prompt_templates import INTENT_EXTRACTION_PROMPT
import re

settings = get_settings()

router = APIRouter(prefix="/chat")

class QuestionRequest(BaseModel):
    question: str
    context_count: int = 5

class ChatResponse(BaseModel):
    answer: Optional[str] = None
    contexts: List[str] = []
    confidence: float = 0.0
    processing_time: int = 0
    intent: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('parameters', pre=True, always=True)
    def validate_parameters(cls, v):
        print(f"=== [Pydantic] Parameters 검증 ===")
        print(f"Input type: {type(v)}")
        print(f"Input value: {repr(v)}")
        import json
        if v is None:
            print("Parameters가 None -> 빈 dict 반환")
            return {}
        if isinstance(v, str):
            print("Parameters가 문자열 -> JSON 파싱 시도")
            try:
                v = json.loads(v)
                print(f"파싱 성공: {v}")
            except:
                print("파싱 실패 -> 빈 dict 반환")
                return {}
        if not isinstance(v, dict):
            print(f"Parameters가 dict가 아님 ({type(v)}) -> 빈 dict 반환")
            return {}
        # 키 정제 (따옴표 제거)
        cleaned_params = {}
        for key, value in v.items():
            clean_key = str(key).strip('"').strip("'")
            if clean_key != key:
                print(f"키 정제: {repr(key)} -> {repr(clean_key)}")
            cleaned_params[clean_key] = value
        print(f"최종 parameters: {cleaned_params}")
        return cleaned_params

# 싱글톤 인스턴스
vector_store = VectorStore(
    openai_api_key=settings.openai_api_key,
    collection_name="insurance_docs"
)
chat_engine = ChatEngine(vector_store=vector_store)
comparison_service = InsuranceComparisonService(vector_store)
recommendation_service = InsuranceRecommendationService(vector_store)

def extract_intent_and_parameters(question: str) -> tuple[str, Dict[str, Any]]:
    """질문에서 의도와 매개변수를 추출합니다."""
    try:
        question_lower = question.lower()
        
        # 보험 추천 의도 감지
        recommendation_keywords = ["추천", "어떤", "적합한", "맞는", "좋은", "괜찮은"]
        if any(keyword in question_lower for keyword in recommendation_keywords):
            # 나이 정보가 있는지 확인
            age_patterns = [r'(\d+)대', r'(\d+)세', r'나이\s*(\d+)', r'(\d+)살']
            has_age_info = any(re.search(pattern, question_lower) for pattern in age_patterns)
            
            # 목적 정보가 있는지 확인
            purpose_keywords = ["사망보장", "질병보장", "의료비보장", "노후대비", "기간보장"]
            has_purpose_info = any(keyword in question_lower for keyword in purpose_keywords)
            
            if has_age_info or has_purpose_info:
                return "insurance_recommendation", {}
        
        # 보험 비교 의도 감지
        comparison_keywords = ["비교", "차이", "어떤게", "어떤 것이", "vs", "versus"]
        if any(keyword in question_lower for keyword in comparison_keywords):
            # 보험명 추출
            insurance_names = comparison_service.extract_insurance_names(question)
            if len(insurance_names) >= 2:
                return "insurance_comparison", {"insurance_names": insurance_names}
        
        # 일반 채팅으로 처리
        return "general_chat", {}
        
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"의도 추출 실패: {e}")
        return "general_chat", {}

@router.post("/question", response_model=ChatResponse)
async def process_question(request: QuestionRequest):
    start_time = time.time()
    
    try:
        # 입력 검증
        if not request.question or request.question.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="질문이 비어 있습니다."
            )
        
        if request.context_count < 1 or request.context_count > 10:
            raise HTTPException(
                status_code=400,
                detail="context_count는 1-10 사이의 값이어야 합니다."
            )
        
        # 1. 의도 및 매개변수 추출
        intent, parameters = extract_intent_and_parameters(request.question)
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[AI서버] 의도 추출 결과: intent={intent}, parameters={parameters}")

        # 2. 의도에 따른 응답 생성
        answer = None
        contexts = []
        confidence = 0.0

        if intent == "insurance_recommendation":
            # 보험 추천 처리
            response = chat_engine.generate_recommendation_answer(request.question)
            answer = response["answer"]
            contexts = response["contexts"]
            confidence = response["confidence"]

        elif intent == "insurance_comparison":
            # 보험 비교 처리
            insurance_names = parameters.get("insurance_names", [])
            if len(insurance_names) >= 2:
                response = chat_engine.generate_comparison_answer(
                    question=request.question,
                    insurance_names=insurance_names
                )
                answer = response["answer"]
                contexts = response["contexts"]
                confidence = response["confidence"]
            else:
                answer = "비교할 보험 상품을 2개 이상 명시해주세요."
                confidence = 0.0

        elif intent == "general_chat":
            # 유사한 컨텍스트 검색
            context_docs = vector_store.similarity_search(
                query=request.question,
                k=request.context_count
            )
            
            # GPT 응답 생성
            response = chat_engine.generate_answer(
                question=request.question,
                context_docs=context_docs
            )
            answer = response["answer"]
            contexts = response["contexts"]
            confidence = response["confidence"]

            # 신뢰도 임계값 적용 (환경변수/설정에서 불러오거나 기본값 0.5)
            threshold = getattr(settings, "confidence_threshold", 0.5)
            if confidence < threshold:
                answer = "죄송합니다. 명확한 답변을 드릴 수 없습니다. 질문을 다시 한번 구체적으로 입력해 주세요."

        else:
            # 기타 의도는 일반 채팅으로 처리
            answer = "죄송합니다. 해당 기능은 아직 지원되지 않습니다."
            confidence = 0.0

        # 처리 시간 계산 (밀리초)
        processing_time = int((time.time() - start_time) * 1000)
        
        # parameters가 dict가 아니면 빈 dict로 강제 변환
        if not isinstance(parameters, dict):
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[AI서버] parameters 타입 불일치: {type(parameters)}, 값: {parameters}")
            parameters = {}
        return ChatResponse(
            answer=answer,
            contexts=contexts,
            confidence=confidence,
            processing_time=processing_time,
            intent=intent,
            parameters=parameters
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )

# (이전 calculate_confidence 함수는 더 이상 사용하지 않음)
    
    return round(confidence, 2) 