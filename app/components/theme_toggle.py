import reflex as rx
from app.states.auth_state import AuthState


def theme_toggle() -> rx.Component:
    return rx.el.button(
        rx.cond(
            AuthState.theme_mode == "light",
            rx.icon("moon", class_name="h-4 w-4"),
            rx.icon("sun", class_name="h-4 w-4"),
        ),
        on_click=AuthState.toggle_theme,
        class_name="p-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors",
        aria_label="Toggle theme",
    )
