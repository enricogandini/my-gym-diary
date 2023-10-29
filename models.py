import datetime

from pydantic import BaseModel


class Exercise(BaseModel):
    key: str
    name: str
    description: str | None = None


class SetOfExcercise(BaseModel):
    weight: float
    n_repetitions: int
    notes: str | None = None

    @property
    def volume(self) -> float:
        return self.weight * self.n_repetitions


class SessionOfExercise(BaseModel):
    exercise_key: str
    sets: list[SetOfExcercise]

    @property
    def n_sets(self) -> int:
        return len(self.sets)

    @property
    def volume(self) -> float:
        return sum(set.volume for set in self.sets)

    @property
    def n_repetitions(self) -> int:
        return sum(set.n_repetitions for set in self.sets)


class TrainingSession(BaseModel):
    date: datetime.date
    excercises: list[SessionOfExercise]

    @property
    def n_excercises(self) -> int:
        return len(self.excercises)
