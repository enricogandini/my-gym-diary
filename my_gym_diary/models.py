import datetime

import reflex as rx
from sqlmodel import Field


class ExerciseType(rx.Model, table=True):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True)
    name: str = Field(unique=True)
    description: str | None = None


class ExerciseEntry(rx.Model, table=True):
    id: int | None = Field(default=None, primary_key=True)
    exercise_type_id: int | None = Field(default=None, foreign_key="exercisetype.id")
    date: datetime.date
    weight: float
    n_repetitions: int
    comment: str | None = None
