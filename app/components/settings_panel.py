import reflex as rx
from app.states.messenger_state import MessengerState, UserData
from app.components.messenger_widgets import avatar


def toggle_row(
    icon: str, label: str, desc: str, value: rx.Var, on_toggle
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                icon, class_name="h-4 w-4 text-gray-500 dark:text-gray-400"
            ),
            class_name="h-10 w-10 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center shrink-0",
        ),
        rx.el.div(
            rx.el.p(
                label,
                class_name="text-sm font-semibold text-gray-900 dark:text-white",
            ),
            rx.el.p(
                desc,
                class_name="text-xs text-gray-500 dark:text-gray-400 mt-0.5",
            ),
            class_name="flex-1",
        ),
        rx.el.button(
            rx.el.div(
                class_name=rx.cond(
                    value,
                    "h-5 w-5 rounded-full bg-white shadow translate-x-5 transition-transform",
                    "h-5 w-5 rounded-full bg-white shadow translate-x-0 transition-transform",
                ),
            ),
            on_click=on_toggle,
            class_name=rx.cond(
                value,
                "w-11 h-6 rounded-full bg-indigo-600 p-0.5 flex items-center transition-colors",
                "w-11 h-6 rounded-full bg-gray-300 dark:bg-gray-700 p-0.5 flex items-center transition-colors",
            ),
        ),
        class_name="flex items-center gap-3 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950",
    )


def select_row(
    icon: str, label: str, desc: str, value: rx.Var, on_change, key: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    icon, class_name="h-4 w-4 text-gray-500 dark:text-gray-400"
                ),
                class_name="h-10 w-10 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center shrink-0",
            ),
            rx.el.div(
                rx.el.p(
                    label,
                    class_name="text-sm font-semibold text-gray-900 dark:text-white",
                ),
                rx.el.p(
                    desc,
                    class_name="text-xs text-gray-500 dark:text-gray-400 mt-0.5",
                ),
                class_name="flex-1",
            ),
            class_name="flex items-center gap-3 flex-1",
        ),
        rx.el.div(
            rx.el.select(
                rx.el.option("Everyone", value="everyone"),
                rx.el.option("Contacts", value="contacts"),
                rx.el.option("Nobody", value="nobody"),
                default_value=value,
                on_change=lambda v: MessengerState.set_privacy(key, v),
                class_name="appearance-none pl-3 pr-8 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm font-medium text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500",
            ),
            rx.icon(
                "chevron-down",
                class_name="h-3.5 w-3.5 text-gray-500 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none",
            ),
            class_name="relative",
        ),
        class_name="flex items-center gap-3 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950",
    )


def blocked_user_card(user: UserData) -> rx.Component:
    return rx.el.div(
        avatar(user["avatar_seed"], "h-10 w-10"),
        rx.el.div(
            rx.el.p(
                user["display_name"],
                class_name="text-sm font-semibold text-gray-900 dark:text-white",
            ),
            rx.el.p(
                f"@{user['username']}",
                class_name="text-xs text-gray-500 dark:text-gray-400",
            ),
            class_name="flex-1 min-w-0",
        ),
        rx.el.button(
            "Unblock",
            on_click=lambda: MessengerState.unblock_user(user["username"]),
            class_name="px-3 py-1.5 text-xs font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/40 rounded-lg transition-colors",
        ),
        class_name="flex items-center gap-3 p-3 rounded-xl border border-gray-200 dark:border-gray-800",
    )


def settings_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Settings & Privacy",
                class_name="text-2xl font-bold text-gray-900 dark:text-white",
            ),
            rx.el.p(
                "Control who can see your info and interact with you",
                class_name="text-sm text-gray-500 dark:text-gray-400 mt-1",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.h2(
                "Privacy",
                class_name="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3",
            ),
            rx.el.div(
                toggle_row(
                    "at-sign",
                    "Username visibility",
                    "Allow others to find you via your @username",
                    MessengerState.privacy_username_visible,
                    lambda: MessengerState.toggle_privacy_bool(
                        "username_visible"
                    ),
                ),
                select_row(
                    "clock",
                    "Last seen",
                    "Who can see when you were last online",
                    MessengerState.privacy_last_seen,
                    MessengerState.set_privacy,
                    "last_seen",
                ),
                toggle_row(
                    "wifi",
                    "Online status",
                    "Show a green dot when you're active",
                    MessengerState.privacy_online_status,
                    lambda: MessengerState.toggle_privacy_bool("online_status"),
                ),
                select_row(
                    "camera",
                    "Profile photo",
                    "Who can see your profile picture",
                    MessengerState.privacy_profile_photo,
                    MessengerState.set_privacy,
                    "profile_photo",
                ),
                toggle_row(
                    "check-check",
                    "Read receipts",
                    "Let others know when you've read their messages",
                    MessengerState.privacy_read_receipts,
                    lambda: MessengerState.toggle_privacy_bool("read_receipts"),
                ),
                class_name="flex flex-col gap-2",
            ),
            class_name="mb-8",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Blocked users",
                    class_name="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider",
                ),
                rx.el.span(
                    MessengerState.blocked_users.length(),
                    class_name="text-xs font-semibold text-gray-600 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full",
                ),
                class_name="flex items-center gap-2 mb-3",
            ),
            rx.cond(
                MessengerState.blocked_users.length() == 0,
                rx.el.div(
                    rx.icon(
                        "shield-check",
                        class_name="h-8 w-8 text-gray-300 mx-auto mb-2",
                    ),
                    rx.el.p(
                        "You haven't blocked anyone",
                        class_name="text-sm font-medium text-gray-500 text-center",
                    ),
                    rx.el.p(
                        "Blocked users won't be able to message you",
                        class_name="text-xs text-gray-400 text-center mt-1",
                    ),
                    class_name="p-8 border border-dashed border-gray-200 dark:border-gray-800 rounded-2xl",
                ),
                rx.el.div(
                    rx.foreach(
                        MessengerState.blocked_users_data, blocked_user_card
                    ),
                    class_name="flex flex-col gap-2",
                ),
            ),
            class_name="mb-8",
        ),
        class_name="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-black",
    )
