# 동양생명 보험 챗봇 - AI 서버 (RAG 시스템)

## 프로젝트 개요
동양생명 보험 챗봇의 AI 엔진입니다. FastAPI 기반으로 구축되었으며, RAG(Retrieval Augmented Generation) 시스템을 통해 보험 PDF 문서를 기반으로 한 전문적인 보험 상담 서비스를 제공합니다.

## 주요 기능
- **RAG 기반 질의응답**: 보험 PDF 문서를 벡터화하여 정확한 정보 검색 및 답변 생성
- **의도 분석**: 사용자 질문의 의도를 분석하여 적절한 응답 전략 선택
- **보험 상품 정보 제공**: 실제 약관 기반 상품별 상세 정보 안내
- **보험 상품 비교**: 여러 보험 상품 간 객관적 비교 분석
- **보험 추천**: 사용자 조건에 맞는 맞춤형 보험 상품 추천
- **신뢰도 평가**: AI 응답의 신뢰도를 수치화하여 제공

## 기술 스택

### 핵심 AI/ML 스택
- **OpenAI GPT-4**: 자연어 생성 및 이해 (모델: `gpt-4-1106-preview`)
- **OpenAI text-embedding-ada-002**: 문서 및 질의 임베딩 (1536차원 벡터)
- **ChromaDB 0.4.x**: 벡터 데이터베이스 (SQLite 기반, 코사인 유사도 검색)
- **LangChain 0.1.x**: RAG 파이프라인 구축 (Document Loader, Text Splitter, Vector Store)
- **FAISS**: 고성능 벡터 유사도 검색 (선택적 사용)
- **Sentence Transformers**: 추가 임베딩 모델 지원 (다국어)

### 웹 프레임워크 및 도구
- **FastAPI**: 고성능 웹 API 프레임워크
- **Python 3.11**: 메인 프로그래밍 언어
- **Pydantic**: 데이터 검증 및 직렬화
- **Uvicorn**: ASGI 서버
- **Docker**: 컨테이너화

## RAG 시스템 아키텍처

```
사용자 질문
    ↓
의도 분석 (Intent Classification)
    ↓
벡터 검색 (Vector Search)
    ↓
컨텍스트 추출 (Context Retrieval)
    ↓
GPT-4 답변 생성 (Answer Generation)
    ↓
신뢰도 평가 (Confidence Scoring)
    ↓
구조화된 응답 반환
```

### 벡터 데이터베이스 구성
- **문서 수**: 19개 보험 PDF 파일
- **청크 수**: 566개 텍스트 청크
- **임베딩 모델**: OpenAI text-embedding-ada-002
- **벡터 차원**: 1536차원
- **저장소**: ChromaDB (SQLite 기반)

## API 명세

### 1. 채팅 API
```http
POST /chat
Content-Type: application/json

{
  "question": "무배당엔젤상해보험에 대해 알려주세요",
  "context_count": 8
}
```

**응답 예시:**
```json
{
  "answer": "**상품명**: 무배당엔젤상해보험\n**주요 특징**: 상해로 인한 사망·후유장해, 입원 및 수술비 등을 보장하는 상해전문 보험입니다.\n**보장 내용**: 상해사망, 상해입원일당, 상해수술비 등\n**가입 조건**: 만 15세 ~ 70세, 일반 건강체 대상\n**주의사항**: 고의사고, 전쟁/테러 등 보장 제외",
  "confidence": 0.87,
  "contexts": [
    {
      "content": "무배당엔젤상해보험은 상해로 인한 사망, 후유장해...",
      "source": "무배당엔젤상해보험.pdf",
      "page": 3
    }
  ],
  "intent": "insurance_info"
}
```

### 2. 헬스체크 API
```http
GET /
```

**응답:**
```json
{
  "status": "healthy",
  "service": "AI Server",
  "version": "1.0.0",
  "vector_store_status": "ready",
  "documents_count": 19,
  "chunks_count": 566
}
```

## 환경 설정

### 필수 환경변수
```bash
# OpenAI API 키
OPENAI_API_KEY=sk-your-openai-api-key

# 벡터 스토어 경로
VECTOR_STORE_PATH=/app/vector_store

# 문서 경로
DOCUMENTS_PATH=/app/documents

# 서버 설정
HOST=0.0.0.0
PORT=8000

# 로깅 레벨
LOG_LEVEL=INFO
```

## 로컬 개발 환경 설정

### 1. 사전 요구사항
- Python 3.11+
- pip 또는 poetry
- OpenAI API 키

