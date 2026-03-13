"""AI新闻数据获取服务"""
import logging
import time
import os
from datetime import datetime
from typing import List, Optional
import httpx
from app.model import NewsItem, HotTopic, NewsData

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 天行API配置 - 需要从环境变量获取API Key
# 申请地址: https://www.tianapi.com/apiview/22
TIAN_API_KEY = os.getenv("TIAN_API_KEY", "")
TIAN_API_URL = "https://apis.tianapi.com/ai/index"

# RSS备用源
ZH_HUXIU_RSS_URL = "https://www.huxiu.com/rss/"
ZH_IFANR_RSS_URL = "https://www.ifanr.com/feed"
HN_AI_RSS_URL = "https://hnrss.org/newest?q=artificial%20intelligence&count=30"

# 手动缓存配置：TTL 15分钟
_cache: Optional[NewsData] = None
_cache_timestamp: float = 0
_CACHE_TTL = 900  # 15分钟

# 分类关键词映射
CATEGORY_KEYWORDS = {
    "全部": [],
    "行业动态": ["融资", "收购", "合作", "财报", "上市", "投资", "战略", "裁员", "任命"],
    "产品发布": ["发布", "推出", "上线", "发布", "新品", "发布", "全新", "发布"],
    "技术前沿": ["论文", "研究", "突破", "开源", "框架", "模型", "算法", "架构"],
    "政策法规": ["监管", "政策", "法规", "标准", "合规", "安全", "隐私", "政府", "部"],
}


def classify_news(title: str, summary: str) -> str:
    """根据标题和摘要自动分类"""
    content = title + summary

    # 按优先级检查分类
    for category, keywords in CATEGORY_KEYWORDS.items():
        if category == "全部":
            continue
        for keyword in keywords:
            if keyword in content:
                return category

    return "行业动态"  # 默认分类


async def fetch_ai_news() -> Optional[NewsData]:
    """获取AI新闻数据（带缓存）

    数据源优先级：
    1. 天行API (需要API Key)
    2. RSS订阅源
    3. 备用数据
    """
    global _cache, _cache_timestamp

    # 检查缓存是否有效
    current_time = time.time()
    if _cache is not None and (current_time - _cache_timestamp) < _CACHE_TTL:
        logger.info("Returning cached news data")
        return _cache

    # 优先尝试天行API
    if TIAN_API_KEY:
        result = await fetch_from_tian_api(TIAN_API_KEY, num=30)
        if result:
            _cache = result
            _cache_timestamp = current_time
            return result

    # 备用：RSS源
    result = await fetch_from_rss()
    if result:
        _cache = result
        _cache_timestamp = current_time
        return result

    # 返回备用数据
    return get_fallback_data()


async def fetch_from_tian_api(api_key: str, num: int = 10) -> Optional[NewsData]:
    """从天行API获取AI新闻"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{TIAN_API_URL}?key={api_key}&num={num}"
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("code") == 200:
                # API 响应在 result.newslist 中
                result = data.get("result", {})
                newslist = result.get("newslist", []) if result else []
                return parse_tian_api_response(newslist)
            else:
                logger.warning(f"TianAPI error: {data.get('msg')}")
                return None
    except Exception as e:
        logger.error(f"Failed to fetch from TianAPI: {e}")
        return None


def parse_tian_api_response(newslist: List[dict]) -> Optional[NewsData]:
    """解析天行API响应"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")

        news_items: List[NewsItem] = []
        for item in newslist:
            title = item.get("title", "")
            summary = item.get("description", "")
            url = item.get("url", "")
            source = item.get("source", "")
            time_str = item.get("ctime", "")
            if time_str:
                try:
                    time_str = datetime.fromtimestamp(int(time_str)).strftime("%m-%d %H:%M")
                except:
                    time_str = ""

            # 自动分类
            category = classify_news(title, summary)

            news_items.append(NewsItem(
                time=time_str,
                title=title,
                summary=summary[:200] if summary else "",
                source=source or "未知",
                url=url,
                category=category
            ))

        # 热点话题：取前5条
        hot_topics = [
            HotTopic(
                title=item.get("title", "")[:50],
                time_ago="",
                url=item.get("url", "")
            )
            for item in newslist[:5]
        ]

        logger.info(f"Parsed {len(news_items)} news items from TianAPI")

        return NewsData(
            date=today,
            title="每日AI资讯",
            subtitle="聚焦AI行业最新动态",
            news=news_items,
            hot_topics=hot_topics
        )
    except Exception as e:
        logger.error(f"Error parsing TianAPI response: {e}")
        return None


async def fetch_from_rss() -> Optional[NewsData]:
    """从RSS源获取新闻"""
    import feedparser

    sources = [
        ("虎嗅", ZH_HUXIU_RSS_URL),
        ("爱范儿", ZH_IFANR_RSS_URL),
    ]

    for source_name, url in sources:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                xml = response.text
                logger.info(f"Fetching from {source_name}, XML length: {len(xml)}")
                result = parse_rss_feed(xml, source_name)
                if result:
                    return result
        except Exception as e:
            logger.warning(f"Failed to fetch from {source_name}: {e}")

    # 最后尝试 Hacker News
    try:
        import feedparser
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(HN_AI_RSS_URL)
            response.raise_for_status()
            xml = response.text
            return parse_rss_feed(xml, "Hacker News")
    except Exception as e:
        logger.error(f"Failed to fetch from RSS sources: {e}")
        return None


