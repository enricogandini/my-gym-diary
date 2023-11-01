import datetime

import reflex as rx
from sqlmodel import Field


class Exercise(rx.Model):
    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(unique=True)
    name: str = Field(unique=True)
    description: str | None = None


class SetOfExercise(rx.Model):
    exercise_id: int = Field(foreign_key="exercise.id")
    weight: float
    n_repetitions: int
    notes: str | None = None

    @property
    def volume(self) -> float:
        return self.weight * self.n_repetitions


class SessionOfExercise(rx.Model):
    exercise_id: int = Field(foreign_key="exercise.id")
    sets: list[SetOfExercise]

    @property
    def n_sets(self) -> int:
        return len(self.sets)

    @property
    def volume(self) -> float:
        return sum(set.volume for set in self.sets)

    @property
    def n_repetitions(self) -> int:
        return sum(set.n_repetitions for set in self.sets)


class TrainingSession(rx.Model):
    date: datetime.date
    exercise_sessions: list[SessionOfExercise]

    @property
    def n_excercises(self) -> int:
        return len(self.exercise_sessions)


def create_exercise(name: str, key: str):
    """Create an exercise"""
    with rx.session() as session:
        exercise = Exercise(name=name, code=key)
        session.add(exercise)
        session.commit()
        print("added exercise")


def add_set_to_session(exercise_id: int, weight: float, n_repetitions: int):
    """Add a set to a session"""
    with rx.session() as session:
        set = SetOfExercise(
            exercise_id=exercise_id, weight=weight, n_repetitions=n_repetitions
        )
        session.add(set)
        session.commit()


def add_session_to_training(
    training_date: datetime.date, exercise_id: int, sets: list[SetOfExercise]
):
    """Add an exercise session to a training session"""
    with rx.session() as session:
        session_obj = SessionOfExercise(exercise_id=exercise_id, sets=sets)
        training_session = TrainingSession(
            date=training_date, exercise_sessions=[session_obj]
        )
        session.add(training_session)
        session.commit()


# Example usage
if __name__ == "__main__":
    create_exercise(name="Bench Press", key="BP")
    add_set_to_session(exercise_id=1, weight=100.0, n_repetitions=10)
    add_set_to_session(exercise_id=1, weight=110.0, n_repetitions=8)
    add_session_to_training(
        datetime.date(2023, 11, 1),
        exercise_id=1,
        sets=[SetOfExercise(exercise_id=1, weight=100.0, n_repetitions=10)],
    )

    # Calculate and print the volume of a set and session
    with rx.session() as session:
        set = session.query(SetOfExercise).first()
        session_obj = session.query(SessionOfExercise).first()
        print(f"Set Volume: {set.volume}")
        print(f"Session Volume: {session_obj.volume}")
