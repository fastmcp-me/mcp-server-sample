#!/Users/cheolminbae/workspace/document-mcp/venv/bin/python3
"""
2025년 세법 개정안 문서 검색 MCP 서버 (간단 최종 버전)
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

import chromadb
from chromadb.config import Settings
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaxDocumentMCPServer:
    def __init__(self):
        self.chroma_host = os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = os.getenv("CHROMA_PORT", "8000")
        self.collection_name = os.getenv("CHROMA_COLLECTION", "tax_document")
        
        # OpenAI 클라이언트 초기화
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
        
        self.openai_client = OpenAI(api_key=openai_api_key)
        
        # ChromaDB 클라이언트 초기화
        try:
            self.chroma_client = chromadb.HttpClient(
                host=self.chroma_host,
                port=self.chroma_port,
                settings=Settings(allow_reset=True)
            )
            
            # 임베딩 모델 초기화
            self.embeddings = HuggingFaceEmbeddings(
                model_name="jhgan/ko-sroberta-multitask",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
            
            # VectorStore 초기화
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                client=self.chroma_client
            )
            
            logger.info("ChromaDB 연결 및 VectorStore 초기화 완료")
            
        except Exception as e:
            logger.error(f"ChromaDB 연결 실패: {e}")
            raise
    
    async def search_document(self, query: str, max_results: int = 5) -> str:
        """문서를 검색하고 OpenAI로 결과를 요약합니다."""
        try:
            logger.info(f"검색 쿼리: {query}, 최대 결과 수: {max_results}")
            
            # 벡터 검색 수행
            results = self.vectorstore.similarity_search(query, k=max_results)
            
            if not results:
                return f"'{query}'에 대한 검색 결과가 없습니다."
            
            # 검색 결과 수집
            search_content = []
            for i, result in enumerate(results, 1):
                content = result.page_content
                metadata = result.metadata
                
                search_content.append(f"""
결과 {i}:
내용: {content}
메타데이터: {metadata}
""")
            
            # OpenAI로 결과 요약
            prompt = f"""
다음은 2025년 세법 개정안 문서에서 '{query}'에 대한 검색 결과입니다.
이 결과를 바탕으로 사용자에게 도움이 되는 정보를 제공해주세요.

검색 결과:
{''.join(search_content)}

위 검색 결과를 바탕으로 다음을 수행해주세요:
1. 관련된 주요 내용을 요약
2. 사용자가 궁금해할 만한 추가 정보 제공
3. 한국어로 명확하고 이해하기 쉽게 설명

답변은 한국어로 작성해주세요.
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 2025년 세법 개정안 전문가입니다. 사용자에게 세법 정보를 명확하고 도움이 되게 설명해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"검색 중 오류 발생: {e}")
            return f"검색 중 오류가 발생했습니다: {str(e)}"
    
    async def get_document_info(self) -> str:
        """문서 정보를 조회합니다."""
        try:
            collection = self.chroma_client.get_collection(self.collection_name)
            count = collection.count()
            
            info_text = f"""
**2025년 세법 개정안 문서 정보**

- 문서명: 2025_tax.pdf
- 저장된 청크 수: {count}개
- 컬렉션명: {self.collection_name}
- 벡터 DB: ChromaDB
- 임베딩 모델: jhgan/ko-sroberta-multitask (한국어 지원)
- AI 모델: OpenAI GPT-4o-mini

이 문서는 2025년 세법 개정안에 대한 내용을 포함하고 있으며, 
자연어 쿼리를 통해 관련 세법 정보를 검색하고 AI가 요약하여 제공합니다.
"""
            
            return info_text
            
        except Exception as e:
            logger.error(f"문서 정보 조회 중 오류 발생: {e}")
            return f"문서 정보 조회 중 오류가 발생했습니다: {str(e)}"

async def handle_mcp_request():
    """MCP 요청을 처리합니다."""
    server = TaxDocumentMCPServer()
    
    while True:
        try:
            # stdin에서 요청 읽기
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line or line.strip() == "":
                continue
            
            try:
                request = json.loads(line.strip())
            except json.JSONDecodeError as e:
                logger.warning(f"JSON 파싱 오류, 무시: {e}")
                continue
            
            # ID가 null이면 건너뛰기
            if request.get("id") is None:
                logger.warning("ID가 null인 요청 무시")
                continue
            
            # 요청 처리
            if request.get("method") == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {
                                "listChanged": False
                            }
                        },
                        "serverInfo": {
                            "name": "tax-document-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif request.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": [
                            {
                                "name": "search_document",
                                "description": "2025년 세법 개정안 문서에서 관련 내용을 검색하고 AI로 요약합니다.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "검색할 쿼리 (예: '소득세', '법인세', '부가가치세' 등)"
                                        },
                                        "max_results": {
                                            "type": "integer",
                                            "description": "최대 결과 수 (기본값: 5)",
                                            "default": 5
                                        }
                                    },
                                    "required": ["query"]
                                }
                            },
                            {
                                "name": "get_document_info",
                                "description": "저장된 문서의 정보를 조회합니다.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {},
                                    "additionalProperties": False
                                }
                            }
                        ]
                    }
                }
            
            elif request.get("method") == "tools/call":
                name = request.get("params", {}).get("name")
                arguments = request.get("params", {}).get("arguments", {})
                
                if name == "search_document":
                    query = arguments.get("query", "")
                    max_results = arguments.get("max_results", 5)
                    result = await server.search_document(query, max_results)
                elif name == "get_document_info":
                    result = await server.get_document_info()
                else:
                    result = f"알 수 없는 도구: {name}"
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
            
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": "Method not found"
                    }
                }
            
            # 응답 출력
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
            
        except Exception as e:
            logger.error(f"요청 처리 중 오류 발생: {e}")
            if 'request' in locals() and request.get("id") is not None:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response, ensure_ascii=False))
                sys.stdout.flush()

async def main():
    """메인 함수"""
    try:
        logger.info("2025년 세법 개정안 MCP 서버 시작...")
        await handle_mcp_request()
    except KeyboardInterrupt:
        logger.info("서버가 중지되었습니다.")
    except Exception as e:
        logger.error(f"서버 실행 중 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