### 2. 프로젝트 설정
```bash
# 저장소 클론
git clone https://github.com/your-username/DogYang-Chatbot-AI.git
cd DogYang-Chatbot-AI

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 OpenAI API 키 등 설정
```

### 3. 문서 임베딩
```bash
# PDF 문서를 벡터 데이터베이스에 임베딩
python vectorize_documents.py

# 또는 빠른 임베딩 (기존 벡터 스토어가 있는 경우)
python quick_vectorize.py
```

### 4. 서버 실행
```bash
# 개발 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 Python으로 직접 실행
python -m app.main
```

### 5. Docker로 실행
```bash
# Docker 이미지 빌드
docker build -t dongyang-ai .

# 컨테이너 실행
docker run -p 8000:8000 --env-file .env -v ./vector_store:/app/vector_store dongyang-ai
```

## 테스트

### API 테스트
```bash
# 헬스체크
curl http://localhost:8000/

# 채팅 테스트
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "무배당엔젤상해보험의 보장 내용이 뭐야?",
    "context_count": 5
  }'
```

### 벡터 검색 테스트
```python
# Python 스크립트로 벡터 검색 테스트
from app.core.vector_store import VectorStore

vector_store = VectorStore(openai_api_key="your-key")
results = vector_store.similarity_search("상해보험", k=5)
for doc in results:
    print(f"Source: {doc.metadata['source']}")
    print(f"Content: {doc.page_content[:100]}...")
```

## RAG 파이프라인 구현 상세

### 1. 문서 전처리 (Document Processing)
```python
# app/utils/document_loader.py
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,        # 청크 크기
            chunk_overlap=200,      # 오버랩 크기
            separators=["\n\n", "\n", ".", " "]  # 분할 기준
        )
    
    def load_pdf(self, file_path: str):
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        
        # 메타데이터 추가
        for i, page in enumerate(pages):
            page.metadata.update({
                "source": file_path.split("/")[-1],
                "page": i + 1,
                "chunk_id": f"{file_path}_{i}"
            })
        
        return self.text_splitter.split_documents(pages)
```

### 2. 벡터화 및 저장 (Vectorization & Storage)
```python
# app/core/vector_store.py
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
import chromadb

class VectorStore:
    def __init__(self, openai_api_key: str, collection_name: str = "insurance_docs"):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=openai_api_key,
            chunk_size=1000  # 배치 처리 크기
        )
        
        # ChromaDB 클라이언트 설정
        self.chroma_client = chromadb.PersistentClient(
            path="./vector_store"
        )
        
        self.vector_store = Chroma(
            client=self.chroma_client,
            collection_name=collection_name,
            embedding_function=self.embeddings
        )
    
    def add_documents(self, documents):
        """PDF 문서들을 벡터 데이터베이스에 추가"""
        return self.vector_store.add_documents(documents)
    
    def similarity_search(self, query: str, k: int = 5):
        """코사인 유사도 기반 검색"""
        return self.vector_store.similarity_search(
            query, 
            k=k,
            search_type="similarity"
        )
    
    def similarity_search_with_score(self, query: str, k: int = 5):
        """유사도 점수와 함께 검색"""
        return self.vector_store.similarity_search_with_score(query, k=k)
```

### 3. 검색기 (Retriever) 구현
```python
# app/core/retriever.py
from typing import List, Dict, Any
from langchain.schema import Document

class InsuranceRetriever:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.insurance_keywords = [
            "보험", "상해", "엔젤", "수호천사", 
            "종신", "암보험", "실손", "건강", "연금"
        ]
    
    def retrieve_contexts(self, query: str, k: int = 8) -> List[Document]:
        """RAG를 위한 컨텍스트 검색"""
        
        # 1. 보험 관련 키워드 강화
        enhanced_query = self._enhance_query(query)
        
        # 2. 벡터 유사도 검색
        docs_with_scores = self.vector_store.similarity_search_with_score(
            enhanced_query, k=k*2  # 더 많이 검색 후 필터링
        )
        
        # 3. 신뢰도 기반 필터링
        filtered_docs = self._filter_by_relevance(docs_with_scores, threshold=0.3)
        
        # 4. 중복 제거 및 다양성 보장
        diverse_docs = self._ensure_diversity(filtered_docs[:k])
        
        return diverse_docs
    
    def _enhance_query(self, query: str) -> str:
        """Query에 보험 관련 컨텍스트 추가"""
        for keyword in self.insurance_keywords:
            if keyword in query:
                return f"{query} {keyword} 보장 약관"
        return query
    
    def _filter_by_relevance(self, docs_with_scores, threshold: float):
        """유사도 임계값 기반 필터링"""
        return [doc for doc, score in docs_with_scores if score <= threshold]
```

