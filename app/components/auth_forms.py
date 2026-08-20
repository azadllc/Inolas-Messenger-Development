import reflex as rx
from app.states.auth_state import AuthState
from app.components.forms import (
    text_field,
    error_banner,
    success_banner,
    primary_button,
)


def divider() -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name="flex-1 h-px bg-gray-200 dark:bg-gray-800"),
        rx.el.span(
            "or",
            class_name="text-xs text-gray-500 dark:text-gray-400 font-medium",
        ),
        rx.el.div(class_name="flex-1 h-px bg-gray-200 dark:bg-gray-800"),
        class_name="flex items-center gap-3 my-5",
    )


def social_buttons() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.el.div(
                rx.image(
                    src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg",
                    class_name="h-4 w-4",
                ),
                rx.el.span(
                    "Continue with Google",
                    class_name="text-sm font-medium text-gray-700 dark:text-gray-200",
                ),
                class_name="flex items-center justify-center gap-2",
            ),
            on_click=AuthState.google_signin,
            disabled=AuthState.is_loading,
            type="button",
            class_name="w-full py-2.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors disabled:opacity-60",
        ),
        rx.cond(
            AuthState.oauth_redirect_target != "",
            rx.el.p(
                f"Redirecting to: {AuthState.oauth_redirect_target}",
                class_name="text-[10px] text-gray-400 text-center mt-1",
            ),
            rx.fragment(),
        ),
        rx.el.button(
            rx.el.div(
                rx.icon(
                    "phone",
                    class_name="h-4 w-4 text-gray-700 dark:text-gray-200",
                ),
                rx.el.span(
                    "Continue with phone",
                    class_name="text-sm font-medium text-gray-700 dark:text-gray-200",
                ),
                class_name="flex items-center justify-center gap-2",
            ),
            on_click=lambda: AuthState.set_mode("phone"),
            type="button",
            class_name="w-full py-2.5 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors",
        ),
        class_name="flex flex-col gap-2.5",
    )


def login_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Welcome back",
            class_name="text-2xl font-bold text-gray-900 dark:text-white mb-1",
        ),
        rx.el.p(
            "Sign in to continue to Inolas",
            class_name="text-sm text-gray-500 dark:text-gray-400 mb-6",
        ),
        error_banner(),
        success_banner(),
        text_field(
            "Email",
            "you@example.com",
            AuthState.email_input,
            AuthState.set_email,
            "email",
            "mail",
        ),
        text_field(
            "Password",
            "Enter your password",
            AuthState.password_input,
            AuthState.set_password,
            "password",
            "lock",
        ),
        rx.el.div(
            rx.el.a(
                "Forgot password?",
                href="#",
                class_name="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:underline",
            ),
            class_name="flex justify-end mb-4",
        ),
        primary_button("Sign in", AuthState.login_email, "log-in"),
        divider(),
        social_buttons(),
        rx.el.p(
            "Don't have an account? ",
            rx.el.button(
                "Sign up",
                on_click=lambda: AuthState.set_mode("register"),
                class_name="font-semibold text-indigo-600 dark:text-indigo-400 hover:underline",
            ),
            class_name="text-sm text-gray-600 dark:text-gray-400 text-center mt-6",
        ),
    )


def register_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Create your account",
            class_name="text-2xl font-bold text-gray-900 dark:text-white mb-1",
        ),
        rx.el.p(
            "Join millions on Inolas Messenger",
            class_name="text-sm text-gray-500 dark:text-gray-400 mb-6",
        ),
        error_banner(),
        text_field(
            "Email",
            "you@example.com",
            AuthState.email_input,
            AuthState.set_email,
            "email",
            "mail",
        ),
        text_field(
            "Password",
            "At least 6 characters",
            AuthState.password_input,
            AuthState.set_password,
            "password",
            "lock",
        ),
        text_field(
            "Confirm password",
            "Re-enter password",
            AuthState.confirm_password_input,
            AuthState.set_confirm_password,
            "password",
            "lock",
        ),
        primary_button("Create account", AuthState.register_email, "user-plus"),
        divider(),
        social_buttons(),
        rx.el.p(
            "Already have an account? ",
            rx.el.button(
                "Sign in",
                on_click=lambda: AuthState.set_mode("login"),
                class_name="font-semibold text-indigo-600 dark:text-indigo-400 hover:underline",
            ),
            class_name="text-sm text-gray-600 dark:text-gray-400 text-center mt-6",
        ),
    )


def phone_form() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.icon("arrow-left", class_name="h-4 w-4"),
            rx.el.span("Back", class_name="text-sm font-medium"),
            on_click=lambda: AuthState.set_mode("login"),
            class_name="flex items-center gap-1.5 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-6 transition-colors",
        ),
        rx.el.h2(
            "Sign in with phone",
            class_name="text-2xl font-bold text-gray-900 dark:text-white mb-1",
        ),
        rx.el.p(
            "We'll send you a one-time code",
            class_name="text-sm text-gray-500 dark:text-gray-400 mb-6",
        ),
        error_banner(),
        success_banner(),
        rx.cond(
            ~AuthState.otp_sent,
            rx.el.div(
                text_field(
                    "Phone number",
                    "+1 555 123 4567",
                    AuthState.phone_input,
                    AuthState.set_phone,
                    "tel",
                    "phone",
                ),
                primary_button("Send code", AuthState.send_otp, "send"),
            ),
            rx.el.div(
                text_field(
                    "Verification code",
                    "6-digit code",
                    AuthState.otp_input,
                    AuthState.set_otp,
                    "text",
                    "shield",
                ),
                primary_button(
                    "Verify & continue", AuthState.verify_otp, "check"
                ),
                rx.el.button(
                    "Resend code",
                    on_click=AuthState.send_otp,
                    type="button",
                    class_name="w-full mt-2 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:underline",
                ),
            ),
        ),
    )


def auth_card() -> rx.Component:
    return rx.el.div(
        rx.match(
            AuthState.auth_mode,
            ("login", login_form()),
            ("register", register_form()),
            ("phone", phone_form()),
            login_form(),
        ),
        class_name="p-8 bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-2xl",
    )
