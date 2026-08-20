import reflex as rx
from app.states.messenger_state import MessengerState
from app.components.messenger_widgets import avatar
from app.components.message_bubble import message_bubble


EMOJIS = [
    "😀",
    "😂",
    "🥰",
    "😎",
    "🤔",
    "👍",
    "🎉",
    "🔥",
    "❤️",
    "💯",
    "🙏",
    "👀",
    "🚀",
    "✨",
    "💪",
    "🎯",
]


def chat_header() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon("arrow-left", class_name="h-5 w-5"),
            on_click=MessengerState.close_chat_mobile,
            class_name="md:hidden p-2 -ml-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800",
        ),
        rx.el.button(
            avatar(MessengerState.active_chat["avatar_seed"], "h-10 w-10"),
            rx.el.div(
                rx.el.p(
                    MessengerState.active_chat["name"],
                    class_name="text-sm font-semibold text-gray-900 dark:text-white truncate",
                ),
                rx.cond(
                    MessengerState.active_chat["username"] != "",
                    rx.el.p(
                        f"@{MessengerState.active_chat['username']}",
                        class_name="text-xs text-gray-500 dark:text-gray-400 truncate",
                    ),
                    rx.el.p(
                        "Direct message",
                        class_name="text-xs text-gray-500 dark:text-gray-400 truncate",
                    ),
                ),
                class_name="flex-1 text-left min-w-0",
            ),
            on_click=lambda: MessengerState.open_profile(
                MessengerState.active_chat["username"]
            ),
            class_name="flex items-center gap-3 flex-1 min-w-0",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("search", class_name="h-4 w-4"),
                on_click=MessengerState.toggle_message_search,
                class_name="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800",
            ),
            rx.el.button(
                rx.icon("info", class_name="h-4 w-4"),
                on_click=lambda: MessengerState.open_profile(
                    MessengerState.active_chat["username"]
                ),
                class_name="p-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800",
            ),
            class_name="flex items-center gap-1 shrink-0",
        ),
        class_name="flex items-center gap-3 px-4 h-16 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 shrink-0",
    )


def message_search_bar() -> rx.Component:
    return rx.cond(
        MessengerState.show_message_search,
        rx.el.div(
            rx.icon(
                "search",
                class_name="h-4 w-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2",
            ),
            rx.el.input(
                placeholder="Search in conversation...",
                default_value=MessengerState.message_search_query,
                on_change=MessengerState.set_message_search_query.debounce(200),
                class_name="w-full pl-9 pr-10 py-2 bg-gray-100 dark:bg-gray-900 rounded-xl text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            ),
            rx.el.button(
                rx.icon("x", class_name="h-4 w-4"),
                on_click=MessengerState.toggle_message_search,
                class_name="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded text-gray-400 hover:text-gray-700",
            ),
            class_name="relative px-4 py-3 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950",
        ),
        rx.fragment(),
    )


def emoji_panel() -> rx.Component:
    return rx.cond(
        MessengerState.show_emoji_panel,
        rx.el.div(
            rx.foreach(
                EMOJIS,
                lambda e: rx.el.button(
                    e,
                    on_click=lambda: MessengerState.insert_emoji(e),
                    class_name="text-2xl p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg",
                ),
            ),
            class_name="absolute bottom-full left-4 mb-2 grid grid-cols-8 gap-1 p-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-lg z-10",
        ),
        rx.fragment(),
    )


def composer() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            emoji_panel(),
            rx.el.button(
                rx.icon("smile", class_name="h-5 w-5"),
                on_click=MessengerState.toggle_emoji_panel,
                class_name="p-2 rounded-full text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 shrink-0",
            ),
            rx.el.input(
                placeholder="Type a message...",
                default_value=MessengerState.composer_text,
                disabled=MessengerState.sending_message,
                on_change=MessengerState.set_composer.debounce(100),
                class_name="flex-1 px-4 py-2.5 bg-gray-100 dark:bg-gray-900 rounded-full text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-60",
            ),
            rx.cond(
                MessengerState.sending_message,
                rx.el.div(
                    rx.el.div(
                        class_name="h-4 w-4 border-2 border-white/40 border-t-white rounded-full animate-spin"
                    ),
                    class_name="h-10 w-10 rounded-full bg-indigo-600 text-white flex items-center justify-center shrink-0",
                ),
                rx.el.button(
                    rx.icon("send", class_name="h-4 w-4"),
                    on_click=MessengerState.send_message,
                    disabled=MessengerState.composer_text.length() == 0,
                    class_name="h-10 w-10 rounded-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white flex items-center justify-center shrink-0 transition-colors",
                ),
            ),
            class_name="relative flex items-end gap-1 p-3 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950",
        ),
        class_name="shrink-0",
    )


