from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import time
from ..core.chat_engine import ChatEngine
from ..core.vector_store import VectorStore
from ..core.config import get_settings

settings = get_settings()

router = APIRouter(prefix="/chat")

class QuestionRequest(BaseModel):
    question: str
    context_count: int = 5

class ChatResponse(BaseModel):
    answer: str
    contexts: List[str]
    confidence: float
    processing_time: int

# 싱글톤 인스턴스
chat_engine = ChatEngine()
vector_store = VectorStore(
    openai_api_key=settings.openai_api_key,
    collection_name="insurance_docs"
)

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
        
        # 처리 시간 계산 (밀리초)
        processing_time = int((time.time() - start_time) * 1000)
        
        # 신뢰도 계산 개선 (컨텍스트 유사도 기반)
        confidence = calculate_confidence(context_docs, request.question)
        
        return ChatResponse(
            answer=response["answer"],
            contexts=response["contexts"],
            confidence=confidence,
            processing_time=processing_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )

def calculate_confidence(context_docs: List, question: str) -> float:
    """컨텍스트 유사도 기반 신뢰도 계산"""
    if not context_docs:
        return 0.3  # 컨텍스트가 없으면 낮은 신뢰도
    
    # 컨텍스트 개수에 따른 기본 신뢰도
    base_confidence = min(0.8, 0.3 + len(context_docs) * 0.1)
    
    # 질문 길이에 따른 조정
    question_length_factor = min(1.0, len(question) / 50)
    
    # 최종 신뢰도 계산
    confidence = base_confidence * question_length_factor
    
    return round(confidence, 2) 