import reflex as rx
from app.states.messenger_state import MessengerState, Chat
from app.components.messenger_widgets import avatar
from app.components.theme_toggle import theme_toggle


def chat_row(chat: Chat) -> rx.Component:
    return rx.el.button(
        avatar(chat["avatar_seed"], "h-11 w-11"),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    chat["name"],
                    class_name="text-sm font-semibold text-gray-900 dark:text-white truncate",
                ),
                rx.el.span(
                    chat["last_time"],
                    class_name="text-xs text-gray-500 dark:text-gray-400 shrink-0",
                ),
                class_name="flex items-center justify-between gap-2",
            ),
            rx.el.div(
                rx.el.p(
                    chat["last_message"],
                    class_name="text-xs text-gray-500 dark:text-gray-400 truncate flex-1",
                ),
                rx.cond(
                    chat["unread"] > 0,
                    rx.el.span(
                        chat["unread"],
                        class_name="h-5 min-w-5 px-1.5 rounded-full bg-indigo-600 text-white text-xs font-semibold flex items-center justify-center shrink-0",
                    ),
                    rx.fragment(),
                ),
                class_name="flex items-center justify-between gap-2 mt-0.5",
            ),
            class_name="flex-1 min-w-0",
        ),
        on_click=lambda: MessengerState.open_chat(chat["id"]),
        class_name=rx.cond(
            MessengerState.active_chat_id == chat["id"],
            "w-full flex items-center gap-3 p-3 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 text-left",
            "w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors text-left",
        ),
    )


def chat_list_skeleton() -> rx.Component:
    return rx.el.div(
        rx.foreach(
            [0, 1, 2, 3, 4],
            lambda _i: rx.el.div(
                rx.el.div(
                    class_name="h-11 w-11 rounded-full bg-gray-200 dark:bg-gray-800 shrink-0"
                ),
                rx.el.div(
                    rx.el.div(
                        class_name="h-3 w-32 rounded-full bg-gray-200 dark:bg-gray-800"
                    ),
                    rx.el.div(
                        class_name="h-2.5 w-44 rounded-full bg-gray-100 dark:bg-gray-900 mt-2"
                    ),
                    class_name="flex-1 min-w-0",
                ),
                class_name="flex items-center gap-3 p-3 animate-pulse",
            ),
        ),
        class_name="flex flex-col",
    )


def chat_list_empty() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "message-square-plus",
                class_name="h-7 w-7 text-indigo-600 dark:text-indigo-400",
            ),
            class_name="h-14 w-14 rounded-2xl bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center mx-auto mb-3",
        ),
        rx.el.p(
            "No conversations yet",
            class_name="text-sm font-semibold text-gray-900 dark:text-white text-center",
        ),
        rx.el.p(
            "Discover people by their @username to start your first chat.",
            class_name="text-xs text-gray-500 dark:text-gray-400 text-center mt-1 mb-4",
        ),
        rx.el.button(
            rx.icon("search", class_name="h-4 w-4"),
            rx.el.span("Discover people", class_name="text-xs font-semibold"),
            on_click=lambda: MessengerState.set_active_view("search"),
            class_name="flex items-center gap-1.5 px-3 py-2 mx-auto bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-colors",
        ),
        class_name="p-8",
    )


def chat_list_no_results() -> rx.Component:
    return rx.el.div(
        rx.icon("inbox", class_name="h-8 w-8 text-gray-300 mx-auto mb-2"),
        rx.el.p(
            "No chats match your search",
            class_name="text-sm text-gray-500 text-center",
        ),
        class_name="p-8",
    )


def chat_list_error() -> rx.Component:
    return rx.el.div(
        rx.icon(
            "triangle-alert",
            class_name="h-8 w-8 text-amber-500 mx-auto mb-2",
        ),
        rx.el.p(
            MessengerState.load_error,
            class_name="text-sm text-gray-600 dark:text-gray-300 text-center",
        ),
        rx.el.button(
            rx.icon("refresh-cw", class_name="h-4 w-4"),
            rx.el.span("Try again", class_name="text-xs font-semibold"),
            on_click=MessengerState.load_messenger_data,
            class_name="flex items-center gap-1.5 px-3 py-2 mx-auto mt-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-colors",
        ),
        class_name="p-8",
    )


def chat_list() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Messages",
                    class_name="text-xl font-bold text-gray-900 dark:text-white",
                ),
                rx.cond(
                    MessengerState.total_unread > 0,
                    rx.el.span(
                        MessengerState.total_unread,
                        class_name="h-5 min-w-5 px-1.5 rounded-full bg-indigo-600 text-white text-xs font-semibold flex items-center justify-center",
                    ),
                    rx.fragment(),
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("square-pen", class_name="h-4 w-4"),
                    on_click=lambda: MessengerState.set_active_view("search"),
                    class_name="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800",
                ),
                theme_toggle(),
                class_name="flex items-center gap-1",
            ),
            class_name="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800",
        ),
        rx.el.div(
            rx.icon(
                "search",
                class_name="h-4 w-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2",
            ),
            rx.el.input(
                placeholder="Search chats",
                default_value=MessengerState.chat_search_query,
                on_change=MessengerState.set_chat_search_query.debounce(200),
                class_name="w-full pl-9 pr-3 py-2 bg-gray-100 dark:bg-gray-900 border border-transparent rounded-xl text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            ),
            class_name="relative p-4 border-b border-gray-200 dark:border-gray-800",
        ),
        rx.el.div(
            rx.cond(
                MessengerState.chats_loading
                & (MessengerState.chats.length() == 0),
                chat_list_skeleton(),
                rx.cond(
                    MessengerState.load_error != "",
                    chat_list_error(),
                    rx.cond(
                        MessengerState.filtered_chats.length() == 0,
                        rx.cond(
                            MessengerState.chat_search_query != "",
                            chat_list_no_results(),
                            chat_list_empty(),
                        ),
                        rx.el.div(
                            rx.foreach(MessengerState.filtered_chats, chat_row),
                            class_name="flex flex-col gap-0.5",
                        ),
                    ),
                ),
            ),
            class_name="flex-1 overflow-y-auto p-2",
        ),
        class_name="flex flex-col w-full md:w-96 h-screen border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 shrink-0",
    )
