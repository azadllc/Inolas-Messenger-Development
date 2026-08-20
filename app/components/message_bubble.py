import reflex as rx
from app.states.messenger_state import MessengerState, Message
from app.components.messenger_widgets import avatar


def message_menu(msg: Message) -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon("trash-2", class_name="h-3.5 w-3.5"),
            rx.el.span(
                "Delete for me",
                class_name="text-xs font-medium whitespace-nowrap",
            ),
            on_click=lambda: MessengerState.open_delete_modal(msg["id"]),
            class_name="flex items-center gap-2 w-full px-3 py-2 hover:bg-red-50 dark:hover:bg-red-950/40 text-red-600 dark:text-red-400 rounded-lg text-left",
        ),
        class_name="absolute z-30 flex flex-col p-1 mt-2 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl shadow-lg min-w-[150px]",
    )


def deleted_bubble(is_me: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("ban", class_name="h-3.5 w-3.5"),
            rx.el.span(
                "This message was deleted",
                class_name="text-xs italic",
            ),
            class_name="flex items-center gap-1.5 px-3 py-2 rounded-2xl bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 max-w-[75%]",
        ),
        class_name=rx.cond(is_me, "flex justify-end", "flex justify-start"),
    )


def message_meta(msg: Message, is_me: rx.Var) -> rx.Component:
    return rx.el.div(
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
        class_name="flex items-center gap-1 mt-1 justify-end",
    )


def message_bubble(msg: Message) -> rx.Component:
    is_me = msg["sender"] == "me"
    return rx.el.div(
        rx.cond(
            msg["deleted_for_everyone"],
            deleted_bubble(is_me),
            rx.el.div(
                rx.cond(
                    ~is_me,
                    avatar(msg["sender"], "h-8 w-8"),
                    rx.fragment(),
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            msg["text"],
                            class_name="text-sm whitespace-pre-wrap break-words",
                        ),
                        message_meta(msg, is_me),
                        class_name=rx.cond(
                            is_me,
                            "px-3 py-2 rounded-2xl bg-indigo-600 text-white rounded-br-md",
                            "px-3 py-2 rounded-2xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-bl-md",
                        ),
                    ),
                    rx.cond(
                        MessengerState.active_message_menu == msg["id"],
                        message_menu(msg),
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
