from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.health import router as health_router
from routes.orders import router as orders_router

app = FastAPI(
    title="Pharma Supply Chain AI Agent",
    description="LLM-powered order prioritization for pharmaceutical distribution",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(orders_router)
