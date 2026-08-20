import reflex as rx
from app.states.auth_state import AuthState


def text_field(
    label: str,
    placeholder: str,
    value: rx.Var,
    on_change,
    type_: str = "text",
    icon: str = "",
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            class_name="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5",
        ),
        rx.el.div(
            rx.cond(
                icon != "",
                rx.el.div(
                    rx.icon(icon, class_name="h-4 w-4 text-gray-400"),
                    class_name="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none",
                ),
                rx.fragment(),
            ),
            rx.el.input(
                placeholder=placeholder,
                default_value=value,
                type=type_,
                on_change=on_change.debounce(200),
                class_name=rx.cond(
                    icon != "",
                    "w-full pl-10 pr-3 py-2.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm",
                    "w-full px-3 py-2.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm",
                ),
            ),
            class_name="relative",
        ),
        class_name="mb-4",
    )


def error_banner() -> rx.Component:
    return rx.cond(
        AuthState.error_message != "",
        rx.el.div(
            rx.icon(
                "triangle-alert",
                class_name="h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0",
            ),
            rx.el.p(
                AuthState.error_message,
                class_name="text-sm text-red-700 dark:text-red-300",
            ),
            class_name="flex items-start gap-2 p-3 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 rounded-xl mb-4",
        ),
        rx.fragment(),
    )


def success_banner() -> rx.Component:
    return rx.cond(
        AuthState.success_message != "",
        rx.el.div(
            rx.icon(
                "circle-check",
                class_name="h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0",
            ),
            rx.el.p(
                AuthState.success_message,
                class_name="text-sm text-green-700 dark:text-green-300",
            ),
            class_name="flex items-start gap-2 p-3 bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-900 rounded-xl mb-4",
        ),
        rx.fragment(),
    )


def primary_button(text: str, on_click, icon: str = "") -> rx.Component:
    return rx.el.button(
        rx.cond(
            AuthState.is_loading,
            rx.el.div(
                rx.el.div(
                    class_name="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin"
                ),
                rx.el.span(
                    "Please wait...", class_name="text-sm font-semibold"
                ),
                class_name="flex items-center justify-center gap-2",
            ),
            rx.el.div(
                rx.cond(
                    icon != "",
                    rx.icon(icon, class_name="h-4 w-4"),
                    rx.fragment(),
                ),
                rx.el.span(text, class_name="text-sm font-semibold"),
                class_name="flex items-center justify-center gap-2",
            ),
        ),
        on_click=on_click,
        disabled=AuthState.is_loading,
        type="button",
        class_name="w-full py-3 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 disabled:cursor-not-allowed text-white rounded-xl transition-colors",
    )
