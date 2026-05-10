import uvicorn
from fastapi import FastAPI

from src.config import settings
from src.orders.order_router import router as order_router

app = FastAPI(root_path=settings.root_path)
app.include_router(order_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8123)