### 4. 생성기 (Generator) 구현
```python
# app/core/chat_engine.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

class InsuranceGenerator:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4-1106-preview",
            temperature=0.1,  # 일관성 있는 답변
            max_tokens=2000,
            openai_api_key=openai_api_key
        )
        
        self.system_prompt = self._load_system_prompt()
    
    def generate_answer(self, question: str, contexts: List[Document]) -> Dict[str, Any]:
        """RAG 기반 답변 생성"""
        
        # 1. 컨텍스트 문자열 구성
        context_str = self._format_contexts(contexts)
        
        # 2. 프롬프트 구성
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"""
            컨텍스트: {context_str}
            
            사용자 질문: {question}
            
            위 컨텍스트를 바탕으로 구조화된 답변을 생성해주세요.
            """)
        ]
        
        # 3. LLM 호출
        response = self.llm(messages)
        
        # 4. 신뢰도 계산
        confidence = self._calculate_confidence(question, contexts, response.content)
        
        return {
            "answer": response.content,
            "confidence": confidence,
            "contexts": self._format_context_metadata(contexts),
            "token_usage": response.response_metadata.get("token_usage", {})
        }
    
    def _format_contexts(self, contexts: List[Document]) -> str:
        """RAG 컨텍스트를 프롬프트용 문자열로 변환"""
        formatted = []
        for i, doc in enumerate(contexts, 1):
            formatted.append(f"""
            [문서 {i}] {doc.metadata.get('source', '알수없음')}
            페이지: {doc.metadata.get('page', 'N/A')}
            내용: {doc.page_content}
            ---
            """)
        return "\n".join(formatted)
```

### 5. 신뢰도 평가 시스템
```python
# app/core/confidence_utils.py
import numpy as np
from typing import List
from langchain.schema import Document

class ConfidenceCalculator:
    def __init__(self):
        self.weights = {
            "context_similarity": 0.4,    # 컨텍스트 유사도
            "answer_completeness": 0.3,   # 답변 완성도
            "source_reliability": 0.2,    # 소스 신뢰성
            "consistency": 0.1            # 답변 일관성
        }
    
    def calculate(self, question: str, contexts: List[Document], answer: str) -> float:
        """RAG 응답의 신뢰도 계산"""
        
        scores = {
            "context_similarity": self._context_similarity_score(question, contexts),
            "answer_completeness": self._answer_completeness_score(answer),
            "source_reliability": self._source_reliability_score(contexts),
            "consistency": self._consistency_score(contexts, answer)
        }
        
        # 가중 평균 계산
        weighted_score = sum(
            scores[metric] * self.weights[metric] 
            for metric in scores
        )
        
        return min(max(weighted_score, 0.0), 1.0)  # 0-1 범위로 정규화
    
    def _context_similarity_score(self, question: str, contexts: List[Document]) -> float:
        """Question과 Context의 유사도 평가"""
        if not contexts:
            return 0.0
        
        # 간단한 키워드 기반 유사도 (실제로는 임베딩 유사도 사용)
        question_words = set(question.lower().split())
        context_scores = []
        
        for doc in contexts:
            context_words = set(doc.page_content.lower().split())
            overlap = len(question_words & context_words)
            score = overlap / max(len(question_words), 1)
            context_scores.append(score)
        
        return np.mean(context_scores)
    
    def _answer_completeness_score(self, answer: str) -> float:
        """Answer의 완성도 평가"""
        # 구조화된 답변 형식 확인
        required_sections = ["상품명", "주요 특징", "보장 내용", "가입 조건"]
        present_sections = sum(1 for section in required_sections if section in answer)
        
        length_score = min(len(answer) / 500, 1.0)  # 최소 500자 기대
        structure_score = present_sections / len(required_sections)
        
        return (length_score + structure_score) / 2
```

## 의도 분류 시스템

### 지원하는 의도 유형
- **insurance_info**: 보험 상품 정보 질의
- **insurance_comparison**: 보험 상품 비교
- **insurance_recommendation**: 보험 상품 추천
- **general_chat**: 일반 대화 및 기타 질의

### 의도별 처리 전략
```python
# insurance_info: 단일 상품 상세 정보 제공
# insurance_comparison: 다중 상품 비교 분석
# insurance_recommendation: 사용자 조건 기반 추천
# general_chat: 보험 관련 일반 질의응답
```

## 신뢰도 평가 시스템

