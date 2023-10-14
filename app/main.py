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
    # TODO: Get exercises from database
    return [
        Exercise(key="BP", name="Bench Press"),
        Exercise(key="DL", name="Deadlift"),
        Exercise(key="SQ", name="Squat"),
        Exercise(key="VP", name="Vertical Press"),
        Exercise(key="BC", name="Biceps Curl"),
    ]


@app.post("/exercises")
def create_exercise(exercise: Exercise) -> Exercise:
    """Create a new exercise"""
    # TODO: Check that no exercise with same key or name exists,
    # then add the exercise to the database
    return exercise


@app.get("/exercises/{exercise_key}")
def get_exercise(exercise_key: str) -> Exercise:
    """Get a specific exercise"""
    # TODO: Get exercise from database
    return Exercise(key=exercise_key, name="Sample Exercise")


@app.put("/exercises/{exercise_key}")
def update_exercise(exercise_key: str, exercise: Exercise) -> Exercise:
    """Update a specific exercise"""
    # TODO: Check that the exercise with exercise_key exists in the database.
    # Check that no exercise with same key or name as new exercise exists,
    # then update the exercise in the database
    return exercise


@app.delete("/exercises/{exercise_key}")
def delete_exercise(exercise_key: str) -> dict[str, str]:
    """Delete a specific exercise"""
    # TODO: Check that the exercise with exercise_key exists in the database.
    # Then delete the exercise from the database.
    return {"message": f"Exercise {exercise_key} deleted"}
