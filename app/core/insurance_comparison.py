from typing import List, Dict, Any
from langchain.schema import Document
from app.core.vector_store import VectorStore
from app.core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

class InsuranceComparisonService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        
        # 보험 상품별 키워드 매핑
        self.insurance_keywords = {
            "종신보험": ["종신", "사망", "보험금", "납입", "만기"],
            "정기보험": ["정기", "기간", "사망", "보험금", "만기"],
            "암보험": ["암", "진단", "입원", "수술", "치료"],
            "실손보험": ["실손", "의료비", "실제", "보장", "치료"],
            "유니버셜보험": ["유니버셜", "투자", "적립", "보험료", "만기"],
            "알뜰플러스": ["알뜰", "플러스", "종신", "납입", "보장"]
        }
    
    def extract_insurance_names(self, question: str) -> List[str]:
        """질문에서 보험 상품명을 추출합니다."""
        extracted_names = []
        question_lower = question.lower()
        
        for insurance_name, keywords in self.insurance_keywords.items():
            # 보험명이 직접 언급된 경우
            if insurance_name.lower() in question_lower:
                extracted_names.append(insurance_name)
            # 키워드가 언급된 경우
            elif any(keyword in question_lower for keyword in keywords):
                extracted_names.append(insurance_name)
        
        # 중복 제거
        return list(set(extracted_names))
    
    def get_insurance_info(self, insurance_name: str) -> Dict[str, Any]:
        """특정 보험 상품의 정보를 검색합니다."""
        try:
            # 보험명으로 검색
            docs = self.vector_store.similarity_search(
                query=insurance_name,
                k=3
            )
            
            # 관련 키워드로 추가 검색
            if insurance_name in self.insurance_keywords:
                for keyword in self.insurance_keywords[insurance_name]:
                    additional_docs = self.vector_store.similarity_search(
                        query=keyword,
                        k=2
                    )
                    docs.extend(additional_docs)
            
            # 중복 제거
            unique_docs = []
            seen_content = set()
            for doc in docs:
                if doc.page_content not in seen_content:
                    unique_docs.append(doc)
                    seen_content.add(doc.page_content)
            
            # 정보 추출
            content = "\n\n".join([doc.page_content for doc in unique_docs[:5]])
            
            return {
                "name": insurance_name,
                "content": content,
                "documents": len(unique_docs)
            }
            
        except Exception as e:
            logger.error(f"보험 정보 검색 실패: {insurance_name}, 오류: {e}")
            return {
                "name": insurance_name,
                "content": f"{insurance_name}에 대한 정보를 찾을 수 없습니다.",
                "documents": 0
            }
    
    def compare_insurances(self, insurance_names: List[str]) -> Dict[str, Any]:
        """여러 보험 상품을 비교합니다."""
        if len(insurance_names) < 2:
            return {
                "error": "비교하려면 최소 2개의 보험 상품이 필요합니다."
            }
        
        # 각 보험의 정보 수집
        insurance_infos = []
        for name in insurance_names:
            info = self.get_insurance_info(name)
            insurance_infos.append(info)
        
        # 비교 분석을 위한 프롬프트 생성
        comparison_prompt = self._create_comparison_prompt(insurance_infos)
        
        return {
            "insurance_names": insurance_names,
            "insurance_infos": insurance_infos,
            "comparison_prompt": comparison_prompt
        }
    
    def _create_comparison_prompt(self, insurance_infos: List[Dict[str, Any]]) -> str:
        """비교 분석을 위한 프롬프트를 생성합니다."""
        prompt = "다음 보험 상품들을 비교 분석해주세요:\n\n"
        
        for i, info in enumerate(insurance_infos, 1):
            prompt += f"=== {i}. {info['name']} ===\n"
            prompt += f"문서 수: {info['documents']}개\n"
            prompt += f"내용:\n{info['content'][:500]}...\n\n"
        
        prompt += """
다음 형식으로 비교 분석해주세요:

## 주요 특징 비교
- [보험1]: [주요 특징]
- [보험2]: [주요 특징]

## 보장 범위 비교
- [보험1]: [보장 내용]
- [보험2]: [보장 내용]

## 가입 조건 비교
- [보험1]: [가입 조건]
- [보험2]: [가입 조건]

## 추천 대상
- [보험1]: [어떤 사람에게 적합한지]
- [보험2]: [어떤 사람에게 적합한지]

## 결론
[전체적인 비교 결과와 추천]
"""
        
        return prompt 