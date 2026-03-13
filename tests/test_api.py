"""测试每日AI新闻API"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """测试健康检查接口"""
    response = client.get("/api/news/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ai_daily_news_success():
    """测试获取每日AI新闻"""
    response = client.get("/api/news/ai-daily")
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["data"] is not None
    assert "date" in data["data"]
    assert "title" in data["data"]
    assert "subtitle" in data["data"]
    assert "news" in data["data"]
    assert "hot_topics" in data["data"]


def test_ai_daily_news_fields():
    """测试新闻字段完整性"""
    # 清除缓存后测试
    from app.service import clear_cache
    clear_cache()

    response = client.get("/api/news/ai-daily")
    data = response.json()

    # 检查新闻列表
    news = data["data"]["news"]
    if news:
        news_item = news[0]
        assert "time" in news_item
        assert "title" in news_item
        assert "summary" in news_item
        assert "source" in news_item
        assert "url" in news_item


def test_root():
    """测试根路径"""
    response = client.get("/")
    assert response.status_code == 200
    assert "name" in response.json()
