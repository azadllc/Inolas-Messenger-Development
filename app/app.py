import reflex as rx
from app.deploy_setup import ensure_deployment_files
from app.states.auth_state import AuthState
from app.components.auth_layout import auth_layout
from app.components.auth_forms import auth_card
from app.components.onboarding_flow import onboarding_card
from app.components.home_layout import home_layout
from app.components.oauth_callback import oauth_callback_page

# Materialize the real root-level deployment files (Dockerfile, start.sh,
# Caddyfile, host configs, .env.example, DEPLOYMENT.md, vercel.json) from the
# canonical sources in app/deploy/. Non-destructive: existing non-empty files
# are kept. Nothing about the app's UI, routes or auth behavior is affected.
ensure_deployment_files()


def verifying_screen() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                class_name="h-8 w-8 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4"
            ),
            rx.el.p(
                "Checking your session...",
                class_name="text-sm text-gray-500",
            ),
            class_name="text-center",
        ),
        class_name="min-h-screen flex items-center justify-center bg-white font-['Inter']",
    )


def redirecting_screen() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                class_name="h-8 w-8 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4"
            ),
            rx.el.p("Redirecting...", class_name="text-sm text-gray-500"),
            class_name="text-center",
        ),
        on_mount=rx.redirect("/"),
        class_name="min-h-screen flex items-center justify-center bg-white font-['Inter']",
    )


def index() -> rx.Component:
    return rx.cond(
        AuthState.session_verifying,
        verifying_screen(),
        rx.cond(
            AuthState.is_authenticated,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        class_name="h-8 w-8 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-4"
                    ),
                    rx.el.p(
                        "Taking you in...",
                        class_name="text-sm text-gray-500",
                    ),
                    class_name="text-center",
                ),
                on_mount=rx.redirect("/home"),
                class_name="min-h-screen flex items-center justify-center bg-white font-['Inter']",
            ),
            auth_layout(auth_card()),
        ),
    )


def onboarding() -> rx.Component:
    return auth_layout(onboarding_card())


def home() -> rx.Component:
    return rx.cond(
        AuthState.session_verifying,
        verifying_screen(),
        rx.cond(
            AuthState.is_authenticated,
            home_layout(),
            redirecting_screen(),
        ),
    )


# Line 88 se lekar 100 tak ke block ko aise badlein:
app = rx.App(
    admin_dash=False,  # 🌟 Yeh line yahan pehle block ke andar aayegi!
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://googleapis.com"),
        rx.el.link(
            rel="preconnect", href="https://gstatic.com", cross_origin=""
        ),
        rx.el.link(
            href="https://googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
            rel="stylesheet",
        ),
    ],
)
