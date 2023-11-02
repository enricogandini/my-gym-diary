import reflex as rx
from sqlmodel import Field, SQLModel

# To understand the logic of multiple models,
# read: https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/

_regex_no_spaces = r"^\S+$"


class ExerciseBase(SQLModel):
    code: str = Field(unique=True, min_length=1, regex=_regex_no_spaces, max_length=10)
    name: str = Field(unique=True, min_length=1, max_length=50)
    description: str | None = None


class Exercise(rx.Model, ExerciseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseRead(ExerciseBase):
    id: int
