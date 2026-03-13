from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.model import (
    NewsResponse,
    NewsItemResponse,
    PaginatedNewsResponse,
    CategoryResponse,
    NewsItem,
)
from app.service import fetch_ai_news

router = APIRouter()


@router.get("/ai-daily", response_model=NewsResponse)
async def get_ai_daily_news():
    """
    获取每日AI新闻

    返回格式:
    - success: 请求是否成功
    - data: 新闻数据（日期、标题、新闻列表、热点话题）
    - message: 错误信息（如果有）
    """
    news_data = await fetch_ai_news()

    if news_data is None:
        return NewsResponse(
            success=False,
            data=None,
            message="Failed to fetch news data"
        )

    return NewsResponse(
        success=True,
        data=news_data,
        message=None
    )


@router.get("/list", response_model=PaginatedNewsResponse)
async def get_news_list(
    category: str = Query("全部", description="新闻分类筛选：全部、行业动态、产品发布、技术前沿、政策法规"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量")
):
    """
    获取新闻列表（支持分页和分类筛选）

    Args:
        category: 分类名称（全部、行业动态、产品发布、技术前沿、政策法规）
        page: 页码，从1开始
        page_size: 每页数量，最大50

    Returns:
        分页后的新闻列表
    """
    news_data = await fetch_ai_news()

    if news_data is None:
        return PaginatedNewsResponse(
            success=False,
            data=None,
            message="Failed to fetch news data"
        )

    # 获取所有新闻
    all_news = news_data.news

    # 分类筛选（使用NewsItem中的category字段）
    if category and category != "全部":
        filtered_news = [item for item in all_news if item.category == category]
        all_news = filtered_news

    # 分页
    total = len(all_news)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_items = all_news[start_idx:end_idx]

    # 转换为字典列表
    items = [item.model_dump() for item in page_items]

    return PaginatedNewsResponse(
        success=True,
        data={
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
        message=None
    )


@router.get("/categories", response_model=CategoryResponse)
async def get_categories():
    """
    获取新闻分类及每个分类的新闻数量

    Returns:
        分类列表及数量统计
    """
    news_data = await fetch_ai_news()

    if news_data is None:
        return CategoryResponse(
            success=False,
            data=None,
            message="Failed to fetch news data"
        )

    # 统计每个分类的数量（使用NewsItem中的category字段）
    category_counts = {}
    for item in news_data.news:
        cat = item.category or "全部"
        category_counts[cat] = category_counts.get(cat, 0) + 1

    # 转换为响应格式
    categories = [
        {"category": cat, "count": cnt}
        for cat, cnt in category_counts.items()
    ]

    # 按数量排序
    categories.sort(key=lambda x: x["count"], reverse=True)

    return CategoryResponse(
        success=True,
        data=categories,
        message=None
    )


@router.get("/detail/{news_index}", response_model=NewsItemResponse)
async def get_news_detail(news_index: int):
    """
    获取新闻详情

    Args:
        news_index: 新闻索引（从0开始）

    Returns:
        单条新闻详情
    """
    news_data = await fetch_ai_news()

    if news_data is None:
        return NewsItemResponse(
            success=False,
            data=None,
            message="Failed to fetch news data"
        )

    # 检查索引范围
    if news_index < 0 or news_index >= len(news_data.news):
        return NewsItemResponse(
            success=False,
            data=None,
            message=f"News not found, index out of range (0-{len(news_data.news) - 1})"
        )

    return NewsItemResponse(
        success=True,
        data=news_data.news[news_index],
        message=None
    )


@router.get("/hot-topics", response_model=NewsResponse)
async def get_hot_topics():
    """
    获取热点话题

    Returns:
        热点话题列表
    """
    news_data = await fetch_ai_news()

    if news_data is None:
        return NewsResponse(
            success=False,
            data=None,
            message="Failed to fetch news data"
        )

    # 只返回热点话题
    from app.model import NewsData
    return NewsResponse(
        success=True,
        data=NewsData(
            date=news_data.date,
            title="热点话题",
            subtitle="本周最热门的AI话题",
            news=[],
            hot_topics=news_data.hot_topics
        ),
        message=None
    )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}
