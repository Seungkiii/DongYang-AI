from typing import List, Dict, Any
from langchain.schema import Document
from app.core.vector_store import VectorStore
from app.core.config import get_settings
import logging
import re

settings = get_settings()
logger = logging.getLogger(__name__)

class InsuranceRecommendationService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        
        # 보험 상품별 특징 매핑
        self.insurance_features = {
            "종신보험": {
                "keywords": ["종신", "사망", "보험금", "납입", "만기"],
                "age_range": "18-65",
                "purposes": ["사망보장", "노후대비", "가족보장"],
                "coverage_types": ["사망보장", "종신보장"],
                "description": "보험 계약자의 생명 전기간 동안 보장하는 보험"
            },
            "정기보험": {
                "keywords": ["정기", "기간", "사망", "보험금", "만기"],
                "age_range": "18-65",
                "purposes": ["사망보장", "기간보장", "가족보장"],
                "coverage_types": ["사망보장", "기간보장"],
                "description": "정한 기간 동안 보장하는 보험"
            },
            "암보험": {
                "keywords": ["암", "진단", "입원", "수술", "치료"],
                "age_range": "18-65",
                "purposes": ["질병보장", "암대비", "치료비보장"],
                "coverage_types": ["질병보장", "암보장"],
                "description": "암 진단 시 보장하는 보험"
            },
            "실손보험": {
                "keywords": ["실손", "의료비", "실제", "보장", "치료"],
                "age_range": "18-65",
                "purposes": ["의료비보장", "실손보장", "치료비보장"],
                "coverage_types": ["의료비보장", "실손보장"],
                "description": "실제 발생한 의료비를 보장하는 보험"
            },
            "유니버셜보험": {
                "keywords": ["유니버셜", "투자", "적립", "보험료", "만기"],
                "age_range": "18-65",
                "purposes": ["투자", "적립", "노후대비"],
                "coverage_types": ["투자보장", "적립보장"],
                "description": "보장과 투자를 결합한 보험"
            },
            "알뜰플러스": {
                "keywords": ["알뜰", "플러스", "종신", "납입", "보장"],
                "age_range": "18-65",
                "purposes": ["종신보장", "알뜰보장", "가족보장"],
                "coverage_types": ["종신보장", "알뜰보장"],
                "description": "알뜰한 보험료로 종신보장을 제공하는 보험"
            }
        }
    
    def extract_user_info(self, question: str) -> Dict[str, Any]:
        """질문에서 사용자 정보를 추출합니다."""
        user_info = {
            "age": None,
            "purpose": None,
            "coverage_type": None
        }
        
        question_lower = question.lower()
        
        # 나이 추출
        age_patterns = [
            r'(\d+)대',
            r'(\d+)세',
            r'나이\s*(\d+)',
            r'(\d+)살'
        ]
        for pattern in age_patterns:
            match = re.search(pattern, question_lower)
            if match:
                age = int(match.group(1))
                if age < 20:
                    user_info["age"] = "20대"
                elif age < 30:
                    user_info["age"] = "20대"
                elif age < 40:
                    user_info["age"] = "30대"
                elif age < 50:
                    user_info["age"] = "40대"
                elif age < 60:
                    user_info["age"] = "50대"
                else:
                    user_info["age"] = "60대"
                break
        
        # 목적 추출
        purpose_keywords = {
            "사망보장": ["사망", "죽음", "가족보장"],
            "질병보장": ["질병", "병", "암", "치료"],
            "의료비보장": ["의료비", "병원비", "치료비", "실손"],
            "노후대비": ["노후", "은퇴", "적립", "투자"],
            "기간보장": ["기간", "정기", "특정기간"]
        }
        
        for purpose, keywords in purpose_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                user_info["purpose"] = purpose
                break
        
        # 보장 유형 추출
        coverage_keywords = {
            "사망보장": ["사망", "죽음"],
            "질병보장": ["질병", "병", "암"],
            "의료비보장": ["의료비", "병원비", "치료비"],
            "투자보장": ["투자", "적립", "유니버셜"],
            "종신보장": ["종신", "평생"]
        }
        
        for coverage, keywords in coverage_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                user_info["coverage_type"] = coverage
                break
        
        return user_info
    
    def calculate_recommendation_score(self, insurance_name: str, user_info: Dict[str, Any]) -> float:
        """보험 상품의 추천 점수를 계산합니다."""
        if insurance_name not in self.insurance_features:
            return 0.0
        
        features = self.insurance_features[insurance_name]
        score = 0.0
        
        # 목적 매칭 점수 (40점)
        if user_info["purpose"] and user_info["purpose"] in features["purposes"]:
            score += 40
        
        # 보장 유형 매칭 점수 (30점)
        if user_info["coverage_type"] and user_info["coverage_type"] in features["coverage_types"]:
            score += 30
        
        # 나이 매칭 점수 (20점)
        if user_info["age"]:
            # 모든 보험이 18-65세 대상이므로 기본 점수 부여
            score += 20
        
        # 키워드 매칭 점수 (10점)
        question_lower = user_info.get("question", "").lower()
        if any(keyword in question_lower for keyword in features["keywords"]):
            score += 10
        
        return score
    
    def get_insurance_info(self, insurance_name: str) -> Dict[str, Any]:
        """특정 보험 상품의 정보를 검색합니다."""
        try:
            # 보험명으로 검색
            docs = self.vector_store.similarity_search(
                query=insurance_name,
                k=3
            )
            
            # 관련 키워드로 추가 검색
            if insurance_name in self.insurance_features:
                for keyword in self.insurance_features[insurance_name]["keywords"]:
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
            content = "\n\n".join([doc.page_content for doc in unique_docs[:3]])
            
            return {
                "name": insurance_name,
                "content": content,
                "documents": len(unique_docs),
                "features": self.insurance_features.get(insurance_name, {})
            }
            
        except Exception as e:
            logger.error(f"보험 정보 검색 실패: {insurance_name}, 오류: {e}")
            return {
                "name": insurance_name,
                "content": f"{insurance_name}에 대한 정보를 찾을 수 없습니다.",
                "documents": 0,
                "features": self.insurance_features.get(insurance_name, {})
            }
    
    def recommend_insurances(self, question: str) -> Dict[str, Any]:
        """사용자 정보를 기반으로 보험을 추천합니다."""
        # 사용자 정보 추출
        user_info = self.extract_user_info(question)
        user_info["question"] = question
        
        # 각 보험의 추천 점수 계산
        recommendations = []
        for insurance_name in self.insurance_features.keys():
            score = self.calculate_recommendation_score(insurance_name, user_info)
            if score > 0:  # 점수가 있는 보험만 추천
                recommendations.append({
                    "insurance_name": insurance_name,
                    "score": score,
                    "features": self.insurance_features[insurance_name]
                })
        
        # 점수 순으로 정렬 (높은 점수 순)
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        # 상위 3개 추천
        top_recommendations = recommendations[:3]
        
        # 추천 보험의 상세 정보 수집
        detailed_recommendations = []
        for rec in top_recommendations:
            info = self.get_insurance_info(rec["insurance_name"])
            detailed_recommendations.append({
                **rec,
                "content": info["content"],
                "documents": info["documents"]
            })
        
        return {
            "user_info": user_info,
            "recommendations": detailed_recommendations,
            "total_recommendations": len(recommendations)
        }
    
    def create_recommendation_prompt(self, recommendation_result: Dict[str, Any]) -> str:
        """추천 분석을 위한 프롬프트를 생성합니다."""
        user_info = recommendation_result["user_info"]
        recommendations = recommendation_result["recommendations"]
        
        prompt = f"""사용자 정보를 바탕으로 보험 상품을 추천해주세요.

## 사용자 정보
- 나이: {user_info.get('age', '정보 없음')}
- 목적: {user_info.get('purpose', '정보 없음')}
- 보장 유형: {user_info.get('coverage_type', '정보 없음')}
- 질문: {user_info.get('question', '')}

## 추천 보험 상품 정보
"""
        
        for i, rec in enumerate(recommendations, 1):
            prompt += f"""
=== {i}. {rec['insurance_name']} (추천 점수: {rec['score']}점) ===
- 특징: {rec['features'].get('description', '정보 없음')}
- 적합한 목적: {', '.join(rec['features'].get('purposes', []))}
- 보장 유형: {', '.join(rec['features'].get('coverage_types', []))}
- 문서 수: {rec['documents']}개
- 상세 내용:
{rec['content'][:300]}...
"""
        
        prompt += """
다음 형식으로 추천 분석해주세요:

## 추천 이유
[사용자 정보를 바탕으로 한 추천 이유]

## 각 보험 상품별 특징
1. [보험1]: [주요 특징과 장점]
2. [보험2]: [주요 특징과 장점]
3. [보험3]: [주요 특징과 장점]

## 최종 추천
[가장 적합한 보험과 그 이유]

## 추가 고려사항
[가입 시 고려해야 할 사항들]
"""
        
        return prompt 