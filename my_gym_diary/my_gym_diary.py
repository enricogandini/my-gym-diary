"""Welcome to Reflex!"""

import asyncio

import pydantic
import reflex as rx

from . import models


class State(rx.State):
    """The app state"""

    available_exercises: list[models.Exercise]

    def _get_all_exercises(self):
        with rx.session() as session:
            return session.query(models.Exercise).all()

    def load_exercises(self):
        self.available_exercises = self._get_all_exercises()
        yield State.reload_exercises

    @rx.background
    async def reload_exercises(self):
        while True:
            await asyncio.sleep(1)
            async with self:
                self.available_exercises = self._get_all_exercises()

    @rx.var
    def n_available_exercises(self) -> int:
        return len(self.available_exercises)


def _get_nice_validation_error_message(exc: pydantic.ValidationError) -> str:
    """Get a nice validation message from a pydantic ValidationError"""
    first_error = exc.errors()[0]
    type = first_error["type"]
    original_message = first_error["msg"]
    first_attribute_name = first_error["loc"][0]
    simple_message = f"{first_attribute_name}: {original_message}"
    try:
        match type:
            case "type_error.none.not_allowed" | "value_error.missing":
                return f"{first_attribute_name} cannot be empty"
            case "value_error.str.regex":
                pattern = first_error["ctx"]["pattern"]
                if pattern.startswith(r"^\S"):
                    return f"{first_attribute_name} cannot contain spaces"
                return f"{first_attribute_name} must match pattern {pattern}"
            case "value_error.any_str.min_length":
                return f"{first_attribute_name} must be at least {first_error["ctx"]["limit_value"]} characters long"
            case "value_error.any_str.max_length":
                return f"{first_attribute_name} must be at most {first_error["ctx"]["limit_value"]} characters long"
            case _:
                return simple_message
    except:
        # TODO: log error
        return simple_message


class NewExerciseFormState(State):
    code: str
    name: str

    def _create_exercise(self):
        try:
            exercise = models.ExerciseCreate(
                code=self.code,
                name=self.name,
            )
        except pydantic.ValidationError as exc:
            # TODO: handle properly by showing errors in the form
            # Also move this handling outside of the generic save method,
            # and into the handle_submit method
            print(exc)
            error_message = _get_nice_validation_error_message(exc)
            print(error_message)
        else:
            with rx.session() as session:
                session.add(models.Exercise.validate(exercise))
                session.commit()

    def handle_submit(self, form_data: dict[str, str]):
        self.name: str = form_data["name"]
        self.code: str = form_data["code"]
        self._create_exercise()
        yield rx.set_value("code", "")
        yield rx.set_value("name", "")


def new_exercise_form():
    return rx.vstack(
        rx.form(
            rx.vstack(
                rx.input(placeholder="Code", id="code"),
                rx.input(placeholder="Name", id="name"),
                rx.button("Create Exercise", type_="submit"),
            ),
            on_submit=NewExerciseFormState.handle_submit,
        ),
    )


def available_exercises_display():
    return rx.vstack(
        rx.heading(State.n_available_exercises, " available exercises"),
        rx.foreach(State.available_exercises, render_exercise_type),
        rx.spacer(),
        width="30vw",
        height="100%",
    )


def render_exercise_type(exercise: models.Exercise):
    return rx.hstack(
        rx.text(f"({exercise.code}) {exercise.name}", width="10vw"),
        rx.spacer(),
        border="solid black 1px",
        spcaing="5",
        width="100%",
    )


def index() -> rx.Component:
    return rx.hstack(
        new_exercise_form(),
        rx.spacer(),
        available_exercises_display(),
        rx.spacer(),
    )


app = rx.App(state=State)
app.add_page(index, on_load=State.load_exercises)
app.compile()
