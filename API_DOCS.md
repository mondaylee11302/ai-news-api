# 每日AI新闻 API 接口文档

## 概述

本文档描述了每日AI新闻后端API的接口规范，供前端开发团队进行联调使用。

**基础URL**: `http://localhost:8005` (本地部署)
**前缀**: `/api/news`

---

## 接口列表

### 1. 获取每日AI新闻 (ai-daily)

获取最新的AI/科技新闻列表。

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
    "title": "AI News - 2026-03-13",
    "subtitle": "Latest from 爱范儿",
    "news": [
      {
        "time": "11小时前",
        "title": "2026 年第一个「机皇」，粉丝先买｜三星 S26 Ultra 评测",
        "summary": "不知道，我的屏幕很曼妙...",
        "source": "Ifanr",
        "url": "https://www.ifanr.com/1657983",
        "category": "行业动态"
      }
    ],
    "hot_topics": [
      {
        "title": "2026 年第一个「机皇」，粉丝先买｜三星 S26 Ultra 评测",
        "time_ago": "",
        "url": "https://www.ifanr.com/1657983"
      }
    ]
  },
  "message": null
}
```

**字段说明**
| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| data.date | string | 日期 (YYYY-MM-DD) |
| data.title | string | 页面标题 |
| data.subtitle | string | 副标题/来源说明 |
| data.news | array | 新闻列表 |
| data.news[].time | string | 发布时间（如"11小时前"） |
| data.news[].title | string | 新闻标题 |
| data.news[].summary | string | 新闻摘要 |
| data.news[].source | string | 来源（如"爱范儿"） |
| data.news[].url | string | 原文链接 |
| data.news[].category | string | 分类（行业动态/产品发布/技术前沿/政策法规） |
| data.hot_topics | array | 热点话题列表 |
| message | string | 错误信息（成功时为null） |

---

### 2. 获取新闻列表 (分页)

支持分页和分类筛选的新闻列表接口。

**请求**
```
GET /api/news/list?page=1&page_size=10&category=行业动态
```

**参数说明**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认10，最大50 |
| category | string | 否 | 分类筛选（见下方可选值） |

**分类可选值**
- `全部` - 所有新闻
- `行业动态` - 企业融资、收购、合作等
- `产品发布` - 新品发布、上线等
- `技术前沿` - 论文、研究、突破等
- `政策法规` - 监管、政策、法规等

**响应示例**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "time": "11小时前",
        "title": "新闻标题",
        "summary": "新闻摘要",
        "source": "爱范儿",
        "url": "https://...",
        "category": "行业动态"
      }
    ],
    "page": 1,
    "page_size": 10,
    "total": 20,
    "total_pages": 2
  },
  "message": null
}
```

---

### 3. 获取新闻分类

获取所有可用的新闻分类及每个分类的新闻数量。

**请求**
```
GET /api/news/categories
```

**响应示例**
```json
{
  "success": true,
  "data": [
    {"category": "行业动态", "count": 15},
    {"category": "产品发布", "count": 3},
    {"category": "技术前沿", "count": 1},
    {"category": "政策法规", "count": 1}
  ],
  "message": null
}
```

---

### 4. 获取热点话题

获取当前的热点话题列表。

**请求**
```
GET /api/news/hot-topics
```

**响应示例**
```json
{
  "success": true,
  "data": {
    "date": "2026-03-13",
    "title": "热点话题",
    "subtitle": "本周最热门的AI话题",
    "news": [],
    "hot_topics": [
      {"title": "GPT-5发布", "time_ago": "12.5k热度", "url": ""},
      {"title": "Claude 3.5", "time_ago": "8.7k热度", "url": ""}
    ]
  },
  "message": null
}
```

---

### 5. 获取新闻详情

根据索引获取单条新闻的详情。

**请求**
```
GET /api/news/detail/0
```

**参数说明**
| 参数 | 类型 | 说明 |
|------|------|------|
| news_index | int | 新闻索引（从0开始） |

**响应示例**
```json
{
  "success": true,
  "data": {
    "time": "11小时前",
    "title": "2026 年第一个「机皇」，粉丝先买｜三星 S26 Ultra 评测",
    "summary": "不知道，我的屏幕很曼妙...",
    "source": "Ifanr",
    "url": "https://www.ifanr.com/1657983",
    "category": "行业动态"
  },
  "message": null
}
```

---

### 6. 健康检查

检查API服务是否正常运行。

**请求**
```
GET /api/news/health
```

**响应示例**
```json
{
  "status": "ok"
}
```

---

## 数据源说明

当前API使用以下数据源（按优先级）：

1. **天行API** (需要配置 `TIAN_API_KEY` 环境变量)
   - 地址: https://www.tianapi.com/apiview/22
   - 免费额度: 注册送100次/天

2. **RSS订阅源** (免费，无需配置)
   - 爱范儿 (ifanr.com) - 中文科技新闻
   - 虎嗅 (huxiu.com) - 中文科技新闻
   - Hacker News (hnrss.org) - AI新闻

3. **备用数据** - 当所有数据源失败时返回

**缓存策略**: 数据15分钟更新一次

---

## 前端集成示例

### JavaScript/Fetch
```javascript
// 获取每日新闻
async function fetchNews() {
  const response = await fetch('http://localhost:8005/api/news/ai-daily');
  const data = await response.json();
  if (data.success) {
    console.log(data.data.news);
  }
}

// 获取分页列表
async function fetchNewsList(page = 1, category = '') {
  const params = new URLSearchParams({ page, page_size: 10 });
  if (category) params.append('category', category);

  const response = await fetch(`http://localhost:8005/api/news/list?${params}`);
  const data = await response.json();
  return data.data;
}
```

### Vue/React
```javascript
// Vue 3 Composition API
import { ref, onMounted } from 'vue';

export default {
  setup() {
    const news = ref([]);
    const loading = ref(false);

    const fetchNews = async () => {
      loading.value = true;
      try {
        const res = await fetch('http://localhost:8005/api/news/ai-daily');
        const data = await res.json();
        if (data.success) {
          news.value = data.data.news;
        }
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchNews);

    return { news, loading, fetchNews };
  }
};
```

---

## 错误处理

所有接口在出错时返回以下格式：

```json
{
  "success": false,
  "data": null,
  "message": "错误描述信息"
}
```

常见错误：
- `Failed to fetch news data` - 数据源获取失败
- `News not found, index out of range` - 新闻索引超出范围

---

## 部署说明

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **配置环境变量（可选）**
```bash
export TIAN_API_KEY="your_api_key_here"
```

3. **启动服务**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

4. **访问API文档**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