def delete_modal() -> rx.Component:
    return rx.cond(
        MessengerState.show_delete_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "eye-off",
                        class_name="h-6 w-6 text-indigo-600 dark:text-indigo-400",
                    ),
                    class_name="h-12 w-12 rounded-2xl bg-indigo-50 dark:bg-indigo-950/40 flex items-center justify-center mx-auto mb-4",
                ),
                rx.el.h3(
                    "Hide this message?",
                    class_name="text-lg font-bold text-gray-900 dark:text-white text-center mb-1",
                ),
                rx.el.p(
                    "It will be removed from your view only. Other people in this chat will still see it.",
                    class_name="text-sm text-gray-500 dark:text-gray-400 text-center mb-6",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("eye-off", class_name="h-4 w-4"),
                        rx.el.span(
                            "Delete for me", class_name="text-sm font-semibold"
                        ),
                        on_click=MessengerState.delete_for_me,
                        class_name="flex items-center justify-center gap-2 w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl",
                    ),
                    rx.el.button(
                        "Cancel",
                        on_click=MessengerState.close_delete_modal,
                        class_name="w-full py-2.5 text-sm font-semibold text-gray-500 hover:text-gray-700",
                    ),
                    class_name="flex flex-col gap-2",
                ),
                class_name="bg-white dark:bg-gray-950 rounded-2xl border border-gray-200 dark:border-gray-800 w-full max-w-sm p-6",
            ),
            class_name="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50",
        ),
        rx.fragment(),
    )


def load_older_button() -> rx.Component:
    return rx.cond(
        MessengerState.has_older_messages,
        rx.el.div(
            rx.el.button(
                rx.icon("arrow-up", class_name="h-3.5 w-3.5"),
                rx.el.span(
                    "Load older messages",
                    class_name="text-xs font-semibold",
                ),
                on_click=MessengerState.load_older_messages,
                class_name="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors",
            ),
            class_name="flex justify-center mb-3",
        ),
        rx.fragment(),
    )


def messages_loading_state() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            class_name="h-8 w-8 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-3"
        ),
        rx.el.p(
            "Loading messages...",
            class_name="text-xs text-gray-500 dark:text-gray-400 text-center",
        ),
        class_name="py-16",
    )


def messages_empty_state() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "message-circle",
                class_name="h-7 w-7 text-indigo-600 dark:text-indigo-400",
            ),
            class_name="h-14 w-14 rounded-2xl bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center mx-auto mb-3",
        ),
        rx.el.p(
            "No messages yet",
            class_name="text-sm font-semibold text-gray-900 dark:text-white text-center",
        ),
        rx.el.p(
            "This conversation is empty for now.",
            class_name="text-xs text-gray-500 dark:text-gray-400 text-center mt-1",
        ),
        class_name="py-16",
    )


def messages_area() -> rx.Component:
    return rx.el.div(
        rx.cond(
            MessengerState.messages_loading,
            messages_loading_state(),
            rx.cond(
                MessengerState.active_messages.length() == 0,
                messages_empty_state(),
                rx.el.div(
                    load_older_button(),
                    rx.foreach(MessengerState.active_messages, message_bubble),
                ),
            ),
        ),
        class_name="flex-1 overflow-y-auto p-4 bg-gray-50 dark:bg-black",
    )


def empty_chat_placeholder() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "message-circle",
                    class_name="h-10 w-10 text-indigo-600 dark:text-indigo-400",
                ),
                class_name="h-20 w-20 rounded-3xl bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center mx-auto mb-6",
            ),
            rx.el.h2(
                "Your messages",
                class_name="text-2xl font-bold text-gray-900 dark:text-white mb-2 text-center",
            ),
            rx.el.p(
                "Select a conversation to read its messages, or find someone by their @username to start a new direct message.",
                class_name="text-sm text-gray-500 dark:text-gray-400 text-center max-w-md mx-auto",
            ),
            class_name="max-w-md",
        ),
        class_name="hidden md:flex flex-1 items-center justify-center bg-gray-50 dark:bg-black p-8",
    )


def chat_view() -> rx.Component:
    return rx.cond(
        MessengerState.active_chat_id != "",
        rx.el.div(
            chat_header(),
            message_search_bar(),
            messages_area(),
            composer(),
            delete_modal(),
            class_name="flex flex-col flex-1 h-full bg-gray-50 dark:bg-black min-w-0",
        ),
        empty_chat_placeholder(),
    )
