import reflex as rx
from app.states.auth_state import AuthState
from app.components.theme_toggle import theme_toggle


def brand_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("message-circle", class_name="h-6 w-6 text-white"),
                    class_name="h-11 w-11 rounded-2xl bg-indigo-600 flex items-center justify-center",
                ),
                rx.el.span(
                    "Inolas",
                    class_name="text-2xl font-bold text-gray-900 dark:text-white tracking-tight",
                ),
                class_name="flex items-center gap-3 mb-10",
            ),
            rx.el.h1(
                "Messaging that feels effortless.",
                class_name="text-4xl xl:text-5xl font-bold text-gray-900 dark:text-white leading-tight tracking-tight mb-4",
            ),
            rx.el.p(
                "Sign in to sync chats, share media, and stay connected across every device.",
                class_name="text-lg text-gray-600 dark:text-gray-400 mb-10 max-w-md",
            ),
            rx.el.div(
                feature_item("shield-check", "End-to-end privacy controls"),
                feature_item("zap", "Real-time messages and typing"),
                feature_item("users", "Group chats up to 500 members"),
                feature_item("smartphone", "Available on all your devices"),
                class_name="flex flex-col gap-4",
            ),
            class_name="max-w-md",
        ),
        class_name="hidden lg:flex flex-col justify-center px-16 py-12 bg-gray-50 dark:bg-gray-900 border-r border-gray-200 dark:border-gray-800 w-1/2",
    )


def feature_item(icon: str, text: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                icon, class_name="h-4 w-4 text-indigo-600 dark:text-indigo-400"
            ),
            class_name="h-8 w-8 rounded-lg bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center flex-shrink-0",
        ),
        rx.el.span(
            text,
            class_name="text-sm font-medium text-gray-700 dark:text-gray-300",
        ),
        class_name="flex items-center gap-3",
    )


def auth_layout(content: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            brand_panel(),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "message-circle",
                                class_name="h-5 w-5 text-white",
                            ),
                            class_name="h-9 w-9 rounded-xl bg-indigo-600 flex items-center justify-center lg:hidden",
                        ),
                        rx.el.span(
                            "Inolas",
                            class_name="text-lg font-bold text-gray-900 dark:text-white lg:hidden",
                        ),
                        class_name="flex items-center gap-2",
                    ),
                    theme_toggle(),
                    class_name="flex items-center justify-between mb-8 lg:justify-end",
                ),
                content,
                class_name="w-full max-w-md",
            ),
            class_name="flex-1 flex items-center justify-center px-6 py-12 lg:px-12",
        ),
        class_name=rx.cond(
            AuthState.theme_mode == "dark",
            "dark min-h-screen bg-white dark:bg-black flex font-['Inter']",
            "min-h-screen bg-white flex font-['Inter']",
        ),
    )
