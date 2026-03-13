"""每日AI新闻 API"""
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import router as news_router

app = FastAPI(
    title="每日AI新闻 API",
    description="提供每日AI新闻资讯接口，数据来源于 maomu.com",
    version="1.0.0"
)

# 配置 CORS，允许跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(news_router, prefix="/api/news", tags=["News"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "每日AI新闻 API",
        "version": "1.0.0",
        "docs": "/docs"
    }
