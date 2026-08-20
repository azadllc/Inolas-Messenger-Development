import reflex as rx
from app.states.messenger_state import MessengerState


def avatar(seed: rx.Var | str, size: str = "h-10 w-10") -> rx.Component:
    seed_var = str(rx.Var.create(seed))
    initial = seed_var.upper()[0:1]
    return rx.el.div(
        rx.el.span(
            initial,
            class_name="text-white font-semibold text-sm select-none",
        ),
        class_name=f"{size} rounded-full flex items-center justify-center shrink-0 bg-indigo-500",
    )


def toast() -> rx.Component:
    return rx.cond(
        MessengerState.toast_message != "",
        rx.el.div(
            rx.icon("check", class_name="h-4 w-4 text-white"),
            rx.el.p(
                MessengerState.toast_message,
                class_name="text-sm font-medium text-white",
            ),
            rx.el.button(
                rx.icon("x", class_name="h-3.5 w-3.5"),
                on_click=MessengerState.dismiss_toast,
                class_name="ml-2 text-white/70 hover:text-white",
            ),
            class_name="fixed bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-2 px-4 py-2.5 bg-gray-900 dark:bg-gray-800 rounded-full shadow-lg z-50",
        ),
        rx.fragment(),
    )
