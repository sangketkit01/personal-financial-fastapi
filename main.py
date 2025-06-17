from fastapi import FastAPI
from routes import user, financial

app = FastAPI()

app.include_router(user.user_router)
app.include_router(financial.financial_router)