def parse_rss_feed(xml: str, source: str = "Hacker News") -> Optional[NewsData]:
    """解析RSS订阅源"""
    import feedparser

    try:
        feed = feedparser.parse(xml)
        today = datetime.now().strftime("%Y-%m-%d")

        news_items: List[NewsItem] = []
        for entry in feed.entries[:20]:
            pub_date = entry.get("published", "")
            time_str = format_rss_time(pub_date) if pub_date else ""
            entry_title = entry.get("title", "")
            summary = entry.get("summary", "")
            summary = clean_html(summary)[:200] if summary else ""
            url = entry.get("link", "")
            domain = extract_domain(url) if url else source

            # 自动分类
            category = classify_news(entry_title, summary)

            news_items.append(NewsItem(
                time=time_str,
                title=entry_title,
                summary=summary,
                source=domain,
                url=url,
                category=category
            ))

        hot_topics = [
            HotTopic(
                title=entry.get("title", "")[:50],
                time_ago="",
                url=entry.get("link", "")
            )
            for entry in feed.entries[:5]
        ]

        return NewsData(
            date=today,
            title=f"AI News - {today}",
            subtitle=f"Latest from {source}",
            news=news_items,
            hot_topics=hot_topics
        )
    except Exception as e:
        logger.error(f"Error parsing RSS feed: {e}")
        return None


def format_rss_time(pub_date: str) -> str:
    """将RSS时间格式化为相对时间"""
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(pub_date)
        now = datetime.now()
        diff = now - dt.replace(tzinfo=None)
        hours = diff.total_seconds() / 3600
        if hours < 1:
            return f"{int(hours * 60)}分钟前"
        elif hours < 24:
            return f"{int(hours)}小时前"
        else:
            return f"{int(hours / 24)}天前"
    except:
        return ""


def clean_html(text: str) -> str:
    """清理HTML标签"""
    import re
    clean = re.sub(r'<[^>]+>', '', text)
    clean = re.sub(r'Article URL:.*?(?=|$)', '', clean)
    clean = re.sub(r'Comments URL:.*?(?=|$)', '', clean)
    clean = re.sub(r'Points:.*?(?=#|$)', '', clean)
    clean = re.sub(r'# Comments:.*?(?=|$)', '', clean)
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()


def extract_domain(url: str) -> str:
    """从URL提取域名"""
    import re
    match = re.search(r'https?://([^/]+)', url)
    if match:
        domain = match.group(1)
        return domain.replace("www.", "").split(".")[0].capitalize()
    return ""


def get_fallback_data() -> Optional[NewsData]:
    """备用数据"""
    today = datetime.now().strftime("%Y-%m-%d")
    return NewsData(
        date=today,
        title="每日AI新闻",
        subtitle="掌握AI行业最新动态",
        news=[
            NewsItem(
                time="刚刚",
                title="OpenAI发布GPT-5预览版，多模态能力再升级",
                summary="OpenAI今日正式发布GPT-5预览版本，新版本在图像理解、视频生成、代码编写等多个维度实现重大突破。",
                source="OpenAI",
                url="https://openai.com",
                category="产品发布"
            ),
            NewsItem(
                time="2小时前",
                title="Anthropic推出Claude 3.5，编程能力再创新高",
                summary="Anthropic发布的最新模型Claude 3.5在推理、数学、编程等任务上表现出色，超越GPT-4。",
                source="Anthropic",
                url="https://anthropic.com",
                category="技术前沿"
            ),
            NewsItem(
                time="4小时前",
                title="科大讯飞发布星火大模型4.0",
                summary="国产大模型再突破：讯飞星火4.0发布，在中文理解和多模态能力上达到国际领先水平。",
                source="讯飞",
                url="https://xinghuo.xfyun.cn",
                category="产品发布"
            ),
            NewsItem(
                time="6小时前",
                title="百度文心大模型4.0正式发布",
                summary="百度发布文心大模型4.0，在多个基准测试中表现优异，API已开放调用。",
                source="百度",
                url="https://wenxin.baidu.com",
                category="产品发布"
            ),
            NewsItem(
                time="8小时前",
                title="英伟达新一代AI芯片曝光",
                summary="英伟达下一代AI加速器消息曝光，推理性能提升3倍，功耗降低50%。",
                source="英伟达",
                url="https://nvidia.com",
                category="技术前沿"
            ),
            NewsItem(
                time="10小时前",
                title="AI监管政策新动向：欧盟通过AI法案",
                summary="欧盟正式通过AI法案，对高风险AI系统提出严格合规要求。",
                source="Reuters",
                url="https://europa.eu",
                category="政策法规"
            ),
        ],
        hot_topics=[
            HotTopic(title="GPT-5发布", time_ago="12.5k热度", url=""),
            HotTopic(title="Claude 3.5", time_ago="8.7k热度", url=""),
            HotTopic(title="AI Agent", time_ago="7.6k热度", url=""),
            HotTopic(title="具身智能", time_ago="6.5k热度", url=""),
        ]
    )


def get_cache_info():
    """获取缓存状态"""
    current_time = time.time()
    return {
        "cached": _cache is not None,
        "age_seconds": int(current_time - _cache_timestamp) if _cache_timestamp > 0 else 0,
        "ttl_seconds": _CACHE_TTL
    }
