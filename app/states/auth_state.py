import reflex as rx
import re
import os
import logging
import asyncio
import traceback
from collections.abc import Mapping
from urllib.parse import parse_qs
from supabase import create_client, Client


_supabase_client: Client | None = None


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set")
        _supabase_client = create_client(url, key)
    return _supabase_client


def _is_real_str(v: object) -> bool:
    """Return True only when v is a real, non-empty string with meaningful content.

    Guards against LocalStorage proxies, default sentinels, and unset values
    that may accidentally look truthy when accessed on a fresh state instance.
    """
    if not isinstance(v, str):
        return False
    s = v.strip()
    if not s:
        return False
    low = s.lower()
    if low in ("none", "null", "undefined", "false", "0"):
        return False
    # Guard against obvious proxy/repr leakage
    if s.startswith("<") and s.endswith(">"):
        return False
    return True


def _normalize_callback_params(raw_value: object) -> dict[str, str]:
    if isinstance(raw_value, str):
        query_string = raw_value[1:] if raw_value.startswith("?") else raw_value
        parsed_values = parse_qs(query_string, keep_blank_values=True)
        return {
            str(key): str(values[-1]) if values else ""
            for key, values in parsed_values.items()
        }
    if isinstance(raw_value, Mapping):
        return {
            str(key): (
                str(value[-1])
                if isinstance(value, (list, tuple)) and value
                else ""
                if isinstance(value, (list, tuple))
                else str(value)
            )
            for key, value in raw_value.items()
        }
    return {}


def _friendly_error(e: Exception) -> str:
    msg = str(e)
    low = msg.lower()
    if "invalid login" in low or "invalid_credentials" in low:
        return "Invalid email or password"
    if "already registered" in low or "user already" in low:
        return "An account with this email already exists"
    if "email not confirmed" in low:
        return "Please confirm your email before signing in"
    if "rate limit" in low:
        return "Too many attempts. Please try again later."
    if "invalid token" in low or "otp" in low and "invalid" in low:
        return "Invalid or expired verification code"
    if "phone" in low and "invalid" in low:
        return "Please enter a valid phone number"
    if len(msg) > 160:
        return "Something went wrong. Please try again."
    return msg or "Something went wrong. Please try again."


