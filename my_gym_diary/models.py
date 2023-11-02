import reflex as rx
from sqlmodel import Field, SQLModel

# To understand the logic of multiple models,
# read: https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/


class ExerciseBase(SQLModel):
    code: str = Field(unique=True)
    name: str = Field(unique=True)
    description: str | None = None


class Exercise(rx.Model, ExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseRead(ExerciseBase):
    id: int
