import fastapi

app = fastapi.FastAPI()


@app.get("/")
def hello() -> dict[str, str]:
    result = {"message": "Hello, World!"}
    return result
