from fastapi import FastAPI

app = FastAPI(
    title="Sentellent AI Equity Analyst",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Sentellent AI Equity Analyst Backend is Running 🚀"
    }