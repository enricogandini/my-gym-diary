import datetime

from pydantic import BaseModel


class Exercise(BaseModel):
    key: str
    name: str
    description: str | None = None


class SetOfExcercise(BaseModel):
    exercise_key: str
    weight: float
    repetitions: int
    notes: str | None = None


class SessionOfExercise(BaseModel):
    exercise_key: str
    sets: list[SetOfExcercise]


class TrainingSession(BaseModel):
    date: datetime.date
    excercises: list[SessionOfExercise]
