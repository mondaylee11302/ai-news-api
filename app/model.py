from typing import List, Optional
from pydantic import BaseModel


class NewsItem(BaseModel):
    """单条新闻"""
    time: str
    title: str
    summary: str
    source: str
    url: str
    category: Optional[str] = "全部"  # 分类：全部、行业动态、产品发布、技术前沿、政策法规


class HotTopic(BaseModel):
    """热点话题"""
    title: str
    time_ago: str
    url: str


class NewsData(BaseModel):
    """新闻数据"""
    date: str
    title: str
    subtitle: str
    news: List[NewsItem]
    hot_topics: List[HotTopic]


class NewsResponse(BaseModel):
    """API响应"""
    success: bool
    data: Optional[NewsData] = None
    message: Optional[str] = None


class NewsItemResponse(BaseModel):
    """单条新闻响应"""
    success: bool
    data: Optional[NewsItem] = None
    message: Optional[str] = None


class PaginatedNewsResponse(BaseModel):
    """分页新闻响应"""
    success: bool
    data: Optional[dict] = None  # 包含 items, page, page_size, total, total_pages
    message: Optional[str] = None


class CategoryResponse(BaseModel):
    """分类响应"""
    success: bool
    data: Optional[List[dict]] = None  # 包含 category, count
    message: Optional[str] = None