class AuthState(rx.State):
    # Session
    is_authenticated: bool = False
    user_id: str = rx.LocalStorage("")
    access_token: str = rx.LocalStorage("")
    refresh_token: str = rx.LocalStorage("")
    user_email: str = ""
    user_phone: str = ""
    user_display_name: str = ""
    user_username: str = ""
    user_bio: str = ""
    user_avatar_seed: str = ""
    auth_method: str = ""

    # UI state
    auth_mode: str = "login"  # login | register | phone
    is_loading: bool = False
    error_message: str = ""
    success_message: str = ""
    theme_mode: str = "light"

    # Form fields
    email_input: str = ""
    password_input: str = ""
    confirm_password_input: str = ""
    phone_input: str = ""
    otp_input: str = ""
    otp_sent: bool = False

    # Onboarding
    onboarding_step: int = 0
    username_input: str = ""
    username_available: bool | None = None
    username_checking: bool = False
    display_name_input: str = ""
    bio_input: str = ""

    # Session verification tracking
    session_verifying: bool = True
    session_verified: bool = False

    @rx.event
    def toggle_theme(self):
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"

    @rx.event
    def set_mode(self, mode: str):
        self.auth_mode = mode
        self.error_message = ""
        self.success_message = ""
        self.otp_sent = False
        self.otp_input = ""

    @rx.event
    def set_email(self, v: str):
        self.email_input = v

    @rx.event
    def set_password(self, v: str):
        self.password_input = v

    @rx.event
    def set_confirm_password(self, v: str):
        self.confirm_password_input = v

    @rx.event
    def set_phone(self, v: str):
        self.phone_input = v

    @rx.event
    def set_otp(self, v: str):
        self.otp_input = v

    @rx.event
    def set_username_input(self, v: str):
        self.username_input = v.lower().strip()
        self.username_available = None

    @rx.event
    def set_display_name(self, v: str):
        self.display_name_input = v

    @rx.event
    def set_bio(self, v: str):
        self.bio_input = v

    @rx.var
    def username_valid_format(self) -> bool:
        if not self.username_input:
            return False
        if len(self.username_input) < 3 or len(self.username_input) > 20:
            return False
        return bool(re.match(r"^[a-z0-9_]+$", self.username_input))

    @rx.var
    def username_hint(self) -> str:
        if not self.username_input:
            return "3-20 characters, lowercase letters, numbers, underscores"
        if len(self.username_input) < 3:
            return "Too short (min 3 characters)"
        if len(self.username_input) > 20:
            return "Too long (max 20 characters)"
        if not re.match(r"^[a-z0-9_]+$", self.username_input):
            return "Only lowercase letters, numbers, and underscores"
        return "Looks good!"

    def _apply_session(self, session, user):
        if session is not None:
            self.access_token = getattr(session, "access_token", "") or ""
            self.refresh_token = getattr(session, "refresh_token", "") or ""
        if user is not None:
            self.user_id = getattr(user, "id", "") or ""
            self.user_email = getattr(user, "email", "") or self.user_email
            self.user_phone = getattr(user, "phone", "") or self.user_phone

    async def _load_profile(self) -> dict | None:
        if not self.user_id:
            return None
        try:
            sb = get_supabase()
            res = await asyncio.to_thread(
                lambda: (
                    sb.table("profiles")
                    .select("id,username,display_name,bio,avatar_url")
                    .eq("id", self.user_id)
                    .limit(1)
                    .execute()
                )
            )
            rows = res.data or []
            return rows[0] if rows else None
        except Exception as e:
            logging.exception(f"Error loading profile: {e}")
            return None

    @rx.event
    async def check_username(self):
        if not self.username_valid_format:
            return
        self.username_checking = True
        yield
        try:
            sb = get_supabase()
            uname = self.username_input
            res = await asyncio.to_thread(
                lambda: (
                    sb.table("profiles")
                    .select("id")
                    .eq("username", uname)
                    .limit(1)
                    .execute()
                )
            )
            self.username_available = len(res.data or []) == 0
        except Exception as e:
            logging.exception(f"Username check error: {e}")
            self.username_available = None
        finally:
            self.username_checking = False

    def _derive_username_candidate(self) -> str:
        base = ""
        if self.user_email and "@" in self.user_email:
            base = self.user_email.split("@")[0]
        elif self.user_phone:
            base = "user" + re.sub(r"\D", "", self.user_phone)[-6:]
        base = re.sub(r"[^a-z0-9_]", "", base.lower())
        if len(base) < 3:
            base = f"user_{self.user_id[:8].lower()}" if self.user_id else ""
        return base[:20]

    def _has_real_session(self) -> bool:
        """Return True only when both access_token and user_id are meaningful strings."""
        return _is_real_str(self.access_token) and _is_real_str(self.user_id)

    async def _finalize_login(self):
        # A valid session (access_token + user_id) is enough to enter the app.
        # Profile data only enriches the identity; it must NEVER block entry.
        profile = None
        try:
            profile = await self._load_profile()
        except Exception as e:
            logging.exception("Unexpected error")
            logging.info(
                f"Finalize login: profile load skipped (non-fatal): {e}"
            )
            profile = None

        # NOTE: Profile creation/upsert is intentionally NOT performed here.
        # Profile creation happens later through the normal onboarding flow.
        # This prevents FK/RLS errors during OAuth callback routing and keeps
        # the callback path fast and quiet.

        # Always establish safe identity defaults from session data.
        if not self.user_avatar_seed:
            self.user_avatar_seed = (
                self.user_email or self.user_phone or self.user_id
            )

        has_username = bool(profile and profile.get("username"))
        if has_username:
            self.user_username = profile.get("username") or ""
            self.user_display_name = (
                profile.get("display_name") or self.user_username
            )
            self.user_bio = profile.get("bio") or ""
            self.user_avatar_seed = (
                self.user_username or self.user_email or self.user_id
            )
            self.is_authenticated = True
            self.onboarding_step = 3
            return rx.redirect("/home")

        # No username yet: enrich from profile if we have one, prefill onboarding
        # fields, but STILL treat the session as authenticated so a valid OAuth
        # login is never bounced back to the login page.
        if profile:
            self.display_name_input = profile.get("display_name") or ""
            self.bio_input = profile.get("bio") or ""
            self.user_display_name = profile.get("display_name") or ""
            self.user_bio = profile.get("bio") or ""
        if not self.user_display_name:
            if self.user_email and "@" in self.user_email:
                self.user_display_name = self.user_email.split("@")[0]
            else:
                self.user_display_name = "New User"
        if not self.username_input:
            candidate = self._derive_username_candidate()
            if candidate:
                self.username_input = candidate

        # Valid session -> authenticated. Route OAuth users straight to /home;
        # email/password signup users still go through onboarding.
        self.is_authenticated = True
        if self.auth_method in ("google", "oauth"):
            self.onboarding_step = 3
            return rx.redirect("/home")
        self.onboarding_step = 1
        return rx.redirect("/onboarding")

    @rx.event
    async def login_email(self):
        self.error_message = ""
        self.success_message = ""
        if not self.email_input or "@" not in self.email_input:
            self.error_message = "Please enter a valid email address"
            return
        if len(self.password_input) < 6:
            self.error_message = "Password must be at least 6 characters"
            return
        self.is_loading = True
        yield
        try:
            sb = get_supabase()
            email = self.email_input
            password = self.password_input
            resp = await asyncio.to_thread(
                lambda: sb.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
            )
            self._apply_session(resp.session, resp.user)
            self.auth_method = "email"
            self.password_input = ""
            redirect = await self._finalize_login()
            self.is_loading = False
            yield redirect
        except Exception as e:
            logging.exception(f"Login error: {e}")
            self.is_loading = False
            self.error_message = _friendly_error(e)

    @rx.event
    async def register_email(self):
        self.error_message = ""
        self.success_message = ""
        if not self.email_input or "@" not in self.email_input:
            self.error_message = "Please enter a valid email address"
            return
        if len(self.password_input) < 6:
            self.error_message = "Password must be at least 6 characters"
            return
        if self.password_input != self.confirm_password_input:
            self.error_message = "Passwords do not match"
            return
        self.is_loading = True
        yield
        try:
            sb = get_supabase()
            email = self.email_input
            password = self.password_input
            resp = await asyncio.to_thread(
                lambda: sb.auth.sign_up({"email": email, "password": password})
            )
            self._apply_session(resp.session, resp.user)
            self.auth_method = "email"
            self.password_input = ""
            self.confirm_password_input = ""
            self.is_loading = False
            if resp.session is None:
                # Email confirmation required
                self.success_message = (
                    "Check your inbox to confirm your email, then sign in."
                )
                self.auth_mode = "login"
                return
            self.user_avatar_seed = self.user_email
            self.onboarding_step = 1
            yield rx.redirect("/onboarding")
        except Exception as e:
            logging.exception(f"Register error: {e}")
            self.is_loading = False
            self.error_message = _friendly_error(e)

    @rx.event
    async def send_otp(self):
        self.error_message = ""
        self.success_message = ""
        phone = self.phone_input.strip()
        if not phone or len(phone) < 7:
            self.error_message = "Please enter a valid phone number"
            return
        self.is_loading = True
        yield
        try:
            sb = get_supabase()
            await asyncio.to_thread(
                lambda: sb.auth.sign_in_with_otp({"phone": phone})
            )
            self.otp_sent = True
            self.success_message = "Verification code sent to your phone."
        except Exception as e:
            logging.exception(f"Send OTP error: {e}")
            self.error_message = _friendly_error(e)
        finally:
            self.is_loading = False

    @rx.event
    async def verify_otp(self):
        self.error_message = ""
        self.success_message = ""
        if not self.otp_input or len(self.otp_input) < 4:
            self.error_message = "Enter the verification code"
            return
        self.is_loading = True
        yield
        try:
            sb = get_supabase()
            phone = self.phone_input.strip()
            token = self.otp_input.strip()
            resp = await asyncio.to_thread(
                lambda: sb.auth.verify_otp(
                    {"phone": phone, "token": token, "type": "sms"}
                )
            )
            self._apply_session(resp.session, resp.user)
            self.auth_method = "phone"
            self.otp_input = ""
            redirect = await self._finalize_login()
            self.is_loading = False
            yield redirect
        except Exception as e:
            logging.exception(f"Verify OTP error: {e}")
            self.is_loading = False
            self.error_message = _friendly_error(e)

    # OAuth callback UI state
    oauth_callback_status: str = "processing"  # processing | success | error
    oauth_callback_error: str = ""
    oauth_redirect_target: str = ""  # Diagnostic field for OAuth URL

    def _compute_callback_url(self) -> str:
        # Always return the explicit production callback URL as requested.
        return "https://inolas-messenger-development-teal-book.reflex.run/auth/callback"

    @rx.event
    async def google_signin(self):
        self.error_message = ""
        self.is_loading = True
        yield
        try:
            sb = get_supabase()
            redirect_to = self._compute_callback_url()
            self.oauth_redirect_target = redirect_to
            payload = {
                "provider": "google",
                "options": {"redirect_to": redirect_to},
            }
            resp = await asyncio.to_thread(
                lambda: sb.auth.sign_in_with_oauth(payload)
            )
            url = getattr(resp, "url", None) or (
                resp.get("url") if isinstance(resp, dict) else None
            )
            self.is_loading = False
            if url:
                self.auth_method = "google"
                yield rx.redirect(url, is_external=True)
            else:
                self.error_message = "Unable to start Google sign-in"
        except Exception as e:
            logging.exception(f"Google sign-in error: {e}")
            self.is_loading = False
            self.error_message = _friendly_error(e)

    @rx.event
    async def handle_oauth_callback(self):
        """Handle Supabase OAuth callback: exchange code and finalize session."""
        self.oauth_callback_status = "processing"
        self.oauth_callback_error = ""
        self.session_verifying = True
        self.session_verified = False
        yield

        params: dict[str, str] = {}
        try:
            page_params = _normalize_callback_params(self.router.page.params)
            query_params = _normalize_callback_params(self.router.url.query)
            query_parameter_values = _normalize_callback_params(
                self.router.url.query_parameters
            )
            params.update(query_parameter_values)
            params.update(page_params)
            params.update(query_params)
        except Exception:
            logging.exception("Unexpected error")
            print(traceback.format_exc())
            params = {}

        err = params.get("error_description") or params.get("error") or ""
        if err:
            self.oauth_callback_status = "error"
            self.oauth_callback_error = _friendly_error(Exception(err))
            return
        code = params.get("code", "")
        if not code:
            # No code, but we may already have a valid Supabase session
            # (e.g. implicit flow, refresh, or an in-progress session).
            # Only treat this as authenticated when we have a REAL local
            # session identity — not a LocalStorage proxy or default sentinel.
            if self._has_real_session():
                if not self.auth_method:
                    self.auth_method = "oauth"
                if not self.user_avatar_seed:
                    self.user_avatar_seed = (
                        self.user_email or self.user_phone or self.user_id
                    )
                # Guarantee authenticated state and safe defaults regardless
                # of any profile-related failure inside _finalize_login.
                self.is_authenticated = True
                if not self.user_display_name:
                    if self.user_email and "@" in self.user_email:
                        self.user_display_name = self.user_email.split("@")[0]
                    else:
                        self.user_display_name = "New User"
                if self.onboarding_step < 1:
                    self.onboarding_step = 3
                redirect = None
                try:
                    redirect = await self._finalize_login()
                except Exception as e:
                    logging.exception("Unexpected error")
                    print(traceback.format_exc())
                    logging.info(
                        f"Callback finalize (no-code) skipped (non-fatal): {e}"
                    )
                    redirect = None
                # Re-assert authenticated state after finalize (in case it
                # cleared anything on error).
                self.is_authenticated = True
                self.session_verifying = False
                self.session_verified = True
                self.oauth_callback_status = "success"
                yield redirect if redirect is not None else rx.redirect("/home")
                return
            # No code and no real session — do not authenticate, do not upsert.
            self.is_authenticated = False
            self.session_verifying = False
            self.session_verified = True
            self.oauth_callback_status = "error"
            self.oauth_callback_error = (
                "Missing authorization code in callback URL."
            )
            return
        try:
            sb = get_supabase()
            session = None
            user = None
            # Try multiple call signatures for cross-version compatibility
            try:
                resp = await asyncio.to_thread(
                    lambda: sb.auth.exchange_code_for_session(
                        {"auth_code": code}
                    )
                )
                session = getattr(resp, "session", None)
                user = getattr(resp, "user", None)
            except Exception as inner:
                logging.exception(f"exchange dict form failed: {inner}")
                print(traceback.format_exc())
                try:
                    resp = await asyncio.to_thread(
                        lambda: sb.auth.exchange_code_for_session(code)
                    )
                    session = getattr(resp, "session", None)
                    user = getattr(resp, "user", None)
                except Exception as inner2:
                    logging.exception(
                        f"exchange positional form failed: {inner2}"
                    )
                    print(traceback.format_exc())
                    raise inner2
            if session is None:
                raise RuntimeError("Failed to exchange code for session")
            # Persist tokens and identity BEFORE any redirect
            self._apply_session(session, user)
            if not self.access_token:
                raise RuntimeError("Session missing access token")
            self.auth_method = "google"
            # Session fields are set; mark authenticated BEFORE finalize so
            # any profile enrichment failure cannot bounce us to login.
            self.is_authenticated = True
            if not self.user_avatar_seed:
                self.user_avatar_seed = (
                    self.user_email or self.user_phone or self.user_id
                )
            redirect = None
            try:
                redirect = await self._finalize_login()
            except Exception as e:
                logging.exception("Unexpected error")
                print(traceback.format_exc())
                logging.info(f"OAuth finalize skipped (non-fatal): {e}")
                redirect = None
            self.is_authenticated = True
            self.session_verifying = False
            self.session_verified = True
            self.oauth_callback_status = "success"
            yield redirect if redirect is not None else rx.redirect("/home")
        except Exception as e:
            logging.exception("Unexpected error")
            print(traceback.format_exc())
            logging.error(
                f"OAuth callback exception trace: {traceback.format_exc()}"
            )
            self.session_verifying = False
            self.session_verified = True
            self.oauth_callback_status = "error"
            self.oauth_callback_error = _friendly_error(e)

    @rx.event
    def retry_from_callback(self):
        self.oauth_callback_status = "processing"
        self.oauth_callback_error = ""
        return rx.redirect("/")

    @rx.event
    async def submit_username(self):
        self.error_message = ""
        if not self.username_valid_format:
            self.error_message = "Please choose a valid username"
            return
        if not self.user_id:
            self.error_message = "Your session expired. Please sign in again."
            return rx.redirect("/")
        try:
            sb = get_supabase()
            uname = self.username_input
            check = await asyncio.to_thread(
                lambda: (
                    sb.table("profiles")
                    .select("id")
                    .eq("username", uname)
                    .limit(1)
                    .execute()
                )
            )
            rows = check.data or []
            if rows and rows[0].get("id") != self.user_id:
                self.username_available = False
                self.error_message = "This username is already taken"
                return
            user_id = self.user_id
            display = self.display_name_input or uname
            payload = {
                "id": user_id,
                "username": uname,
                "display_name": display,
            }
            await asyncio.to_thread(
                lambda: sb.table("profiles").upsert(payload).execute()
            )
            self.user_username = uname
            self.onboarding_step = 2
        except Exception as e:
            logging.exception(f"Submit username error: {e}")
            self.error_message = _friendly_error(e)

    @rx.event
    async def submit_profile(self):
        self.error_message = ""
        if not self.user_id:
            self.error_message = "Your session expired. Please sign in again."
            return rx.redirect("/")
        display = self.display_name_input or self.user_username
        bio = self.bio_input
        try:
            sb = get_supabase()
            user_id = self.user_id
            payload = {
                "id": user_id,
                "display_name": display,
                "bio": bio,
            }
            if self.user_username:
                payload["username"] = self.user_username
            await asyncio.to_thread(
                lambda: sb.table("profiles").upsert(payload).execute()
            )
            self.user_display_name = display
            self.user_bio = bio
            self.user_avatar_seed = (
                self.user_username or self.user_email or self.user_id
            )
            self.onboarding_step = 3
            self.is_authenticated = True
            return rx.redirect("/home")
        except Exception as e:
            logging.exception(f"Submit profile error: {e}")
            self.error_message = _friendly_error(e)

    @rx.event
    async def skip_profile(self):
        self.error_message = ""
        if not self.user_id:
            return rx.redirect("/")
        display = self.user_username
        try:
            sb = get_supabase()
            user_id = self.user_id
            payload = {
                "id": user_id,
                "display_name": display,
            }
            if self.user_username:
                payload["username"] = self.user_username
            await asyncio.to_thread(
                lambda: sb.table("profiles").upsert(payload).execute()
            )
            self.user_display_name = display
            self.user_avatar_seed = (
                self.user_username or self.user_email or self.user_id
            )
            self.onboarding_step = 3
            self.is_authenticated = True
            self.onboarding_step = 3
            return rx.redirect("/home")
        except Exception as e:
            logging.exception(f"Skip profile error: {e}")
            self.error_message = _friendly_error(e)

    @rx.event
    async def restore_session(self):
        """Restore Supabase session from stored refresh token, then route accordingly."""
        # Mark verification in progress so protected routes wait instead of
        # bouncing to /login while we validate.
        self.session_verifying = True
        self.session_verified = False
        yield

        try:
            current_path = self.router.page.path or "/"
        except Exception:
            logging.exception("Router path unavailable")
            current_path = "/"

        # Already fully authenticated with profile AND a real session identity -
        # redirect from login pages. Guard prevents LocalStorage proxy/default
        # values from tricking the router into /home on a fresh visit.
        if (
            self.is_authenticated
            and _is_real_str(self.user_username)
            and self._has_real_session()
        ):
            self.session_verifying = False
            self.session_verified = True
            if current_path in ("/", "/onboarding"):
                yield rx.redirect("/home")
            return

        if not _is_real_str(self.refresh_token):
            # Fallback: if we still have a real access_token + user_id, treat
            # as authenticated (OAuth session already established).
            if self._has_real_session():
                self.is_authenticated = True
                if not self.user_avatar_seed:
                    self.user_avatar_seed = (
                        self.user_email or self.user_phone or self.user_id
                    )
                if not self.user_display_name:
                    if self.user_email and "@" in self.user_email:
                        self.user_display_name = self.user_email.split("@")[0]
                    else:
                        self.user_display_name = "New User"
                self.session_verifying = False
                self.session_verified = True
                if current_path in ("/", "/onboarding"):
                    yield rx.redirect("/home")
                return
            self.session_verifying = False
            self.session_verified = True
            return

        try:
            sb = get_supabase()
            token = self.refresh_token
            resp = await asyncio.to_thread(
                lambda: sb.auth.refresh_session(token)
            )
            if not (
                resp
                and getattr(resp, "session", None)
                and getattr(resp, "user", None)
            ):
                self.session_verifying = False
                self.session_verified = True
                return
            self._apply_session(resp.session, resp.user)
            profile = None
            try:
                profile = await self._load_profile()
            except Exception as e:
                logging.exception("Unexpected error")
                logging.info(
                    f"Restore session profile load skipped (non-fatal): {e}"
                )
                profile = None
            if profile and profile.get("username"):
                self.user_username = profile.get("username") or ""
                self.user_display_name = (
                    profile.get("display_name") or self.user_username
                )
                self.user_bio = profile.get("bio") or ""
                self.user_avatar_seed = (
                    self.user_username or self.user_email or self.user_id
                )
                self.is_authenticated = True
                self.onboarding_step = 3
                self.session_verifying = False
                self.session_verified = True
                if current_path in ("/", "/onboarding"):
                    yield rx.redirect("/home")
                return
            # Valid session but incomplete profile
            if profile:
                self.display_name_input = profile.get("display_name") or ""
                self.bio_input = profile.get("bio") or ""
                self.user_display_name = profile.get("display_name") or ""
            if not self.user_display_name:
                if self.user_email and "@" in self.user_email:
                    self.user_display_name = self.user_email.split("@")[0]
                else:
                    self.user_display_name = "New User"
            self.user_avatar_seed = self.user_email or self.user_id
            if not self.username_input:
                candidate = self._derive_username_candidate()
                if candidate:
                    self.username_input = candidate
            # Keep valid session authenticated even if profile incomplete
            self.is_authenticated = True
            self.session_verifying = False
            self.session_verified = True
            # For OAuth-like flows, don't force onboarding on every restore
            if self.auth_method in ("google", "oauth"):
                self.onboarding_step = 3
                if current_path in ("/", "/onboarding"):
                    yield rx.redirect("/home")
                return
            self.onboarding_step = 1
            if current_path != "/onboarding":
                yield rx.redirect("/onboarding")
        except Exception as e:
            logging.exception(f"Restore session error: {e}")
            self.access_token = ""
            self.refresh_token = ""
            self.user_id = ""
            self.session_verifying = False
            self.session_verified = True

    @rx.event
    async def logout(self):
        try:
            sb = get_supabase()
            await asyncio.to_thread(lambda: sb.auth.sign_out())
        except Exception as e:
            logging.exception(f"Logout error: {e}")
        self.is_authenticated = False
        self.user_id = ""
        self.access_token = ""
        self.refresh_token = ""
        self.user_email = ""
        self.user_phone = ""
        self.user_username = ""
        self.user_display_name = ""
        self.user_bio = ""
        self.user_avatar_seed = ""
        self.auth_method = ""
        self.onboarding_step = 0
        self.email_input = ""
        self.password_input = ""
        self.confirm_password_input = ""
        self.phone_input = ""
        self.otp_input = ""
        self.otp_sent = False
        self.auth_mode = "login"
        self.session_verifying = False
        self.session_verified = True
        return rx.redirect("/")
