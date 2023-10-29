"""Welcome to Reflex!"""

import reflex as rx


class State(rx.State):
    """The app state"""

    count = 0

    def increment(self):
        self.count += 1


def index() -> rx.Component:
    return rx.vstack(
        rx.heading(State.count),
        rx.button("Increment", on_click=State.increment),
    )


app = rx.App(state=State)
app.add_page(index)
app.compile()
