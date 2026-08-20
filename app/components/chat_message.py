import reflex as rx
from app.states.messenger_state import MessengerState, Message, Reaction
from app.components.messenger_widgets import avatar


def reaction_pill(r: Reaction) -> rx.Component:
    return rx.el.div(
        rx.el.span(r["emoji"], class_name="text-sm"),
        rx.el.span(
            r["users"].length(),
            class_name="text-xs font-semibold text-gray-700 dark:text-gray-300",
        ),
        class_name="flex items-center gap-1 px-2 py-0.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full",
    )


def reaction_picker(msg_id: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.foreach(
            ["👍", "❤️", "😂", "😮", "😢", "🔥"],
            lambda e: rx.el.button(
                e,
                on_click=lambda: MessengerState.react_to_message(msg_id, e),
                class_name="text-lg hover:scale-125 transition-transform p-1",
            ),
        ),
        class_name="flex items-center gap-0.5 p-1 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-full shadow-lg",
    )


def message_menu(msg: Message, is_me: rx.Var) -> rx.Component:
    return rx.el.div(
        reaction_picker(msg["id"]),
        rx.el.div(
            rx.el.button(
                rx.icon("reply", class_name="h-3.5 w-3.5"),
                rx.el.span("Reply", class_name="text-xs font-medium"),
                on_click=lambda: MessengerState.start_reply(msg["id"]),
                class_name="flex items-center gap-2 w-full px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-lg text-left",
            ),
            rx.el.button(
                rx.icon("forward", class_name="h-3.5 w-3.5"),
                rx.el.span("Forward", class_name="text-xs font-medium"),
                on_click=lambda: MessengerState.open_forward_modal(msg["id"]),
                class_name="flex items-center gap-2 w-full px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-lg text-left",
            ),
            rx.el.button(
                rx.icon("pin", class_name="h-3.5 w-3.5"),
                rx.el.span(
                    rx.cond(msg["pinned"], "Unpin", "Pin"),
                    class_name="text-xs font-medium",
                ),
                on_click=lambda: MessengerState.toggle_pin_message(msg["id"]),
                class_name="flex items-center gap-2 w-full px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-lg text-left",
            ),
            rx.cond(
                is_me,
                rx.el.button(
                    rx.icon("pencil", class_name="h-3.5 w-3.5"),
                    rx.el.span("Edit", class_name="text-xs font-medium"),
                    on_click=lambda: MessengerState.start_edit(msg["id"]),
                    class_name="flex items-center gap-2 w-full px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-lg text-left",
                ),
                rx.fragment(),
            ),
            rx.el.button(
                rx.icon("trash-2", class_name="h-3.5 w-3.5"),
                rx.el.span("Delete", class_name="text-xs font-medium"),
                on_click=lambda: MessengerState.open_delete_modal(msg["id"]),
                class_name="flex items-center gap-2 w-full px-3 py-2 hover:bg-red-50 dark:hover:bg-red-950/40 text-red-600 dark:text-red-400 rounded-lg text-left",
            ),
            class_name="flex flex-col p-1 mt-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-lg min-w-[140px]",
        ),
        class_name="absolute z-30",
    )


