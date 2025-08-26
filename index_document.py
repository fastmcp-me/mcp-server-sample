#!/usr/bin/env python3
"""
PDF 문서를 파싱하고 ChromaDB에 벡터로 저장하는 스크립트
"""

import os
import logging
from typing import List, Dict, Any
from pathlib import Path

import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIndexer:
    def __init__(self, pdf_path: str = "2025_tax.pdf", collection_name: str = "tax_document"):
        self.pdf_path = pdf_path
        self.collection_name = collection_name
        self.chroma_host = os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = os.getenv("CHROMA_PORT", "8000")
        
        # ChromaDB 클라이언트 초기화
        self.chroma_client = chromadb.HttpClient(
            host=self.chroma_host,
            port=self.chroma_port,
            settings=Settings(allow_reset=True)
        )
        
        # 임베딩 모델 초기화 (한국어 지원)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="jhgan/ko-sroberta-multitask",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # 텍스트 분할기 초기화
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdf(self) -> List[str]:
        """PDF 파일을 로드하고 텍스트를 추출합니다."""
        logger.info(f"PDF 파일 로딩 중: {self.pdf_path}")
        
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {self.pdf_path}")
        
        try:
            loader = PyPDFLoader(self.pdf_path)
            pages = loader.load()
            
            texts = []
            for i, page in enumerate(pages):
                text = page.page_content.strip()
                if text:
                    texts.append(f"페이지 {i+1}: {text}")
            
            logger.info(f"총 {len(texts)} 페이지의 텍스트를 추출했습니다.")
            return texts
            
        except Exception as e:
            logger.error(f"PDF 로딩 중 오류 발생: {e}")
            raise
    
    def split_text(self, texts: List[str]) -> List[str]:
        """텍스트를 청크로 분할합니다."""
        logger.info("텍스트 청크 분할 중...")
        
        chunks = []
        for text in texts:
            text_chunks = self.text_splitter.split_text(text)
            chunks.extend(text_chunks)
        
        logger.info(f"총 {len(chunks)}개의 청크로 분할했습니다.")
        return chunks
    
    def create_metadata(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """각 청크에 대한 메타데이터를 생성합니다."""
        metadata_list = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "chunk_id": i,
                "source": self.pdf_path,
                "document_type": "tax_law_2025",
                "chunk_size": len(chunk),
                "language": "ko"
            }
            metadata_list.append(metadata)
        
        return metadata_list
    
    def index_documents(self):
        """문서를 인덱싱하고 ChromaDB에 저장합니다."""
        logger.info("문서 인덱싱 시작...")
        
        # 기존 컬렉션이 있다면 삭제
        try:
            self.chroma_client.delete_collection(self.collection_name)
            logger.info(f"기존 컬렉션 '{self.collection_name}' 삭제됨")
        except:
            pass
        
        # PDF 로드 및 텍스트 추출
        texts = self.load_pdf()
        
        # 텍스트 청크 분할
        chunks = self.split_text(texts)
        
        # 메타데이터 생성
        metadata_list = self.create_metadata(chunks)
        
        # ChromaDB에 저장
        logger.info("ChromaDB에 벡터 저장 중...")
        
        vectorstore = Chroma.from_texts(
            texts=chunks,
            embedding=self.embeddings,
            collection_name=self.collection_name,
            client=self.chroma_client,
            metadatas=metadata_list
        )
        
        # 컬렉션 정보 출력
        collection = self.chroma_client.get_collection(self.collection_name)
        count = collection.count()
        
        logger.info(f"인덱싱 완료! 총 {count}개의 청크가 저장되었습니다.")
        logger.info(f"컬렉션 이름: {self.collection_name}")
        
        return vectorstore
    
    def test_search(self, query: str = "소득세", k: int = 3):
        """검색 기능을 테스트합니다."""
        logger.info(f"검색 테스트: '{query}'")
        
        vectorstore = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            client=self.chroma_client
        )
        
        results = vectorstore.similarity_search(query, k=k)
        
        logger.info(f"검색 결과 ({len(results)}개):")
        for i, result in enumerate(results, 1):
            logger.info(f"\n--- 결과 {i} ---")
            logger.info(f"내용: {result.page_content[:200]}...")
            logger.info(f"메타데이터: {result.metadata}")
        
        return results

def main():
    """메인 실행 함수"""
    try:
        # 인덱서 초기화
        indexer = DocumentIndexer()
        
        # 문서 인덱싱
        vectorstore = indexer.index_documents()
        
        # 검색 테스트
        indexer.test_search("소득세")
        indexer.test_search("법인세")
        
        logger.info("모든 작업이 완료되었습니다!")
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        raise

if __name__ == "__main__":
    main()
