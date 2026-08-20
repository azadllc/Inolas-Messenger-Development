import reflex as rx
from app.states.auth_state import AuthState
from app.states.messenger_state import MessengerState


def nav_item(icon: str, label: str, view: str) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, class_name="h-5 w-5"),
        rx.el.span(label, class_name="text-sm font-medium"),
        on_click=lambda: MessengerState.set_active_view(view),
        class_name=rx.cond(
            MessengerState.active_view == view,
            "flex items-center gap-3 w-full px-3 py-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300",
            "flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors",
        ),
    )


def sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("message-circle", class_name="h-5 w-5 text-white"),
                class_name="h-9 w-9 rounded-xl bg-indigo-600 flex items-center justify-center",
            ),
            rx.el.span(
                "Inolas",
                class_name="text-lg font-bold text-gray-900 dark:text-white",
            ),
            class_name="flex items-center gap-2 px-3 h-16 border-b border-gray-200 dark:border-gray-800",
        ),
        rx.el.nav(
            nav_item("message-square", "Chats", "chats"),
            nav_item("search", "Discover", "search"),
            nav_item("settings", "Settings", "settings"),
            class_name="flex flex-col gap-1 p-3 flex-1",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.span(
                            AuthState.user_avatar_seed.upper()[0:1],
                            class_name="text-white font-semibold text-sm",
                        ),
                        class_name="h-8 w-8 rounded-full bg-indigo-500 flex items-center justify-center shrink-0",
                    ),
                    rx.el.div(
                        rx.el.p(
                            AuthState.user_display_name,
                            class_name="text-sm font-semibold text-gray-900 dark:text-white truncate",
                        ),
                        rx.el.p(
                            f"@{AuthState.user_username}",
                            class_name="text-xs text-gray-500 dark:text-gray-400 truncate",
                        ),
                        class_name="flex-1 text-left min-w-0",
                    ),
                    rx.el.button(
                        rx.icon("log-out", class_name="h-4 w-4"),
                        on_click=AuthState.logout,
                        class_name="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white",
                    ),
                    class_name="flex items-center gap-2 p-2 rounded-xl border border-gray-200 dark:border-gray-800 w-full",
                ),
                class_name="p-3 border-t border-gray-200 dark:border-gray-800",
            ),
        ),
        class_name="hidden md:flex flex-col w-64 h-screen border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 shrink-0",
    )


from app.components.chat_list import chat_list
from app.components.chat_view import chat_view
from app.components.search_panel import search_panel
from app.components.settings_panel import settings_panel
from app.components.profile_panel import profile_panel
from app.components.messenger_widgets import toast


def main_content() -> rx.Component:
    return rx.match(
        MessengerState.active_view,
        (
            "chats",
            rx.el.div(
                rx.el.div(
                    chat_list(),
                    class_name=rx.cond(
                        MessengerState.mobile_show_chat,
                        "hidden md:flex",
                        "flex",
                    ),
                ),
                rx.el.div(
                    chat_view(),
                    class_name=rx.cond(
                        MessengerState.mobile_show_chat,
                        "flex flex-1 h-screen min-w-0",
                        "hidden md:flex flex-1 h-screen min-w-0",
                    ),
                ),
                profile_panel(),
                class_name="flex flex-1 h-screen min-w-0 relative",
            ),
        ),
        ("search", search_panel()),
        ("settings", settings_panel()),
        chat_list(),
    )


def home_layout() -> rx.Component:
    return rx.el.div(
        sidebar(),
        main_content(),
        toast(),
        class_name=rx.cond(
            AuthState.theme_mode == "dark",
            "dark flex h-screen w-screen bg-white dark:bg-black overflow-hidden font-['Inter']",
            "flex h-screen w-screen bg-white overflow-hidden font-['Inter']",
        ),
    )
