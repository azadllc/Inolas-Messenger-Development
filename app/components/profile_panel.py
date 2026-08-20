import reflex as rx
from app.states.messenger_state import MessengerState


def action_button(
    icon: str, label: str, on_click, variant: str = "default"
) -> rx.Component:
    class_map = {
        "primary": "flex flex-col items-center gap-1.5 p-3 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white transition-colors flex-1",
        "danger": "flex flex-col items-center gap-1.5 p-3 rounded-xl bg-red-50 dark:bg-red-950/40 hover:bg-red-100 dark:hover:bg-red-950 text-red-600 dark:text-red-400 transition-colors flex-1",
        "default": "flex flex-col items-center gap-1.5 p-3 rounded-xl bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 transition-colors flex-1",
    }
    return rx.el.button(
        rx.icon(icon, class_name="h-5 w-5"),
        rx.el.span(label, class_name="text-xs font-semibold"),
        on_click=on_click,
        class_name=class_map.get(variant, class_map["default"]),
    )


def info_row(icon: str, label: str, value: rx.Var | str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-gray-400"),
            class_name="h-8 w-8 rounded-lg bg-gray-100 dark:bg-gray-800 flex items-center justify-center shrink-0",
        ),
        rx.el.div(
            rx.el.p(
                label,
                class_name="text-xs font-medium text-gray-500 dark:text-gray-400",
            ),
            rx.el.p(
                value,
                class_name="text-sm font-semibold text-gray-900 dark:text-white",
            ),
            class_name="flex-1 min-w-0",
        ),
        class_name="flex items-center gap-3 p-3 rounded-xl border border-gray-200 dark:border-gray-800",
    )


def profile_panel() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Profile",
                    class_name="text-base font-bold text-gray-900 dark:text-white",
                ),
                rx.el.button(
                    rx.icon("x", class_name="h-4 w-4"),
                    on_click=MessengerState.close_profile,
                    class_name="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800",
                ),
                class_name="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    MessengerState.active_profile[
                                        "avatar_seed"
                                    ].upper()[0:1],
                                    class_name="text-white font-bold text-3xl",
                                ),
                                class_name="h-24 w-24 rounded-full bg-indigo-500 flex items-center justify-center",
                            ),
                            rx.cond(
                                MessengerState.active_profile["online"],
                                rx.el.span(
                                    class_name="absolute bottom-1 right-1 h-4 w-4 rounded-full bg-green-500 border-2 border-white dark:border-gray-950"
                                ),
                                rx.fragment(),
                            ),
                            class_name="relative",
                        ),
                        rx.el.h3(
                            MessengerState.active_profile["display_name"],
                            class_name="text-xl font-bold text-gray-900 dark:text-white mt-3",
                        ),
                        rx.el.p(
                            f"@{MessengerState.active_profile['username']}",
                            class_name="text-sm text-indigo-600 dark:text-indigo-400 font-medium",
                        ),
                        rx.cond(
                            MessengerState.active_profile["online"],
                            rx.el.p(
                                "● Online now",
                                class_name="text-xs font-medium text-green-600 dark:text-green-400 mt-1",
                            ),
                            rx.el.p(
                                MessengerState.active_profile["last_seen"],
                                class_name="text-xs text-gray-500 mt-1",
                            ),
                        ),
                        class_name="flex flex-col items-center py-6",
                    ),
                    rx.el.div(
                        action_button(
                            "message-circle",
                            "Message",
                            lambda: MessengerState.message_user(
                                MessengerState.active_profile["username"]
                            ),
                            "primary",
                        ),
                        action_button(
                            "user-round",
                            "View profile",
                            MessengerState.close_profile,
                        ),
                        class_name="flex gap-2 px-4",
                    ),
                    rx.el.div(
                        rx.cond(
                            MessengerState.active_profile["bio"] != "",
                            rx.el.div(
                                rx.el.p(
                                    "About",
                                    class_name="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2",
                                ),
                                rx.el.p(
                                    MessengerState.active_profile["bio"],
                                    class_name="text-sm text-gray-700 dark:text-gray-300 leading-relaxed",
                                ),
                                class_name="p-4 rounded-xl border border-gray-200 dark:border-gray-800 mb-3",
                            ),
                            rx.fragment(),
                        ),
                        info_row(
                            "at-sign",
                            "Username",
                            f"@{MessengerState.active_profile['username']}",
                        ),
                        rx.el.div(class_name="h-2"),
                        info_row(
                            "clock",
                            "Last seen",
                            MessengerState.active_profile["last_seen"],
                        ),
                        class_name="px-4 mt-6",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Actions",
                            class_name="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2",
                        ),
                        rx.cond(
                            MessengerState.is_active_user_blocked,
                            rx.el.button(
                                rx.icon("user-check", class_name="h-4 w-4"),
                                rx.el.span(
                                    "Unblock user",
                                    class_name="text-sm font-semibold",
                                ),
                                on_click=lambda: MessengerState.unblock_user(
                                    MessengerState.active_profile["username"]
                                ),
                                class_name="flex items-center gap-2 w-full p-3 rounded-xl bg-green-50 dark:bg-green-950/40 hover:bg-green-100 text-green-600 dark:text-green-400 transition-colors mb-2",
                            ),
                            rx.el.button(
                                rx.icon("ban", class_name="h-4 w-4"),
                                rx.el.span(
                                    "Block user",
                                    class_name="text-sm font-semibold",
                                ),
                                on_click=lambda: MessengerState.block_user(
                                    MessengerState.active_profile["username"]
                                ),
                                class_name="flex items-center gap-2 w-full p-3 rounded-xl bg-red-50 dark:bg-red-950/40 hover:bg-red-100 text-red-600 dark:text-red-400 transition-colors mb-2",
                            ),
                        ),
                        rx.el.button(
                            rx.icon("flag", class_name="h-4 w-4"),
                            rx.el.span(
                                "Report user",
                                class_name="text-sm font-semibold",
                            ),
                            on_click=lambda: MessengerState.report_user(
                                MessengerState.active_profile["username"]
                            ),
                            class_name="flex items-center gap-2 w-full p-3 rounded-xl border border-gray-200 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-900 text-gray-700 dark:text-gray-200 transition-colors",
                        ),
                        class_name="px-4 mt-6 pb-6",
                    ),
                    class_name="flex-1 overflow-y-auto",
                ),
                class_name="flex-1 overflow-y-auto",
            ),
            class_name="flex flex-col h-full",
        ),
        class_name=rx.cond(
            MessengerState.show_profile_panel,
            "flex flex-col w-full lg:w-96 h-full border-l border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 shrink-0 absolute lg:relative right-0 top-0 z-20",
            "hidden",
        ),
    )
