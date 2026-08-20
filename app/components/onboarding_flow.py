import reflex as rx
from app.states.auth_state import AuthState
from app.components.forms import error_banner, primary_button


def step_indicator() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                class_name=rx.cond(
                    AuthState.onboarding_step >= 1,
                    "h-1.5 flex-1 rounded-full bg-indigo-600",
                    "h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-800",
                ),
            ),
            rx.el.div(
                class_name=rx.cond(
                    AuthState.onboarding_step >= 2,
                    "h-1.5 flex-1 rounded-full bg-indigo-600",
                    "h-1.5 flex-1 rounded-full bg-gray-200 dark:bg-gray-800",
                ),
            ),
            class_name="flex gap-2 mb-6",
        ),
        rx.el.p(
            rx.cond(
                AuthState.onboarding_step == 1, "Step 1 of 2", "Step 2 of 2"
            ),
            class_name="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1",
        ),
    )


def username_step() -> rx.Component:
    return rx.el.div(
        step_indicator(),
        rx.el.h2(
            "Choose your username",
            class_name="text-2xl font-bold text-gray-900 dark:text-white mb-1",
        ),
        rx.el.p(
            "This is how people find and mention you on Inolas.",
            class_name="text-sm text-gray-500 dark:text-gray-400 mb-6",
        ),
        error_banner(),
        rx.el.div(
            rx.el.label(
                "Username",
                class_name="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "@", class_name="text-gray-400 text-sm font-medium"
                    ),
                    class_name="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none",
                ),
                rx.el.input(
                    placeholder="yourname",
                    default_value=AuthState.username_input,
                    on_change=[
                        AuthState.set_username_input,
                        AuthState.check_username.debounce(500),
                    ],
                    class_name="w-full pl-8 pr-10 py-2.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm",
                ),
                rx.el.div(
                    rx.cond(
                        AuthState.username_checking,
                        rx.el.div(
                            class_name="h-4 w-4 border-2 border-gray-300 border-t-indigo-600 rounded-full animate-spin"
                        ),
                        rx.cond(
                            AuthState.username_available.to(bool)
                            & AuthState.username_valid_format,
                            rx.icon(
                                "circle-check",
                                class_name="h-4 w-4 text-green-500",
                            ),
                            rx.cond(
                                (AuthState.username_available == False)
                                & AuthState.username_valid_format,
                                rx.icon(
                                    "circle-x",
                                    class_name="h-4 w-4 text-red-500",
                                ),
                                rx.fragment(),
                            ),
                        ),
                    ),
                    class_name="absolute right-3 top-1/2 -translate-y-1/2",
                ),
                class_name="relative",
            ),
            rx.el.p(
                AuthState.username_hint,
                class_name=rx.cond(
                    AuthState.username_valid_format,
                    "text-xs text-green-600 dark:text-green-400 mt-1.5 font-medium",
                    "text-xs text-gray-500 dark:text-gray-400 mt-1.5",
                ),
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.p(
                "Preview",
                class_name="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.span(
                            AuthState.user_email.upper()[0:1],
                            class_name="text-white font-semibold text-sm",
                        ),
                        class_name="h-10 w-10 rounded-full bg-indigo-500 flex items-center justify-center shrink-0",
                    ),
                    rx.el.div(
                        rx.el.p(
                            rx.cond(
                                AuthState.username_input != "",
                                f"@{AuthState.username_input}",
                                "@yourname",
                            ),
                            class_name="text-sm font-semibold text-gray-900 dark:text-white",
                        ),
                        rx.el.p(
                            "New on Inolas",
                            class_name="text-xs text-gray-500 dark:text-gray-400",
                        ),
                    ),
                    class_name="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl",
                ),
                class_name="mb-6",
            ),
        ),
        primary_button("Continue", AuthState.submit_username, "arrow-right"),
    )


def profile_step() -> rx.Component:
    return rx.el.div(
        step_indicator(),
        rx.el.h2(
            "Set up your profile",
            class_name="text-2xl font-bold text-gray-900 dark:text-white mb-1",
        ),
        rx.el.p(
            "Add a display name and short bio so friends recognize you.",
            class_name="text-sm text-gray-500 dark:text-gray-400 mb-6",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    AuthState.user_email.upper()[0:1],
                    class_name="text-white font-bold text-2xl",
                ),
                class_name="h-20 w-20 rounded-full bg-indigo-500 flex items-center justify-center",
            ),
            rx.el.button(
                rx.icon("camera", class_name="h-3.5 w-3.5"),
                rx.el.span("Change photo", class_name="text-xs font-medium"),
                type="button",
                class_name="flex items-center gap-1.5 mt-3 px-3 py-1.5 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors",
            ),
            class_name="flex flex-col items-center mb-6",
        ),
        rx.el.div(
            rx.el.label(
                "Display name",
                class_name="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5",
            ),
            rx.el.input(
                placeholder="Your name",
                default_value=AuthState.display_name_input,
                on_change=AuthState.set_display_name.debounce(200),
                class_name="w-full px-3 py-2.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm",
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "About",
                class_name="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5",
            ),
            rx.el.textarea(
                placeholder="Tell people a bit about you...",
                default_value=AuthState.bio_input,
                on_change=AuthState.set_bio.debounce(200),
                rows=3,
                class_name="w-full px-3 py-2.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm resize-none",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.el.button(
                "Skip",
                on_click=AuthState.skip_profile,
                type="button",
                class_name="flex-1 py-3 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-xl text-sm font-semibold transition-colors",
            ),
            rx.el.button(
                "Finish setup",
                on_click=AuthState.submit_profile,
                type="button",
                class_name="flex-1 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-sm font-semibold transition-colors",
            ),
            class_name="flex gap-3",
        ),
    )


def onboarding_card() -> rx.Component:
    return rx.el.div(
        rx.match(
            AuthState.onboarding_step,
            (1, username_step()),
            (2, profile_step()),
            username_step(),
        ),
        class_name="p-8 bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-2xl",
    )
