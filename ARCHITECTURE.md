# 동양생명 보험 챗봇 시스템 아키텍처

## 시스템 개요
동양생명 보험 챗봇은 3-tier 아키텍처로 구성된 AI 기반 보험 상담 서비스입니다.

```
┌─────────────────────────────────────────────────────────────────┐
│                        사용자 (User)                              │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTPS/HTTP
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                          │
│                  (EC2: 80, 443 포트)                           │
└─────────────┬───────────────────────┬───────────────────────────┘
              │                       │
              ▼                       ▼
┌─────────────────────────┐  ┌─────────────────────────────────────┐
│     Frontend            │  │           Backend                   │
│   (React + TypeScript)  │  │      (Spring Boot + Java)          │
│   Port: 3000            │  │         Port: 8080                  │
│                         │  │                                     │
│ • 사용자 인터페이스      │  │ • REST API 제공                    │
│ • 실시간 채팅 UI        │  │ • 프론트엔드-AI 서버 중계           │
│ • 신뢰도 시각화         │  │ • 세션 관리                        │
│ • 응답 구조화 표시      │  │ • 로깅 및 모니터링                 │
└─────────────────────────┘  └─────────────┬───────────────────────┘
                                           │ HTTP API 호출
                                           ▼
                              ┌─────────────────────────────────────┐
                              │            AI Server                │
                              │      (FastAPI + Python)            │
                              │         Port: 8000                  │
                              │                                     │
                              │ • RAG (검색 증강 생성)              │
                              │ • OpenAI GPT-4 통합                │
                              │ • 벡터 검색 (ChromaDB)             │
                              │ • 의도 분석 및 답변 생성            │
                              └─────────────┬───────────────────────┘
                                           │
                                           ▼
                              ┌─────────────────────────────────────┐
                              │         Vector Database             │
                              │          (ChromaDB)                 │
                              │                                     │
                              │ • 보험 PDF 문서 임베딩              │
                              │ • 유사도 기반 검색                  │
                              │ • 19개 PDF → 566개 청크            │
                              └─────────────────────────────────────┘
```

## 데이터 흐름 (Data Flow)

```
1. 사용자 질문 입력
   ↓
2. Frontend → Backend (REST API)
   ↓
3. Backend → AI Server (FastAPI)
   ↓
4. AI Server → Vector DB (유사도 검색)
   ↓
5. AI Server → OpenAI GPT (RAG 기반 답변 생성)
   ↓
6. AI Server → Backend (구조화된 응답)
   ↓
7. Backend → Frontend (JSON 응답)
   ↓
8. Frontend → 사용자 (UI 렌더링)
```

## 주요 API 엔드포인트

### Frontend ↔ Backend
- `POST /api/chat` - 채팅 메시지 전송
- `GET /api/health` - 서비스 상태 확인

### Backend ↔ AI Server
- `POST /chat` - RAG 기반 질의응답
- `GET /` - AI 서버 상태 확인

## 배포 환경

### AWS EC2 인스턴스
- **주소**: `ec2-3-38-100-135.ap-northeast-2.compute.amazonaws.com`
- **OS**: Amazon Linux 2
- **Docker**: 모든 서비스 컨테이너화
- **Nginx**: 리버스 프록시 및 정적 파일 서빙

### 포트 구성
- **80**: HTTP (Nginx)
- **443**: HTTPS (Nginx) - SSL 인증서 필요
- **3000**: Frontend (내부)
- **8080**: Backend (내부)
- **8000**: AI Server (내부)

## 기술 스택

### Frontend
- React 18, TypeScript, Vite
- Tailwind CSS, Zustand
- Axios (API 통신)

### Backend
- Spring Boot 3.x, Java 17
- Spring Web, JPA
- Docker

### AI Server
- FastAPI, Python 3.11
- LangChain, OpenAI GPT-4
- ChromaDB (벡터 데이터베이스)
- Docker

### 인프라
- AWS EC2, Docker Compose
- Nginx (리버스 프록시)
- GitHub Actions (CI/CD)