### 신뢰도 계산 요소
1. **컨텍스트 유사도**: 검색된 문서와 질문의 관련성
2. **답변 일관성**: 생성된 답변의 논리적 일관성
3. **소스 신뢰성**: 참조 문서의 신뢰성
4. **완성도**: 답변의 완전성 및 구체성

### 임계값 설정
- **높은 신뢰도 (0.7+)**: 확신 있는 답변 제공
- **중간 신뢰도 (0.3-0.7)**: 조건부 답변 + 추가 정보 요청
- **낮은 신뢰도 (0.3-)**: 답변 보류 + 재질문 유도

## CI/CD 파이프라인

### GitHub Actions Workflow
`.github/workflows/deploy.yml`을 통한 자동 배포:

**배포 트리거:**
- `main` 브랜치 push 시 자동 배포
- Pull Request 시 테스트 실행

**배포 단계:**
1. **의존성 설치**: requirements.txt 기반 패키지 설치
2. **테스트 실행**: 단위 테스트 및 API 테스트
3. **Docker 이미지 빌드**: 최적화된 프로덕션 이미지 생성
4. **EC2 배포**: SSH를 통한 원격 서버 배포
5. **벡터 스토어 동기화**: 기존 임베딩 데이터 보존
6. **서비스 재시작**: 무중단 배포
7. **헬스체크**: 배포 후 서비스 상태 확인

**환경변수 관리:**
- GitHub Secrets를 통한 민감 정보 보호
- `OPENAI_API_KEY`, `EC2_HOST`, `EC2_PRIVATE_KEY` 등

## 모니터링 및 로깅

### 주요 로그 포인트
```python
# API 요청/응답 로깅
logger.info(f"Chat request: {question[:50]}...")
logger.info(f"Response confidence: {confidence}")

# 벡터 검색 로깅
logger.debug(f"Retrieved {len(contexts)} contexts")

# OpenAI API 호출 로깅
logger.info(f"OpenAI API call: {model}, tokens: {tokens}")

# 에러 로깅
logger.error(f"Vector search failed: {str(e)}")
```

### 성능 메트릭
- **응답 시간**: 평균 2-5초 (벡터 검색 + GPT 생성)
- **토큰 사용량**: 질문당 평균 1000-2000 토큰
- **검색 정확도**: 상위 5개 문서 중 관련 문서 비율
- **사용자 만족도**: 신뢰도 점수 기반 품질 평가

## 트러블슈팅

### 일반적인 문제들

1. **벡터 스토어 초기화 실패**
   ```bash
   # ChromaDB 데이터 삭제 후 재생성
   rm -rf vector_store/
   python vectorize_documents.py
   ```

2. **OpenAI API 키 오류**
   ```bash
   # API 키 확인
   echo $OPENAI_API_KEY
   
   # API 키 테스트
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

3. **메모리 부족**
   ```bash
   # Docker 메모리 제한 증가
   docker run --memory=4g dongyang-ai
   
   # 또는 청크 크기 조정
   # chunk_size를 1000에서 500으로 감소
   ```

4. **느린 응답 속도**
   ```python
   # 컨텍스트 수 조정
   context_count = 5  # 기본값 8에서 5로 감소
   
   # 캐싱 활용
   # 동일 질문에 대한 응답 캐싱 구현
   ```

## 성능 최적화

### 1. 벡터 검색 최적화
- 인덱스 튜닝: HNSW 알고리즘 파라미터 조정
- 배치 처리: 다중 질문 동시 처리
- 캐싱: 자주 검색되는 벡터 결과 캐싱

### 2. LLM 호출 최적화
- 프롬프트 압축: 불필요한 컨텍스트 제거
- 배치 요청: 여러 질문을 하나의 요청으로 처리
- 스트리밍: 긴 답변의 점진적 전송

### 3. 메모리 관리
- 벡터 스토어 분할: 대용량 문서 처리
- 가비지 컬렉션: 주기적 메모리 정리
- 연결 풀링: DB 연결 재사용

## 보안 고려사항

### API 보안
- Rate Limiting: 요청 빈도 제한
- Input Validation: 악성 입력 차단
- CORS 설정: 허용된 도메인만 접근

### 데이터 보안
- 개인정보 마스킹: 민감 정보 자동 제거
- 로그 암호화: 민감한 로그 데이터 암호화
- 접근 제어: 벡터 스토어 접근 권한 관리

## 라이센스
MIT License

## 기여하기
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 지원 및 문의
- 이슈 리포팅: GitHub Issues
- 기술 문의: [이메일 주소]
- 문서 개선: Pull Request 환영
