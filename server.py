import argparse
import os
from typing import Literal

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict

mcp = FastMCP('uncensored-ai-chat', host='127.0.0.1', port=8000)


class Message(BaseModel):
    model_config = ConfigDict(extra='forbid')
    role: Literal['system', 'user', 'assistant']
    content: str


@mcp.tool()
async def create_chat_completion(
    model: str,
    messages: list[Message],
) -> dict:
    """Uncensored 채팅 API를 호출합니다. 서비스 이용 요금이 발생할 수 있습니다."""
    if not model.strip() or not messages:
        raise ValueError('모델과 하나 이상의 메시지가 필요합니다.')
    url = 'https://api.uncensored.com/api/v1/chat/completions'
    key = os.environ.get('UNCENSORED_API_KEY', '')
    headers = {'X-api-key': key}
    if not key.strip():
        raise ValueError('선택한 제공자의 API 키 환경변수를 설정해 주세요.')
    payload = {'model': model, 'messages': [m.model_dump() for m in messages], 'stream': False}
    try:
        async with httpx.AsyncClient(timeout=120, follow_redirects=False) as client:
            response = await client.post(url, headers=headers, json=payload)
        if not 200 <= response.status_code < 300:
            raise ValueError(f'제공자 API 오류: HTTP {response.status_code}')
        result = response.json()
        if not isinstance(result, dict):
            raise ValueError('제공자가 JSON 객체를 반환하지 않았습니다.')
        return result
    except httpx.TimeoutException:
        raise ValueError('API 요청 제한 시간 120초를 초과했습니다.') from None
    except httpx.RequestError:
        raise ValueError('API 서버 연결에 실패했습니다.') from None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='채팅 API MCP 서버')
    parser.add_argument('--transport', choices=['stdio', 'streamable-http'], default='stdio')
    args = parser.parse_args()
    mcp.run(transport=args.transport)
