import reflex as rx
from app.states.auth_state import AuthState
from app.components.auth_layout import auth_layout


def processing_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                class_name="h-12 w-12 border-[3px] border-indigo-200 dark:border-indigo-900 border-t-indigo-600 rounded-full animate-spin mx-auto mb-5"
            ),
            rx.el.h2(
                "Signing you in...",
                class_name="text-xl font-bold text-gray-900 dark:text-white mb-1 text-center",
            ),
            rx.el.p(
                "Completing your Google authentication.",
                class_name="text-sm text-gray-500 dark:text-gray-400 text-center",
            ),
            class_name="py-8",
        ),
    )


def success_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "circle-check",
                class_name="h-7 w-7 text-green-600 dark:text-green-400",
            ),
            class_name="h-14 w-14 rounded-2xl bg-green-50 dark:bg-green-950/40 flex items-center justify-center mx-auto mb-5",
        ),
        rx.el.h2(
            "You're signed in",
            class_name="text-xl font-bold text-gray-900 dark:text-white mb-1 text-center",
        ),
        rx.el.p(
            "Redirecting you now...",
            class_name="text-sm text-gray-500 dark:text-gray-400 text-center",
        ),
        class_name="py-6",
    )


def error_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                "triangle-alert",
                class_name="h-7 w-7 text-red-600 dark:text-red-400",
            ),
            class_name="h-14 w-14 rounded-2xl bg-red-50 dark:bg-red-950/40 flex items-center justify-center mx-auto mb-5",
        ),
        rx.el.h2(
            "Sign-in failed",
            class_name="text-xl font-bold text-gray-900 dark:text-white mb-2 text-center",
        ),
        rx.el.p(
            rx.cond(
                AuthState.oauth_callback_error != "",
                AuthState.oauth_callback_error,
                "We couldn't complete your Google sign-in.",
            ),
            class_name="text-sm text-gray-500 dark:text-gray-400 text-center mb-6",
        ),
        rx.el.button(
            rx.icon("rotate-ccw", class_name="h-4 w-4"),
            rx.el.span("Back to sign in", class_name="text-sm font-semibold"),
            on_click=AuthState.retry_from_callback,
            class_name="flex items-center justify-center gap-2 w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl transition-colors",
        ),
    )


def oauth_callback_card() -> rx.Component:
    return rx.el.div(
        rx.match(
            AuthState.oauth_callback_status,
            ("processing", processing_view()),
            ("success", success_view()),
            ("error", error_view()),
            processing_view(),
        ),
        class_name="p-8 bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-2xl",
    )


def oauth_callback_page() -> rx.Component:
    return auth_layout(oauth_callback_card())
