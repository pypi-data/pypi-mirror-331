import time
from typing import Optional

from httpx import AsyncClient

from nekro_agent.api import core
from nekro_agent.api.schemas import AgentCtx

__meta__ = core.ExtMetaData(
    name="google_search",
    description="[NA] Google搜索工具",
    version="0.1.0",
    author="KroMiose",
    url="https://github.com/KroMiose/nekro-agent",
)

_last_keyword = None
_last_call_time = 0


@core.agent_collector.mount_method(core.MethodType.AGENT)
async def google_search(keyword: str, _ctx: AgentCtx) -> str:
    """使用 Google 搜索获取实时信息

    * 调用即此方法即结束响应，直到搜索结果返回

    Args:
        keyword (str): 搜索关键词
    """
    global _last_keyword, _last_call_time

    # 防止重复搜索和频繁调用
    if keyword == _last_keyword and time.time() - _last_call_time < 10:
        return "[错误] 禁止频繁搜索相同内容，结果无变化"

    proxy = core.config.DEFAULT_PROXY
    api_key = core.config.GOOGLE_SEARCH_API_KEY
    cx_key = core.config.GOOGLE_SEARCH_CX_KEY
    max_results = core.config.GOOGLE_SEARCH_MAX_RESULTS or 3

    if not api_key or not cx_key:
        return "[Google] 未配置 API Key 或 CX Key"

    if proxy and not proxy.startswith("http"):
        proxy = f"http://{proxy}"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        async with AsyncClient(proxies=proxy) as cli:
            response = (
                await cli.get(
                    "https://www.googleapis.com/customsearch/v1",
                    headers=headers,
                    params={"key": api_key, "cx": cx_key, "q": keyword},
                )
            ).json()
    except Exception as e:
        core.logger.exception("Google搜索失败")
        return f"[Google] 搜索失败: {e!s}"

    try:
        items = response["items"]
        results = "\n".join([f"[{item['title']}] {item['snippet']} - from: {item['link']}" for item in items[:max_results]])
    except:
        return f"[Google] 未找到关于'{keyword}'的信息"

    _last_keyword = keyword
    _last_call_time = time.time()

    return f"[Google Search Results]\n{results}\nAnalyze and synthesize the above search results to provide insights. DO NOT directly repeat the search results - integrate them into a thoughtful response."


def clean_up():
    """清理扩展"""
    global _last_keyword, _last_call_time
    _last_keyword = None
    _last_call_time = 0
