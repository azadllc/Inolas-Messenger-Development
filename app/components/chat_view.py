import reflex as rx
from app.states.messenger_state import MessengerState, Message, Chat
from app.components.messenger_widgets import avatar
from app.components.chat_message import message_bubble


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
STICKERS = ["🐱", "🐶", "🦊", "🐼", "🦁", "🐯", "🐸", "🦄"]
GIF_SAMPLES: list[str] = []


def chat_header() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon("arrow-left", class_name="h-5 w-5"),
            on_click=MessengerState.close_chat_mobile,
            class_name="md:hidden p-2 -ml-2 rounded-lg text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800",
        ),
        rx.el.button(
            rx.el.div(
                avatar(MessengerState.active_chat["avatar_seed"], "h-10 w-10"),
                rx.cond(
                    MessengerState.active_chat["online"],
                    rx.el.span(
                        class_name="absolute bottom-0 right-0 h-3 w-3 rounded-full bg-green-500 border-2 border-white dark:border-gray-950"
                    ),
                    rx.fragment(),
                ),
                class_name="relative",
            ),
            rx.el.div(
                rx.el.p(
                    MessengerState.active_chat["name"],
                    class_name="text-sm font-semibold text-gray-900 dark:text-white truncate",
                ),
                rx.cond(
                    MessengerState.active_chat["typing"],
                    rx.el.p(
                        "typing...",
                        class_name="text-xs text-indigo-600 dark:text-indigo-400 italic",
                    ),
                    rx.el.p(
                        MessengerState.active_chat["last_seen"],
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


def pinned_bar() -> rx.Component:
    return rx.cond(
        MessengerState.pinned_messages.length() > 0,
        rx.el.div(
            rx.icon(
                "pin",
                class_name="h-4 w-4 text-indigo-600 dark:text-indigo-400 shrink-0",
            ),
            rx.el.div(
                rx.el.p(
                    "Pinned message",
                    class_name="text-xs font-semibold text-indigo-600 dark:text-indigo-400",
                ),
                rx.el.p(
                    MessengerState.pinned_messages[0]["text"],
                    class_name="text-xs text-gray-700 dark:text-gray-300 truncate",
                ),
                class_name="flex-1 min-w-0",
            ),
            rx.el.span(
                MessengerState.pinned_messages.length(),
                class_name="text-xs font-semibold text-white bg-indigo-600 px-1.5 py-0.5 rounded-full",
            ),
            class_name="flex items-center gap-2 px-4 py-2 bg-indigo-50 dark:bg-indigo-950/40 border-b border-indigo-100 dark:border-indigo-900",
        ),
        rx.fragment(),
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


def typing_indicator() -> rx.Component:
    return rx.cond(
        MessengerState.active_chat["typing"],
        rx.el.div(
            avatar(MessengerState.active_chat["avatar_seed"], "h-8 w-8"),
            rx.el.div(
                rx.el.div(
                    class_name="h-2 w-2 rounded-full bg-gray-400 animate-bounce"
                ),
                rx.el.div(
                    class_name="h-2 w-2 rounded-full bg-gray-400 animate-bounce",
                    style={"animationDelay": "0.15s"},
                ),
                rx.el.div(
                    class_name="h-2 w-2 rounded-full bg-gray-400 animate-bounce",
                    style={"animationDelay": "0.3s"},
                ),
                class_name="flex items-center gap-1 px-3 py-2.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-md",
            ),
            class_name="flex items-end gap-2 mb-3",
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


def sticker_panel() -> rx.Component:
    return rx.cond(
        MessengerState.show_sticker_panel,
        rx.el.div(
            rx.el.p(
                "Stickers",
                class_name="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2",
            ),
            rx.el.div(
                rx.foreach(
                    STICKERS,
                    lambda s: rx.el.button(
                        s,
                        on_click=lambda: MessengerState.send_sticker(s),
                        class_name="text-4xl p-3 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl",
                    ),
                ),
                class_name="grid grid-cols-4 gap-1",
            ),
            class_name="absolute bottom-full left-4 mb-2 w-72 p-3 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl shadow-lg z-10",
        ),
        rx.fragment(),
    )


def attach_menu() -> rx.Component:
    return rx.cond(
        MessengerState.show_attach_menu,
        rx.el.div(
            rx.el.button(
                rx.icon("image", class_name="h-4 w-4 text-blue-500"),
                rx.el.span(
                    "Photo",
                    class_name="text-xs font-medium text-gray-700 dark:text-gray-200",
                ),
                on_click=lambda: MessengerState.attach_type("image"),
                class_name="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg",
            ),
            rx.el.button(
                rx.icon("video", class_name="h-4 w-4 text-red-500"),
                rx.el.span(
                    "Video",
                    class_name="text-xs font-medium text-gray-700 dark:text-gray-200",
                ),
                on_click=lambda: MessengerState.attach_type("video"),
                class_name="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg",
            ),
            rx.el.button(
                rx.icon("file-text", class_name="h-4 w-4 text-purple-500"),
                rx.el.span(
                    "Document",
                    class_name="text-xs font-medium text-gray-700 dark:text-gray-200",
                ),
                on_click=lambda: MessengerState.attach_type("document"),
                class_name="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg",
            ),
            rx.el.button(
                rx.icon("mic", class_name="h-4 w-4 text-green-500"),
                rx.el.span(
                    "Voice note",
                    class_name="text-xs font-medium text-gray-700 dark:text-gray-200",
                ),
                on_click=lambda: MessengerState.attach_type("voice"),
                class_name="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg",
            ),
            class_name="absolute bottom-full left-4 mb-2 flex flex-col p-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-lg z-10 min-w-[160px]",
        ),
        rx.fragment(),
    )


def reply_preview() -> rx.Component:
    return rx.cond(
        MessengerState.reply_to_id != "",
        rx.el.div(
            rx.el.div(
                rx.icon(
                    "reply",
                    class_name="h-4 w-4 text-indigo-600 dark:text-indigo-400 shrink-0",
                ),
                rx.el.div(
                    rx.el.p(
                        f"Replying to {MessengerState.reply_to_sender}",
                        class_name="text-xs font-semibold text-indigo-600 dark:text-indigo-400",
                    ),
                    rx.el.p(
                        MessengerState.reply_to_preview,
                        class_name="text-xs text-gray-600 dark:text-gray-400 truncate",
                    ),
                    class_name="flex-1 min-w-0",
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-4 w-4"),
                    on_click=MessengerState.cancel_reply,
                    class_name="p-1 rounded text-gray-400 hover:text-gray-700",
                ),
                class_name="flex items-center gap-2 px-3 py-2 bg-indigo-50 dark:bg-indigo-950/40 border-l-2 border-indigo-500",
            ),
        ),
        rx.fragment(),
    )


def edit_preview() -> rx.Component:
    return rx.cond(
        MessengerState.edit_message_id != "",
        rx.el.div(
            rx.icon("pencil", class_name="h-4 w-4 text-amber-600 shrink-0"),
            rx.el.p(
                "Editing message",
                class_name="flex-1 text-xs font-semibold text-amber-700 dark:text-amber-400",
            ),
            rx.el.button(
                rx.icon("x", class_name="h-4 w-4"),
                on_click=MessengerState.cancel_edit,
                class_name="p-1 rounded text-gray-400 hover:text-gray-700",
            ),
            class_name="flex items-center gap-2 px-3 py-2 bg-amber-50 dark:bg-amber-950/40 border-l-2 border-amber-500",
        ),
        rx.fragment(),
    )


def composer() -> rx.Component:
    return rx.el.div(
        reply_preview(),
        edit_preview(),
        rx.el.div(
            attach_menu(),
            emoji_panel(),
            sticker_panel(),
            rx.el.button(
                rx.icon("plus", class_name="h-5 w-5"),
                on_click=MessengerState.toggle_attach_menu,
                class_name="p-2 rounded-full text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 shrink-0",
            ),
            rx.el.button(
                rx.icon("smile", class_name="h-5 w-5"),
                on_click=MessengerState.toggle_emoji_panel,
                class_name="p-2 rounded-full text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 shrink-0",
            ),
            rx.el.button(
                rx.icon("sticker", class_name="h-5 w-5"),
                on_click=MessengerState.toggle_sticker_panel,
                class_name="p-2 rounded-full text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 shrink-0",
            ),
            rx.el.input(
                placeholder="Type a message...",
                default_value=MessengerState.composer_text,
                on_change=MessengerState.set_composer.debounce(100),
                class_name="flex-1 px-4 py-2.5 bg-gray-100 dark:bg-gray-900 rounded-full text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            ),
            rx.cond(
                MessengerState.composer_text.length() > 0,
                rx.el.button(
                    rx.icon("send", class_name="h-4 w-4"),
                    on_click=MessengerState.send_message,
                    class_name="h-10 w-10 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white flex items-center justify-center shrink-0 transition-colors",
                ),
                rx.el.button(
                    rx.icon("mic", class_name="h-4 w-4"),
                    on_click=lambda: MessengerState.attach_type("voice"),
                    class_name="h-10 w-10 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white flex items-center justify-center shrink-0 transition-colors",
                ),
            ),
            class_name="relative flex items-end gap-1 p-3 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950",
        ),
        class_name="shrink-0",
    )


def forward_target_row(chat: rx.Var) -> rx.Component:
    return rx.el.button(
        avatar(chat["avatar_seed"], "h-9 w-9"),
        rx.el.div(
            rx.el.p(
                chat["name"],
                class_name="text-sm font-semibold text-gray-900 dark:text-white text-left",
            ),
            rx.el.p(
                rx.cond(
                    chat["type"] == "group",
                    "Group",
                    f"@{chat['username']}",
                ),
                class_name="text-xs text-gray-500 text-left",
            ),
            class_name="flex-1 min-w-0",
        ),
        rx.cond(
            MessengerState.forward_targets.contains(chat["id"]),
            rx.el.div(
                rx.icon("check", class_name="h-3.5 w-3.5 text-white"),
                class_name="h-5 w-5 rounded-full bg-indigo-600 flex items-center justify-center",
            ),
            rx.el.div(
                class_name="h-5 w-5 rounded-full border-2 border-gray-300 dark:border-gray-700"
            ),
        ),
        on_click=lambda: MessengerState.toggle_forward_target(chat["id"]),
        class_name="flex items-center gap-3 w-full p-2.5 hover:bg-gray-50 dark:hover:bg-gray-900 rounded-xl transition-colors",
    )


def forward_modal() -> rx.Component:
    return rx.cond(
        MessengerState.show_forward_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Forward to...",
                        class_name="text-base font-bold text-gray-900 dark:text-white",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-4 w-4"),
                        on_click=MessengerState.close_forward_modal,
                        class_name="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800",
                    ),
                    class_name="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800",
                ),
                rx.el.div(
                    rx.foreach(MessengerState.chats, forward_target_row),
                    class_name="flex flex-col p-2 overflow-y-auto max-h-80",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=MessengerState.close_forward_modal,
                        class_name="flex-1 py-2.5 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-xl text-sm font-semibold",
                    ),
                    rx.el.button(
                        f"Send ({MessengerState.forward_targets.length()})",
                        on_click=MessengerState.submit_forward,
                        disabled=MessengerState.forward_targets.length() == 0,
                        class_name="flex-1 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white rounded-xl text-sm font-semibold",
                    ),
                    class_name="flex gap-2 p-4 border-t border-gray-200 dark:border-gray-800",
                ),
                class_name="bg-white dark:bg-gray-950 rounded-2xl border border-gray-200 dark:border-gray-800 w-full max-w-md",
            ),
            class_name="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50",
        ),
        rx.fragment(),
    )


def delete_modal() -> rx.Component:
    return rx.cond(
        MessengerState.show_delete_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "trash-2",
                        class_name="h-6 w-6 text-red-600 dark:text-red-400",
                    ),
                    class_name="h-12 w-12 rounded-2xl bg-red-50 dark:bg-red-950/40 flex items-center justify-center mx-auto mb-4",
                ),
                rx.el.h3(
                    "Delete message?",
                    class_name="text-lg font-bold text-gray-900 dark:text-white text-center mb-1",
                ),
                rx.el.p(
                    "This can't be undone.",
                    class_name="text-sm text-gray-500 dark:text-gray-400 text-center mb-6",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("user", class_name="h-4 w-4"),
                        rx.el.span(
                            "Delete for me", class_name="text-sm font-semibold"
                        ),
                        on_click=MessengerState.delete_for_me,
                        class_name="flex items-center justify-center gap-2 w-full py-2.5 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-xl",
                    ),
                    rx.el.button(
                        rx.icon("users", class_name="h-4 w-4"),
                        rx.el.span(
                            "Delete for everyone",
                            class_name="text-sm font-semibold",
                        ),
                        on_click=MessengerState.delete_for_everyone,
                        class_name="flex items-center justify-center gap-2 w-full py-2.5 bg-red-600 hover:bg-red-700 text-white rounded-xl",
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


def messages_area() -> rx.Component:
    return rx.el.div(
        load_older_button(),
        rx.foreach(MessengerState.active_messages, message_bubble),
        typing_indicator(),
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
                "Select a chat from the list to view messages, or discover new people to connect with.",
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
            pinned_bar(),
            message_search_bar(),
            messages_area(),
            composer(),
            forward_modal(),
            delete_modal(),
            class_name="flex flex-col flex-1 h-full bg-gray-50 dark:bg-black min-w-0",
        ),
        empty_chat_placeholder(),
    )
