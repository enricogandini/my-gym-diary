"""Welcome to Reflex!"""

import reflex as rx

import models


class AddExercise(rx.State):
    """The app state"""

    name: str
    key: str

    def add_exercise(self, name: str, key: str):
        self.name = name
        self.key = key


def index() -> rx.Component:
    return rx.vstack(
        rx.heading(State.count),
        rx.button("Increment", on_click=State.increment),
    )


app = rx.App(state=State)
app.add_page(index)
app.compile()
