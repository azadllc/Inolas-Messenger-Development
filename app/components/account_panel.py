import reflex as rx
from app.states.auth_state import AuthState
from app.components.theme_toggle import theme_toggle


def profile_card() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                AuthState.user_avatar_seed.upper()[0:1],
                class_name="text-white font-bold text-2xl",
            ),
            class_name="h-16 w-16 rounded-full bg-indigo-500 flex items-center justify-center shrink-0",
        ),
        rx.el.div(
            rx.el.p(
                AuthState.user_display_name,
                class_name="text-base font-bold text-gray-900 dark:text-white truncate",
            ),
            rx.el.p(
                f"@{AuthState.user_username}",
                class_name="text-sm font-medium text-indigo-600 dark:text-indigo-400 truncate",
            ),
            rx.cond(
                AuthState.user_bio != "",
                rx.el.p(
                    AuthState.user_bio,
                    class_name="text-xs text-gray-600 dark:text-gray-300 mt-1",
                ),
                rx.fragment(),
            ),
            class_name="flex-1 min-w-0",
        ),
        class_name="flex items-center gap-4 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950",
    )


def info_row(icon: str, label: str, value: rx.Var | str) -> rx.Component:
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
                class_name="text-xs font-medium text-gray-500 dark:text-gray-400",
            ),
            rx.el.p(
                value,
                class_name="text-sm font-semibold text-gray-900 dark:text-white truncate",
            ),
            class_name="flex-1 min-w-0",
        ),
        class_name="flex items-center gap-3 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950",
    )


def appearance_row() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "sun-moon",
                class_name="h-4 w-4 text-gray-500 dark:text-gray-400",
            ),
            class_name="h-10 w-10 rounded-xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center shrink-0",
        ),
        rx.el.div(
            rx.el.p(
                "Appearance",
                class_name="text-sm font-semibold text-gray-900 dark:text-white",
            ),
            rx.el.p(
                "Switch between the light and dark interface",
                class_name="text-xs text-gray-500 dark:text-gray-400 mt-0.5",
            ),
            class_name="flex-1 min-w-0",
        ),
        theme_toggle(),
        class_name="flex items-center gap-3 p-4 rounded-2xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950",
    )


def account_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Account",
                class_name="text-2xl font-bold text-gray-900 dark:text-white",
            ),
            rx.el.p(
                "Your Inolas profile and app preferences",
                class_name="text-sm text-gray-500 dark:text-gray-400 mt-1",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.h2(
                "Profile",
                class_name="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3",
            ),
            rx.el.div(
                profile_card(),
                info_row("at-sign", "Username", f"@{AuthState.user_username}"),
                rx.cond(
                    AuthState.user_email != "",
                    info_row("mail", "Email", AuthState.user_email),
                    rx.fragment(),
                ),
                rx.cond(
                    AuthState.user_phone != "",
                    info_row("phone", "Phone", AuthState.user_phone),
                    rx.fragment(),
                ),
                class_name="flex flex-col gap-2",
            ),
            class_name="mb-8",
        ),
        rx.el.div(
            rx.el.h2(
                "Preferences",
                class_name="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3",
            ),
            appearance_row(),
            class_name="mb-8",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("log-out", class_name="h-4 w-4"),
                rx.el.span("Sign out", class_name="text-sm font-semibold"),
                on_click=AuthState.logout,
                class_name="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors",
            ),
            class_name="pb-6",
        ),
        class_name="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-black",
    )
