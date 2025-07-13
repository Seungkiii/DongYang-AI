from typing import List, Dict
from pathlib import Path
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_pdf_documents(docs_path: str) -> List[Document]:
    """PDF 문서들을 로드하고 LangChain Document 객체로 변환합니다."""
    documents = []
    docs_dir = Path(docs_path)
    
    if not docs_dir.exists():
        logger.error(f"Documents directory does not exist: {docs_path}")
        return documents
    
    pdf_files = list(docs_dir.glob("*.pdf"))
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    successful_loads = 0
    failed_loads = 0
    
    for i, pdf_path in enumerate(pdf_files):
        try:
            logger.info(f"Loading PDF {i+1}/{len(pdf_files)}: {pdf_path.name}")
            
            reader = PdfReader(str(pdf_path))
            text = ""
            
            # 각 페이지에서 텍스트 추출
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num} of {pdf_path.name}: {e}")
                    continue
            
            if text.strip():
                doc = Document(
                    page_content=text.strip(),
                    metadata={
                        "source": pdf_path.name,
                        "file_path": str(pdf_path),
                        "pages": len(reader.pages)
                    }
                )
                documents.append(doc)
                successful_loads += 1
                logger.info(f"✅ Successfully loaded {pdf_path.name} ({len(reader.pages)} pages)")
            else:
                logger.warning(f"⚠️  No text extracted from {pdf_path.name}")
                failed_loads += 1
                
        except Exception as e:
            logger.error(f"❌ Error loading {pdf_path.name}: {e}")
            failed_loads += 1
    
    logger.info(f"📊 Loading Summary: {successful_loads} successful, {failed_loads} failed")
    return documents

def split_documents(documents: List[Document], chunk_size: int, chunk_overlap: int) -> List[Document]:
    """문서를 청크로 분할합니다."""
    logger.info(f"Splitting {len(documents)} documents into chunks (size: {chunk_size}, overlap: {chunk_overlap})")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    
    all_chunks = []
    for i, doc in enumerate(documents):
        try:
            doc_chunks = text_splitter.split_documents([doc])
            all_chunks.extend(doc_chunks)
            logger.info(f"Document {i+1}/{len(documents)} split into {len(doc_chunks)} chunks")
        except Exception as e:
            logger.error(f"Error splitting document {i+1}: {e}")
    
    logger.info(f"✅ Total chunks created: {len(all_chunks)}")
    return all_chunks 