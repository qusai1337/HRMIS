from fastapi import FastAPI
from routes import cases
from routes import reports
from routes import victims
app = FastAPI()

app.include_router(cases.router)
app.include_router(reports.router)

app.include_router(victims.router)
