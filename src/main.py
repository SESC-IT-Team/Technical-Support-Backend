import uvicorn
from fastapi import FastAPI
from src.users.user_router import router as user_router
from src.orders.order_router import router as order_router
app = FastAPI()
app.include_router(user_router)
app.include_router(order_router)
app.include_router()
app.include_router()
app.include_router()

@app.get("/")
async def root(a: int):
    return {"message": a}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