def media_content(msg: Message, is_me: rx.Var) -> rx.Component:
    return rx.match(
        msg["type"],
        (
            "image",
            rx.el.img(
                src=msg["media_url"],
                class_name="rounded-xl max-w-xs max-h-64 object-cover",
            ),
        ),
        (
            "video",
            rx.el.div(
                rx.el.div(
                    rx.icon("play", class_name="h-8 w-8 text-white fill-white"),
                    class_name="h-14 w-14 rounded-full bg-black/60 flex items-center justify-center",
                ),
                rx.el.p(
                    msg["file_name"],
                    class_name="text-xs text-white/90 absolute bottom-2 left-3",
                ),
                rx.el.p(
                    msg["file_size"],
                    class_name="text-xs text-white/70 absolute bottom-2 right-3",
                ),
                class_name="relative w-64 h-40 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center",
            ),
        ),
        (
            "gif",
            rx.el.div(
                rx.el.img(
                    src=msg["media_url"],
                    class_name="rounded-xl max-w-xs max-h-64 object-cover",
                ),
                rx.el.span(
                    "GIF",
                    class_name="absolute top-2 left-2 px-1.5 py-0.5 bg-black/60 text-white text-xs font-bold rounded",
                ),
                class_name="relative",
            ),
        ),
        (
            "sticker",
            rx.el.div(
                msg["text"],
                class_name="text-6xl leading-none",
            ),
        ),
        (
            "document",
            rx.el.div(
                rx.el.div(
                    rx.icon("file-text", class_name="h-6 w-6 text-white"),
                    class_name="h-11 w-11 rounded-xl bg-indigo-600 flex items-center justify-center shrink-0",
                ),
                rx.el.div(
                    rx.el.p(
                        msg["file_name"],
                        class_name="text-sm font-semibold text-gray-900 dark:text-white truncate",
                    ),
                    rx.el.p(
                        msg["file_size"],
                        class_name="text-xs text-gray-500 dark:text-gray-400",
                    ),
                    class_name="flex-1 min-w-0",
                ),
                rx.icon(
                    "download", class_name="h-4 w-4 text-gray-400 shrink-0"
                ),
                class_name="flex items-center gap-3 p-2.5 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 min-w-[220px]",
            ),
        ),
        (
            "voice",
            rx.el.div(
                rx.el.button(
                    rx.icon("play", class_name="h-4 w-4 fill-current"),
                    class_name=rx.cond(
                        is_me,
                        "h-9 w-9 rounded-full bg-white/20 text-white flex items-center justify-center shrink-0",
                        "h-9 w-9 rounded-full bg-indigo-600 text-white flex items-center justify-center shrink-0",
                    ),
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            class_name="h-1 flex-1 rounded-full bg-current opacity-30"
                        ),
                        rx.el.div(class_name="h-2 w-2 rounded-full bg-current"),
                        class_name="flex items-center gap-1",
                    ),
                    rx.el.p(
                        msg["file_size"],
                        class_name=rx.cond(
                            is_me,
                            "text-xs text-white/80 mt-1",
                            "text-xs text-gray-500 dark:text-gray-400 mt-1",
                        ),
                    ),
                    class_name="flex-1 min-w-[140px]",
                ),
                class_name="flex items-center gap-3",
            ),
        ),
        rx.el.p(
            msg["text"], class_name="text-sm whitespace-pre-wrap break-words"
        ),
    )


