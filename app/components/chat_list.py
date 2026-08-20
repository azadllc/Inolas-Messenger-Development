import reflex as rx
from app.states.messenger_state import MessengerState, Chat
from app.components.messenger_widgets import avatar, online_dot
from app.components.theme_toggle import theme_toggle


def chat_row(chat: Chat) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            avatar(chat["avatar_seed"], "h-11 w-11"),
            online_dot(chat["online"] & (chat["type"] == "dm")),
            class_name="relative shrink-0",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    chat["name"],
                    class_name="text-sm font-semibold text-gray-900 dark:text-white truncate",
                ),
                rx.el.div(
                    rx.cond(
                        chat["pinned"],
                        rx.icon("pin", class_name="h-3 w-3 text-gray-400"),
                        rx.fragment(),
                    ),
                    rx.cond(
                        chat["muted"],
                        rx.icon("bell-off", class_name="h-3 w-3 text-gray-400"),
                        rx.fragment(),
                    ),
                    rx.el.span(
                        chat["last_time"],
                        class_name="text-xs text-gray-500 dark:text-gray-400 shrink-0",
                    ),
                    class_name="flex items-center gap-1",
                ),
                class_name="flex items-center justify-between gap-2",
            ),
            rx.el.div(
                rx.cond(
                    chat["typing"],
                    rx.el.p(
                        "typing...",
                        class_name="text-xs text-indigo-600 dark:text-indigo-400 italic truncate flex-1",
                    ),
                    rx.el.p(
                        chat["last_message"],
                        class_name="text-xs text-gray-500 dark:text-gray-400 truncate flex-1",
                    ),
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
                MessengerState.filtered_chats.length() == 0,
                rx.el.div(
                    rx.icon(
                        "inbox", class_name="h-8 w-8 text-gray-300 mx-auto mb-2"
                    ),
                    rx.el.p(
                        "No chats found",
                        class_name="text-sm text-gray-500 text-center",
                    ),
                    class_name="p-8",
                ),
                rx.el.div(
                    rx.foreach(MessengerState.filtered_chats, chat_row),
                    class_name="flex flex-col gap-0.5",
                ),
            ),
            class_name="flex-1 overflow-y-auto p-2",
        ),
        class_name="flex flex-col w-full md:w-96 h-screen border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 shrink-0",
    )
