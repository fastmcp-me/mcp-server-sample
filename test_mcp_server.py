#!/usr/bin/env python3
"""
MCP 서버 테스트 스크립트
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPClientTest:
    def __init__(self, server_path: str = "python mcp_server.py"):
        self.server_path = server_path
        self.process = None
    
    async def start_server(self):
        """MCP 서버를 시작합니다."""
        try:
            self.process = subprocess.Popen(
                self.server_path.split(),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info("MCP 서버가 시작되었습니다.")
            await asyncio.sleep(2)  # 서버 초기화 대기
        except Exception as e:
            logger.error(f"서버 시작 실패: {e}")
            raise
    
    async def stop_server(self):
        """MCP 서버를 중지합니다."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            logger.info("MCP 서버가 중지되었습니다.")
    
    async def send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 서버에 요청을 보냅니다."""
        try:
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # 응답 읽기
            response_line = self.process.stdout.readline()
            if response_line:
                return json.loads(response_line)
            else:
                raise Exception("서버로부터 응답을 받지 못했습니다.")
                
        except Exception as e:
            logger.error(f"요청 전송 실패: {e}")
            raise
    
    async def test_list_tools(self):
        """도구 목록 조회를 테스트합니다."""
        logger.info("=== 도구 목록 조회 테스트 ===")
        
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        try:
            response = await self.send_request(request)
            logger.info(f"응답: {json.dumps(response, indent=2, ensure_ascii=False)}")
            return response
        except Exception as e:
            logger.error(f"도구 목록 조회 실패: {e}")
            return None
    
    async def test_search_document(self, query: str, max_results: int = 3):
        """문서 검색을 테스트합니다."""
        logger.info(f"=== 문서 검색 테스트: '{query}' ===")
        
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "search_document",
                "arguments": {
                    "query": query,
                    "max_results": max_results
                }
            }
        }
        
        try:
            response = await self.send_request(request)
            logger.info(f"검색 결과: {json.dumps(response, indent=2, ensure_ascii=False)}")
            return response
        except Exception as e:
            logger.error(f"문서 검색 실패: {e}")
            return None
    
    async def test_get_document_info(self):
        """문서 정보 조회를 테스트합니다."""
        logger.info("=== 문서 정보 조회 테스트 ===")
        
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_document_info",
                "arguments": {}
            }
        }
        
        try:
            response = await self.send_request(request)
            logger.info(f"문서 정보: {json.dumps(response, indent=2, ensure_ascii=False)}")
            return response
        except Exception as e:
            logger.error(f"문서 정보 조회 실패: {e}")
            return None
    
    async def test_list_collections(self):
        """컬렉션 목록 조회를 테스트합니다."""
        logger.info("=== 컬렉션 목록 조회 테스트 ===")
        
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "list_collections",
                "arguments": {}
            }
        }
        
        try:
            response = await self.send_request(request)
            logger.info(f"컬렉션 목록: {json.dumps(response, indent=2, ensure_ascii=False)}")
            return response
        except Exception as e:
            logger.error(f"컬렉션 목록 조회 실패: {e}")
            return None

async def main():
    """메인 테스트 함수"""
    client = MCPClientTest()
    
    try:
        # 서버 시작
        await client.start_server()
        
        # 테스트 실행
        await client.test_list_tools()
        await asyncio.sleep(1)
        
        await client.test_get_document_info()
        await asyncio.sleep(1)
        
        await client.test_list_collections()
        await asyncio.sleep(1)
        
        # 검색 테스트
        search_queries = ["소득세", "법인세", "부가가치세", "양도소득세"]
        for query in search_queries:
            await client.test_search_document(query, max_results=2)
            await asyncio.sleep(1)
        
        logger.info("모든 테스트가 완료되었습니다!")
        
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}")
    finally:
        # 서버 중지
        await client.stop_server()

if __name__ == "__main__":
    asyncio.run(main())
