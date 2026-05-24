from fastapi import APIRouter

from app.api.routes import auth, context, grammar, health, learning, speaking, stats, words

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(words.router)
api_router.include_router(context.router)
api_router.include_router(grammar.router)
api_router.include_router(learning.router)
api_router.include_router(speaking.router)
api_router.include_router(stats.router)
