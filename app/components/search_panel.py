import reflex as rx
from app.states.messenger_state import MessengerState, UserData
from app.components.messenger_widgets import avatar


def search_result_card(user: UserData) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                avatar(user["avatar_seed"], "h-12 w-12"),
                rx.cond(
                    user["online"],
                    rx.el.span(
                        class_name="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full bg-green-500 border-2 border-white dark:border-gray-950"
                    ),
                    rx.fragment(),
                ),
                class_name="relative shrink-0",
            ),
            rx.el.div(
                rx.el.p(
                    user["display_name"],
                    class_name="text-sm font-semibold text-gray-900 dark:text-white truncate",
                ),
                rx.el.p(
                    f"@{user['username']}",
                    class_name="text-xs text-gray-500 dark:text-gray-400 truncate",
                ),
                rx.el.p(
                    user["bio"],
                    class_name="text-xs text-gray-600 dark:text-gray-300 truncate mt-1",
                ),
                rx.el.div(
                    rx.cond(
                        user["online"],
                        rx.el.span(
                            "● Online",
                            class_name="text-xs font-medium text-green-600 dark:text-green-400",
                        ),
                        rx.el.span(
                            user["last_seen"],
                            class_name="text-xs text-gray-400",
                        ),
                    ),
                    class_name="mt-1",
                ),
                class_name="flex-1 min-w-0",
            ),
            class_name="flex items-start gap-3 flex-1 min-w-0",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("user-round", class_name="h-4 w-4"),
                rx.el.span("View", class_name="text-xs font-semibold"),
                on_click=lambda: MessengerState.open_profile(user["username"]),
                class_name="flex items-center gap-1.5 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-200 rounded-lg transition-colors",
            ),
            rx.el.button(
                rx.icon("message-circle", class_name="h-4 w-4"),
                rx.el.span("Message", class_name="text-xs font-semibold"),
                on_click=lambda: MessengerState.message_user(user["username"]),
                class_name="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors",
            ),
            class_name="flex items-center gap-2 shrink-0",
        ),
        class_name="flex items-center gap-3 p-4 border border-gray-200 dark:border-gray-800 rounded-2xl hover:border-indigo-200 dark:hover:border-indigo-800 transition-colors bg-white dark:bg-gray-950",
    )


def search_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Discover people",
                class_name="text-2xl font-bold text-gray-900 dark:text-white",
            ),
            rx.el.p(
                "Find anyone on Inolas by their @username or display name",
                class_name="text-sm text-gray-500 dark:text-gray-400 mt-1",
            ),
            class_name="mb-6",
        ),
        rx.el.div(
            rx.icon(
                "search",
                class_name="h-5 w-5 text-gray-400 absolute left-4 top-1/2 -translate-y-1/2",
            ),
            rx.el.input(
                placeholder="Search @username or name...",
                default_value=MessengerState.search_query,
                on_change=MessengerState.set_search_query.debounce(200),
                class_name="w-full pl-12 pr-4 py-3 bg-white dark:bg-gray-950 border border-gray-200 dark:border-gray-800 rounded-2xl text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent",
            ),
            class_name="relative mb-6",
        ),
        rx.cond(
            MessengerState.search_query == "",
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "users",
                        class_name="h-8 w-8 text-indigo-600 dark:text-indigo-400",
                    ),
                    class_name="h-16 w-16 rounded-2xl bg-indigo-50 dark:bg-indigo-950 flex items-center justify-center mx-auto mb-4",
                ),
                rx.el.h3(
                    "Start typing to search",
                    class_name="text-lg font-semibold text-gray-900 dark:text-white text-center mb-1",
                ),
                rx.el.p(
                    "Try searching for @emma, @marcus, or any friend's name",
                    class_name="text-sm text-gray-500 dark:text-gray-400 text-center",
                ),
                class_name="py-16",
            ),
            rx.cond(
                MessengerState.search_results.length() == 0,
                rx.el.div(
                    rx.icon(
                        "search-x",
                        class_name="h-10 w-10 text-gray-300 mx-auto mb-3",
                    ),
                    rx.el.p(
                        "No results found",
                        class_name="text-sm font-medium text-gray-500 text-center",
                    ),
                    class_name="py-16",
                ),
                rx.el.div(
                    rx.el.p(
                        f"{MessengerState.search_results.length()} result(s)",
                        class_name="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-3",
                    ),
                    rx.el.div(
                        rx.foreach(
                            MessengerState.search_results, search_result_card
                        ),
                        class_name="flex flex-col gap-2",
                    ),
                ),
            ),
        ),
        class_name="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-black",
    )
