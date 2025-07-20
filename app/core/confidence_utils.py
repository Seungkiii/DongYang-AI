import numpy as np
import re
from typing import List
from langchain_openai import OpenAIEmbeddings
from core.config import get_settings

settings = get_settings()

EMBED_MODEL = settings.openai_embedding_model
OPENAI_API_KEY = settings.openai_api_key

# 불확실/모호한 답변 패턴
UNCERTAIN_PATTERNS = [
    r"\b아마도\b", r"\b가능\b", r"\b일 수 있습니다\b", r"\b모르겠습니다\b", r"\b생각합니다\b",
    r"\b추정됩니다\b", r"\b정확하지 않습니다\b", r"\b확실하지 않습니다\b"
]

uncertain_regex = re.compile("|".join(UNCERTAIN_PATTERNS))

embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model=EMBED_MODEL)

def cosine_similarity(vec1, vec2):
    if not vec1 or not vec2:
        return 0.0
    try:
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(np.dot(v1, v2) / (norm1 * norm2))
    except Exception:
        return 0.0


def calculate_confidence_score(question: str, answer: str, context_docs: List[str],
                               context_count: int = 5) -> float:
    """
    질문, 답변, 컨텍스트 문서 기반 신뢰도(0~1) 계산
    - 컨텍스트 유사도: 질문-문서 임베딩 코사인 유사도 평균
    - 답변 불확실성: 불확실/모호 패턴 감지 시 감점
    - 답변 길이: 길수록 가점
    - 컨텍스트 개수, 키워드 중첩 등 추가 반영
    """
    # 컨텍스트 유사도
    if not context_docs:
        context_sim = 0.0
    else:
        q_emb = embeddings.embed_query(question)
        ctx_embs = embeddings.embed_documents(context_docs)
        sims = [cosine_similarity(q_emb, ctx) for ctx in ctx_embs]
        context_sim = float(np.mean(sims))

    # 불확실/모호 패턴 감지
    uncertain_penalty = 0.0
    if uncertain_regex.search(answer):
        uncertain_penalty = 0.2

    # 답변 길이 가중치 (100자 이상이면 가점)
    length_bonus = min(len(answer) / 300, 1.0) * 0.15

    # 컨텍스트 개수 가중치
    context_bonus = min(len(context_docs) / context_count, 1.0) * 0.1

    # 질문과 답변 키워드 중첩률
    q_keywords = set(re.findall(r"[\w가-힣]+", question))
    a_keywords = set(re.findall(r"[\w가-힣]+", answer))
    overlap = len(q_keywords & a_keywords) / (len(q_keywords) + 1e-8)
    overlap_bonus = min(overlap, 1.0) * 0.1

    # 최종 score
    score = context_sim * 0.6 + length_bonus + context_bonus + overlap_bonus - uncertain_penalty
    score = max(0.0, min(1.0, score))
    return round(score, 3)
