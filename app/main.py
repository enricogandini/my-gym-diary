import fastapi
from models import Exercise

app = fastapi.FastAPI()


@app.get("/")
def hello() -> dict[str, str]:
    result = {"message": "Hello, World!"}
    return result


@app.get("/exercises")
def get_exercises() -> list[Exercise]:
    """Get all the available exercises"""
    return [
        Exercise(key="BP", name="Bench Press"),
        Exercise(key="DL", name="Deadlift"),
        Exercise(key="SQ", name="Squat"),
        Exercise(key="VP", name="Vertical Press"),
        Exercise(key="BC", name="Biceps Curl"),
    ]
