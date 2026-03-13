# AI 新闻 API 接口文档

**Base URL**: `https://web-production-82de.up.railway.app`

---

## 1. 每日 AI 新闻

获取每日 AI 新闻列表

**请求**
```
GET /api/news/ai-daily
```

**响应示例**
```json
{
  "success": true,
  "data": {
    "date": "2026-03-13",
    "title": "每日AI资讯",
    "subtitle": "聚焦AI行业最新动态",
    "news": [
      {
        "time": "03-13 12:00",
        "title": "英伟达黄仁勋：没有 GeForce，就没有 AI",
        "summary": "...",
        "source": "IT家人工智能",
        "url": "https://...",
        "category": "行业动态"
      }
    ],
    "hot_topics": [...]
  }
}
```

---

## 2. 新闻列表（分页）

支持分类筛选和分页

**请求**
```
GET /api/news/list?category=全部&page=1&page_size=10
```

**参数**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| category | string | 全部 | 分类：全部、行业动态、产品发布、技术前沿、政策法规 |
| page | int | 1 | 页码 |
| page_size | int | 10 | 每页数量，最大50 |

**响应**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "page": 1,
    "page_size": 10,
    "total": 30,
    "total_pages": 3
  }
}
```

---

## 3. 分类统计

获取各分类的新闻数量

**请求**
```
GET /api/news/categories
```

**响应**
```json
{
  "success": true,
  "data": [
    {"category": "技术前沿", "count": 12},
    {"category": "行业动态", "count": 8},
    {"category": "产品发布", "count": 6},
    {"category": "政策法规", "count": 4}
  ]
}
```

---

## 4. 热点话题

获取热点话题列表

**请求**
```
GET /api/news/hot-topics
```

---

## 5. 健康检查

**请求**
```
GET /api/news/health
```

**响应**
```json
{"status": "ok"}
```