def message_bubble(msg: Message) -> rx.Component:
    is_me = msg["sender"] == "me"
    return rx.el.div(
        rx.cond(
            msg["deleted_for_everyone"],
            rx.el.div(
                rx.el.div(
                    rx.icon("ban", class_name="h-3.5 w-3.5"),
                    rx.el.span(
                        "This message was deleted",
                        class_name="text-xs italic",
                    ),
                    class_name=rx.cond(
                        is_me,
                        "flex items-center gap-1.5 px-3 py-2 rounded-2xl bg-gray-200 dark:bg-gray-800 text-gray-500 dark:text-gray-400 max-w-[75%]",
                        "flex items-center gap-1.5 px-3 py-2 rounded-2xl bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 max-w-[75%]",
                    ),
                ),
                class_name=rx.cond(
                    is_me,
                    "flex justify-end",
                    "flex justify-start",
                ),
            ),
            rx.el.div(
                rx.cond(
                    ~is_me,
                    avatar(msg["sender"], "h-8 w-8"),
                    rx.fragment(),
                ),
                rx.el.div(
                    rx.cond(
                        msg["forwarded"],
                        rx.el.div(
                            rx.icon("forward", class_name="h-3 w-3"),
                            rx.el.span(
                                "Forwarded", class_name="text-xs italic"
                            ),
                            class_name=rx.cond(
                                is_me,
                                "flex items-center gap-1 text-white/70 mb-1",
                                "flex items-center gap-1 text-gray-500 mb-1",
                            ),
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        msg["reply_to"] != "",
                        rx.el.div(
                            rx.el.p(
                                msg["reply_sender"],
                                class_name=rx.cond(
                                    is_me,
                                    "text-xs font-semibold text-white/90",
                                    "text-xs font-semibold text-indigo-600 dark:text-indigo-400",
                                ),
                            ),
                            rx.el.p(
                                msg["reply_preview"],
                                class_name=rx.cond(
                                    is_me,
                                    "text-xs text-white/70 truncate",
                                    "text-xs text-gray-600 dark:text-gray-400 truncate",
                                ),
                            ),
                            class_name=rx.cond(
                                is_me,
                                "border-l-2 border-white/50 pl-2 mb-2 max-w-full",
                                "border-l-2 border-indigo-500 pl-2 mb-2 max-w-full",
                            ),
                        ),
                        rx.fragment(),
                    ),
                    rx.el.div(
                        rx.cond(
                            (msg["type"] == "sticker")
                            | (msg["type"] == "image")
                            | (msg["type"] == "gif"),
                            media_content(msg, is_me),
                            rx.el.div(
                                media_content(msg, is_me),
                                rx.cond(
                                    (msg["type"] != "text")
                                    & (msg["text"] != ""),
                                    rx.el.p(
                                        msg["text"],
                                        class_name="text-sm mt-2",
                                    ),
                                    rx.fragment(),
                                ),
                            ),
                        ),
                        rx.el.div(
                            rx.cond(
                                msg["edited"],
                                rx.el.span(
                                    "edited",
                                    class_name=rx.cond(
                                        is_me,
                                        "text-[10px] italic text-white/60",
                                        "text-[10px] italic text-gray-400",
                                    ),
                                ),
                                rx.fragment(),
                            ),
                            rx.el.span(
                                msg["timestamp"],
                                class_name=rx.cond(
                                    is_me,
                                    "text-[10px] text-white/70",
                                    "text-[10px] text-gray-400",
                                ),
                            ),
                            rx.cond(
                                is_me,
                                rx.cond(
                                    msg["read_by"].length() > 0,
                                    rx.icon(
                                        "check-check",
                                        class_name="h-3 w-3 text-white/90",
                                    ),
                                    rx.icon(
                                        "check",
                                        class_name="h-3 w-3 text-white/60",
                                    ),
                                ),
                                rx.fragment(),
                            ),
                            class_name="flex items-center gap-1 mt-1 justify-end",
                        ),
                        class_name=rx.cond(
                            msg["type"] == "sticker",
                            "px-1 py-1",
                            rx.cond(
                                is_me,
                                "px-3 py-2 rounded-2xl bg-indigo-600 text-white rounded-br-md",
                                "px-3 py-2 rounded-2xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-bl-md",
                            ),
                        ),
                    ),
                    rx.cond(
                        msg["reactions"].length() > 0,
                        rx.el.div(
                            rx.foreach(msg["reactions"], reaction_pill),
                            class_name=rx.cond(
                                is_me,
                                "flex items-center gap-1 mt-1 justify-end",
                                "flex items-center gap-1 mt-1 justify-start",
                            ),
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        MessengerState.active_message_menu == msg["id"],
                        message_menu(msg, is_me),
                        rx.fragment(),
                    ),
                    class_name="relative max-w-[70%] group",
                ),
                rx.el.button(
                    rx.icon("ellipsis-vertical", class_name="h-4 w-4"),
                    on_click=lambda: MessengerState.toggle_message_menu(
                        msg["id"]
                    ),
                    class_name="opacity-0 group-hover:opacity-100 p-1.5 rounded-full text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-opacity self-center",
                ),
                class_name=rx.cond(
                    is_me,
                    "group flex items-end gap-2 justify-end",
                    "group flex items-end gap-2 justify-start",
                ),
            ),
        ),
        class_name="mb-3",
    )
