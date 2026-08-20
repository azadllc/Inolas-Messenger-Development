import asyncio
import logging
import os
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator, TypedDict

import psycopg
import reflex as rx
from psycopg.rows import dict_row

from app.states.auth_state import _is_real_str


class UserData(TypedDict):
    id: str
    username: str
    display_name: str
    bio: str
    avatar_seed: str


class Message(TypedDict):
    id: str
    chat_id: str
    sender: str
    text: str
    timestamp: str
    edited: bool
    deleted_for_everyone: bool
    deleted_for_me: bool


class Chat(TypedDict):
    id: str
    name: str
    username: str
    avatar_seed: str
    participants: list[str]
    unread: int
    last_message: str
    last_time: str


EMPTY_CHAT: Chat = Chat(
    id="",
    name="",
    username="",
    avatar_seed="",
    participants=[],
    unread=0,
    last_message="",
    last_time="",
)

EMPTY_USER: UserData = UserData(
    id="",
    username="",
    display_name="",
    bio="",
    avatar_seed="",
)

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)
_MESSAGE_PAGE_LIMIT = 200
_CHAT_LIST_LIMIT = 200
_SEARCH_LIMIT = 20


def _parse_ts(value: object) -> datetime | None:
    """Parse a Postgres/Supabase timestamptz string into an aware datetime."""
    if not value:
        return None
    raw = str(value).strip()
    if raw.endswith("Z"):
        raw = f"{raw[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _relative_time(moment: datetime | None) -> str:
    if moment is None:
        return ""
    seconds = (datetime.now(timezone.utc) - moment).total_seconds()
    if seconds < 60:
        return "now"
    if seconds < 3600:
        return f"{int(seconds // 60)}m"
    if seconds < 86400:
        return f"{int(seconds // 3600)}h"
    if seconds < 172800:
        return "Yesterday"
    if seconds < 604800:
        return moment.strftime("%a")
    return moment.strftime("%b %d")


def _clock_time(moment: datetime | None) -> str:
    if moment is None:
        return ""
    return moment.strftime("%I:%M %p").lstrip("0")


def _profile_to_user(row: dict) -> UserData:
    username = str(row.get("username") or "").strip()
    display_name = str(row.get("display_name") or "").strip() or (
        username or "Inolas user"
    )
    return UserData(
        id=str(row.get("id") or ""),
        username=username,
        display_name=display_name,
        bio=str(row.get("bio") or ""),
        avatar_seed=username or display_name,
    )


def _sanitize_search_term(query: str) -> str:
    cleaned = query.strip().lstrip("@")
    for bad in (",", "(", ")", "%", "*", '"', "'", "\\"):
        cleaned = cleaned.replace(bad, " ")
    return " ".join(cleaned.split())


_DB_URL_ENV_VARS = (
    "REFLEX_DB_URL",
    "DB_URL",
    "DATABASE_URL",
    "POSTGRES_URL",
)


def _normalize_dsn(raw: str) -> str:
    """Turn a SQLAlchemy-style URL into a libpq DSN psycopg accepts."""
    dsn = raw.strip()
    for prefix, replacement in (
        ("postgresql+psycopg://", "postgresql://"),
        ("postgresql+psycopg2://", "postgresql://"),
        ("postgresql+asyncpg://", "postgresql://"),
        ("postgres+psycopg://", "postgresql://"),
        ("postgres://", "postgresql://"),
    ):
        if dsn.startswith(prefix):
            dsn = f"{replacement}{dsn[len(prefix) :]}"
            break
    return dsn


def _database_dsn() -> str:
    """Resolve the connected Postgres URL used for all real chat queries."""
    for name in _DB_URL_ENV_VARS:
        raw = os.getenv(name)
        if raw and raw.strip():
            return _normalize_dsn(raw)
    raise RuntimeError("No Postgres database URL is configured")


@contextmanager
def _db() -> Iterator[psycopg.Cursor]:
    """Open a short-lived transaction against the connected Postgres db."""
    with psycopg.connect(_database_dsn(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            yield cur


def _is_uuid(value: object) -> bool:
    """Only real uuid strings may be used as chat/profile identifiers."""
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        uuid.UUID(value.strip())
    except ValueError:
        return False
    return True


def _fetch_chats_sync(
    user_id: str,
) -> tuple[list[Chat], dict[str, UserData]]:
    """Load the current profile's real DM chats from Postgres."""
    if not _is_uuid(user_id):
        return [], {}
    sql = """
        with my_chats as (
            select cm.chat_id, cm.last_read_at
            from public.chat_members cm
            where cm.user_id = %(uid)s
        ),
        partner as (
            select distinct on (cm.chat_id) cm.chat_id, cm.user_id as partner_id
            from public.chat_members cm
            join my_chats mc on mc.chat_id = cm.chat_id
            where cm.user_id <> %(uid)s
            order by cm.chat_id, cm.joined_at asc
        ),
        last_msg as (
            select distinct on (m.chat_id)
                m.chat_id, m.sender_id, m.body, m.created_at
            from public.messages m
            join my_chats mc on mc.chat_id = m.chat_id
            where m.deleted_at is null
            order by m.chat_id, m.created_at desc
        ),
        unread as (
            select m.chat_id, count(*) as unread_count
            from public.messages m
            join my_chats mc on mc.chat_id = m.chat_id
            where m.sender_id <> %(uid)s
              and m.deleted_at is null
              and (mc.last_read_at is null or m.created_at > mc.last_read_at)
            group by m.chat_id
        )
        select
            c.id::text as chat_id,
            c.updated_at,
            c.created_at,
            p.partner_id::text as partner_id,
            pr.username,
            pr.display_name,
            pr.bio,
            lm.sender_id::text as last_sender_id,
            lm.body as last_body,
            lm.created_at as last_created_at,
            coalesce(u.unread_count, 0) as unread_count
        from public.chats c
        join my_chats mc on mc.chat_id = c.id
        join partner p on p.chat_id = c.id
        join public.profiles pr on pr.id = p.partner_id
        left join last_msg lm on lm.chat_id = c.id
        left join unread u on u.chat_id = c.id
        order by coalesce(lm.created_at, c.updated_at, c.created_at) desc
        limit %(limit)s
    """
    with _db() as cur:
        cur.execute(sql, {"uid": user_id, "limit": _CHAT_LIST_LIMIT})
        rows = cur.fetchall()

    chats: list[Chat] = []
    users: dict[str, UserData] = {}
    for row in rows:
        partner = _profile_to_user(
            {
                "id": row["partner_id"],
                "username": row["username"],
                "display_name": row["display_name"],
                "bio": row["bio"],
            }
        )
        if partner["username"]:
            users[partner["username"]] = partner
        preview = ""
        body = str(row.get("last_body") or "").strip()
        if body:
            preview = (
                f"You: {body}"
                if str(row.get("last_sender_id") or "") == user_id
                else body
            )
        activity = (
            _parse_ts(row.get("last_created_at"))
            or _parse_ts(row.get("updated_at"))
            or _parse_ts(row.get("created_at"))
        )
        chats.append(
            Chat(
                id=str(row["chat_id"]),
                name=partner["display_name"],
                username=partner["username"],
                avatar_seed=partner["avatar_seed"],
                participants=[user_id, partner["id"]],
                unread=int(row.get("unread_count") or 0),
                last_message=preview,
                last_time=_relative_time(activity),
            )
        )
    return chats, users


def _fetch_messages_sync(
    chat_id: str, user_id: str
) -> tuple[list[Message], dict[str, UserData]]:
    """Load the most recent real messages for a chat the user belongs to."""
    if not _is_uuid(chat_id) or not _is_uuid(user_id):
        return [], {}
    sql = """
        select
            m.id::text as id,
            m.sender_id::text as sender_id,
            m.body,
            m.created_at,
            m.edited_at,
            m.deleted_at,
            pr.username,
            pr.display_name,
            pr.bio
        from public.messages m
        left join public.profiles pr on pr.id = m.sender_id
        where m.chat_id = %(chat)s
          and exists (
              select 1 from public.chat_members cm
              where cm.chat_id = %(chat)s and cm.user_id = %(uid)s
          )
        order by m.created_at desc
        limit %(limit)s
    """
    with _db() as cur:
        cur.execute(
            sql,
            {"chat": chat_id, "uid": user_id, "limit": _MESSAGE_PAGE_LIMIT},
        )
        rows = list(reversed(cur.fetchall()))
    if not rows:
        return [], {}

    users: dict[str, UserData] = {}
    messages: list[Message] = []
    for row in rows:
        sender_id = str(row.get("sender_id") or "")
        if sender_id == user_id:
            sender_label = "me"
        else:
            profile = _profile_to_user(
                {
                    "id": sender_id,
                    "username": row.get("username"),
                    "display_name": row.get("display_name"),
                    "bio": row.get("bio"),
                }
            )
            if profile["username"]:
                users[profile["username"]] = profile
                sender_label = profile["username"]
            else:
                sender_label = profile["display_name"] or sender_id[:8]
        deleted = row.get("deleted_at") is not None
        created = _parse_ts(row.get("created_at"))
        messages.append(
            Message(
                id=str(row.get("id")),
                chat_id=chat_id,
                sender=sender_label,
                text="" if deleted else str(row.get("body") or ""),
                timestamp=_clock_time(created) or _relative_time(created),
                edited=row.get("edited_at") is not None,
                deleted_for_everyone=deleted,
                deleted_for_me=False,
            )
        )
    return messages, users


def _search_profiles_sync(term: str, exclude_id: str) -> list[UserData]:
    """Search real profiles by username or display name."""
    cleaned = term.strip()
    if not cleaned:
        return []
    sql = """
        select id::text as id, username, display_name, bio
        from public.profiles
        where (username ilike %(pattern)s or display_name ilike %(pattern)s)
          and (%(exclude)s::uuid is null or id <> %(exclude)s::uuid)
        order by
            case when lower(username) = lower(%(term)s) then 0 else 1 end,
            username asc
        limit %(limit)s
    """
    with _db() as cur:
        cur.execute(
            sql,
            {
                "pattern": f"%{cleaned}%",
                "term": cleaned,
                "exclude": exclude_id if _is_uuid(exclude_id) else None,
                "limit": _SEARCH_LIMIT,
            },
        )
        rows = cur.fetchall()

    results: list[UserData] = []
    for row in rows:
        user = _profile_to_user(row)
        if not user["username"] or user["id"] == exclude_id:
            continue
        results.append(user)
    return results


def _fetch_profile_by_username_sync(username: str) -> UserData | None:
    """Resolve a real profile row from an exact @username."""
    handle = username.strip().lstrip("@")
    if not handle:
        return None
    with _db() as cur:
        cur.execute(
            """
            select id::text as id, username, display_name, bio
            from public.profiles
            where lower(username) = lower(%(username)s)
            limit 1
            """,
            {"username": handle},
        )
        row = cur.fetchone()
    if row is None:
        return None
    user = _profile_to_user(row)
    return user if user["id"] else None


def _find_dm_chat_sync(user_id: str, other_id: str) -> str:
    """Return the id of an existing DM chat shared by both profiles."""
    if not _is_uuid(user_id) or not _is_uuid(other_id) or user_id == other_id:
        return ""
    with _db() as cur:
        cur.execute(
            """
            select c.id::text as chat_id
            from public.chats c
            join public.chat_members mine
                on mine.chat_id = c.id and mine.user_id = %(uid)s
            join public.chat_members theirs
                on theirs.chat_id = c.id and theirs.user_id = %(other)s
            where c.chat_type = 'dm'
            order by c.created_at asc
            limit 1
            """,
            {"uid": user_id, "other": other_id},
        )
        row = cur.fetchone()
    return str(row["chat_id"]) if row else ""


def _ensure_dm_chat_sync(user_id: str, other_id: str) -> tuple[str, bool]:
    """Reuse or create the DM chat between two real profiles.

    Returns (chat_id, created). The lookup, chat insert and both membership
    inserts run inside ONE transaction, so a chat can never be committed
    with a single member and concurrent attempts cannot leak partial rows.
    """
    if not _is_uuid(user_id) or not _is_uuid(other_id):
        raise ValueError("Both profile ids must be real uuids")
    if user_id == other_id:
        raise ValueError("A profile cannot open a DM with itself")

    with _db() as cur:
        cur.execute(
            """
            select c.id::text as chat_id
            from public.chats c
            join public.chat_members mine
                on mine.chat_id = c.id and mine.user_id = %(uid)s
            join public.chat_members theirs
                on theirs.chat_id = c.id and theirs.user_id = %(other)s
            where c.chat_type = 'dm'
            order by c.created_at asc
            limit 1
            """,
            {"uid": user_id, "other": other_id},
        )
        existing = cur.fetchone()
        if existing:
            return str(existing["chat_id"]), False

        cur.execute(
            """
            insert into public.chats (chat_type, created_by)
            values ('dm', %(uid)s)
            returning id::text as chat_id
            """,
            {"uid": user_id},
        )
        created = cur.fetchone()
        if created is None or not created.get("chat_id"):
            raise RuntimeError("Chat row was not created")
        chat_id = str(created["chat_id"])
        cur.execute(
            """
            insert into public.chat_members (chat_id, user_id)
            values (%(chat)s, %(uid)s), (%(chat)s, %(other)s)
            on conflict (chat_id, user_id) do nothing
            """,
            {"chat": chat_id, "uid": user_id, "other": other_id},
        )
    return chat_id, True


def _send_text_message_sync(chat_id: str, sender_id: str, body: str) -> None:
    """Persist one real text message, scoped to a verified membership."""
    text = body.strip()
    if not _is_uuid(chat_id) or not _is_uuid(sender_id):
        raise PermissionError("Sender is not a member of this conversation")
    if not text:
        raise ValueError("Message body cannot be empty")

    with _db() as cur:
        cur.execute(
            """
            insert into public.messages (chat_id, sender_id, body)
            select %(chat)s, %(uid)s, %(body)s
            where exists (
                select 1 from public.chat_members cm
                where cm.chat_id = %(chat)s and cm.user_id = %(uid)s
            )
            returning id::text as id
            """,
            {"chat": chat_id, "uid": sender_id, "body": text},
        )
        inserted = cur.fetchone()
        if inserted is None:
            raise PermissionError("Sender is not a member of this conversation")
        cur.execute(
            """
            update public.chat_members
            set last_read_at = timezone('utc'::text, now())
            where chat_id = %(chat)s and user_id = %(uid)s
            """,
            {"chat": chat_id, "uid": sender_id},
        )


class MessengerState(rx.State):
    # Layout / navigation
    active_view: str = "chats"  # chats | search | settings | profile
    active_chat_id: str = ""
    show_profile_panel: bool = False
    profile_username: str = ""
    mobile_show_chat: bool = False

    # Identity (mirrored from AuthState on load)
    current_user_id: str = ""
    current_username: str = ""

    # Real data loaded from the database
    users: dict[str, UserData] = {}
    chats: list[Chat] = []
    messages_by_chat: dict[str, list[Message]] = {}

    # Loading / error state
    chats_loading: bool = False
    messages_loading: bool = False
    search_loading: bool = False
    starting_chat: bool = False
    sending_message: bool = False
    data_initialized: bool = False
    load_error: str = ""
    message_load_error: str = ""
    search_error: str = ""

    # Search
    search_query: str = ""
    search_results: list[UserData] = []
    chat_search_query: str = ""
    message_search_query: str = ""
    show_message_search: bool = False

    # Composer
    composer_text: str = ""
    composer_key: int = 0
    show_emoji_panel: bool = False

    # Message actions (local, display-only)
    active_message_menu: str = ""
    show_delete_modal: bool = False
    delete_message_id: str = ""

    # Toasts
    toast_message: str = ""

    # Pagination / lazy loading
    page_size: int = 30
    visible_count: int = 30

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------
    @rx.event(background=True)
    async def load_messenger_data(self):
        """Load the signed-in profile's real chats when entering /home."""
        from app.states.auth_state import AuthState

        user_id = ""
        for attempt in range(4):
            async with self:
                auth = await self.get_state(AuthState)
                user_id = auth.user_id if _is_real_str(auth.user_id) else ""
                self.current_user_id = user_id
                self.current_username = (
                    auth.user_username
                    if _is_real_str(auth.user_username)
                    else ""
                )
                if user_id:
                    self.chats_loading = True
                    self.load_error = ""
            if user_id:
                break
            if attempt < 3:
                await asyncio.sleep(0.6)

        if not user_id:
            async with self:
                self.chats = []
                self.messages_by_chat = {}
                self.active_chat_id = ""
                self.chats_loading = False
                self.data_initialized = True
            return

        try:
            chats, users = await asyncio.to_thread(_fetch_chats_sync, user_id)
        except Exception as e:
            logging.exception(f"Chat list load error: {e}")
            async with self:
                self.chats_loading = False
                self.data_initialized = True
                self.load_error = (
                    "We couldn't load your conversations right now."
                )
            return

        has_active = False
        async with self:
            self.chats = chats
            merged = dict(self.users)
            merged.update(users)
            self.users = merged
            self.chats_loading = False
            self.data_initialized = True
            self.load_error = ""
            has_active = any(c["id"] == self.active_chat_id for c in chats)
            if not has_active:
                self.active_chat_id = ""
                self.mobile_show_chat = False
                self.messages_by_chat = {}
        if has_active:
            yield MessengerState.load_chat_messages

    @rx.event(background=True)
    async def load_chat_messages(self):
        """Load real messages for the active chat."""
        async with self:
            chat_id = self.active_chat_id
            user_id = self.current_user_id
            if not chat_id or not user_id:
                self.messages_loading = False
                return
            self.messages_loading = True
            self.message_load_error = ""

        try:
            messages, users = await asyncio.to_thread(
                _fetch_messages_sync, chat_id, user_id
            )
        except Exception as e:
            logging.exception(f"Message load error: {e}")
            async with self:
                self.messages_loading = False
                self.message_load_error = (
                    "We couldn't load this conversation right now."
                )
                self.toast_message = "Couldn't load messages. Please retry."
            return

        async with self:
            history = dict(self.messages_by_chat)
            history[chat_id] = messages
            self.messages_by_chat = history
            merged = dict(self.users)
            merged.update(users)
            self.users = merged
            self.visible_count = self.page_size
            self.messages_loading = False

    @rx.event(background=True)
    async def refresh_chats(self):
        """Reload the chat list previews/order without dropping the open chat."""
        async with self:
            user_id = self.current_user_id
            if not user_id:
                return

        try:
            chats, users = await asyncio.to_thread(_fetch_chats_sync, user_id)
        except Exception as e:
            logging.exception(f"Chat list refresh error: {e}")
            return

        async with self:
            self.chats = chats
            merged = dict(self.users)
            merged.update(users)
            self.users = merged
            self.load_error = ""
            self.data_initialized = True

    @rx.event(background=True)
    async def search_profiles(self):
        """Search real profiles, always excluding the current user."""
        async with self:
            term = _sanitize_search_term(self.search_query)
            exclude_id = self.current_user_id
            if not term:
                self.search_results = []
                self.search_loading = False
                self.search_error = ""
                return
            self.search_loading = True
            self.search_error = ""

        try:
            results = await asyncio.to_thread(
                _search_profiles_sync, term, exclude_id
            )
        except Exception as e:
            logging.exception(f"Profile search error: {e}")
            async with self:
                self.search_results = []
                self.search_loading = False
                self.search_error = "Search failed. Please try again."
            return

        async with self:
            if _sanitize_search_term(self.search_query) != term:
                return
            self.search_results = results
            merged = dict(self.users)
            for user in results:
                merged[user["username"]] = user
            self.users = merged
            self.search_loading = False

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------
    @rx.event
    def set_active_view(self, view: str):
        if self.active_view != view:
            self.active_view = view
        if self.show_profile_panel:
            self.show_profile_panel = False

    def _find_chat_index(self, chat_id: str) -> int:
        for i, c in enumerate(self.chats):
            if c["id"] == chat_id:
                return i
        return -1

    @rx.event
    def open_chat(self, chat_id: str):
        idx = self._find_chat_index(chat_id)
        if idx < 0:
            self.toast_message = "This conversation is no longer available"
            return MessengerState.load_messenger_data
        changed = self.active_chat_id != chat_id
        if changed:
            self.active_chat_id = chat_id
            self.visible_count = self.page_size
        self.mobile_show_chat = True
        if self.show_profile_panel:
            self.show_profile_panel = False
        if self.show_message_search:
            self.show_message_search = False
            self.message_search_query = ""
        if self.chats[idx]["unread"] > 0:
            self.chats[idx]["unread"] = 0
        return MessengerState.load_chat_messages

    @rx.event
    def load_older_messages(self):
        total = len(self.messages_by_chat.get(self.active_chat_id, []))
        if self.visible_count < total:
            self.visible_count = min(self.visible_count + self.page_size, total)

    @rx.event
    def close_chat_mobile(self):
        self.mobile_show_chat = False

    @rx.event
    def set_search_query(self, v: str):
        self.search_query = v
        return MessengerState.search_profiles

    @rx.event
    def set_chat_search_query(self, v: str):
        self.chat_search_query = v

    @rx.event
    def set_message_search_query(self, v: str):
        self.message_search_query = v

    @rx.event
    def toggle_message_search(self):
        self.show_message_search = not self.show_message_search
        self.message_search_query = ""

    @rx.event
    def set_composer(self, v: str):
        self.composer_text = v

    @rx.event
    def toggle_emoji_panel(self):
        self.show_emoji_panel = not self.show_emoji_panel

    @rx.event
    def insert_emoji(self, emoji: str):
        self.composer_text = f"{self.composer_text}{emoji}"

    # ------------------------------------------------------------------
    # Sending real text messages
    # ------------------------------------------------------------------
    @rx.event(background=True)
    async def send_message(self):
        """Persist the composer text as a real message in the active chat."""
        async with self:
            chat_id = self.active_chat_id
            user_id = self.current_user_id
            body = self.composer_text.strip()
            if not chat_id:
                self.toast_message = "Open a conversation first"
                return
            if not user_id:
                self.toast_message = "Please sign in again to send messages"
                return
            if not body:
                return
            if len(body) > 4000:
                self.toast_message = "Message is too long (4000 characters max)"
                return
            if self.sending_message:
                return
            self.sending_message = True
            self.composer_text = ""
            self.composer_key += 1
            self.show_emoji_panel = False

        try:
            await asyncio.to_thread(
                _send_text_message_sync, chat_id, user_id, body
            )
        except PermissionError as e:
            logging.exception(f"Message send permission error: {e}")
            async with self:
                self.sending_message = False
                self.composer_text = body
                self.composer_key += 1
                self.toast_message = "You're no longer part of this chat"
            return
        except Exception as e:
            logging.exception(f"Message send error: {e}")
            async with self:
                self.sending_message = False
                self.composer_text = body
                self.composer_key += 1
                self.toast_message = "Message not sent. Please try again."
            return

        async with self:
            self.sending_message = False
            self.message_load_error = ""
        yield MessengerState.load_chat_messages
        yield MessengerState.refresh_chats

    # ------------------------------------------------------------------
    # Message interactions (local view state)
    # ------------------------------------------------------------------
    @rx.event
    def toggle_message_menu(self, message_id: str):
        self.active_message_menu = (
            "" if self.active_message_menu == message_id else message_id
        )

    @rx.event
    def close_message_menu(self):
        self.active_message_menu = ""

    @rx.event
    def open_delete_modal(self, message_id: str):
        self.delete_message_id = message_id
        self.show_delete_modal = True
        self.active_message_menu = ""

    @rx.event
    def close_delete_modal(self):
        self.show_delete_modal = False
        self.delete_message_id = ""

    @rx.event
    def delete_for_me(self):
        msgs = self.messages_by_chat.get(self.active_chat_id, [])
        for i, m in enumerate(msgs):
            if m["id"] == self.delete_message_id:
                msgs[i]["deleted_for_me"] = True
                break
        self.messages_by_chat[self.active_chat_id] = msgs
        self.show_delete_modal = False
        self.delete_message_id = ""

    # ------------------------------------------------------------------
    # People
    # ------------------------------------------------------------------
    @rx.event
    def open_profile(self, username: str):
        if not username:
            return
        self.profile_username = username
        self.show_profile_panel = True

    @rx.event
    def close_profile(self):
        self.show_profile_panel = False

    @rx.event(background=True)
    async def message_user(self, username: str):
        """Create or reuse a real DM chat with this profile, then open it."""
        async with self:
            target = str(username or "").strip().lstrip("@")
            if not target:
                return
            user_id = self.current_user_id
            if not user_id:
                self.toast_message = "Please sign in again to start a chat"
                return
            if self.starting_chat:
                return
            if target == self.current_username:
                self.toast_message = "You can't message yourself"
                return
            known = self.users.get(target)
            target_id = known["id"] if known else ""
            existing_chat_id = ""
            for chat in self.chats:
                if chat["username"] == target:
                    existing_chat_id = chat["id"]
                    break
            self.active_view = "chats"
            self.show_profile_panel = False
            self.search_query = ""
            self.search_results = []

        if existing_chat_id:
            async with self:
                self.active_chat_id = existing_chat_id
                self.visible_count = self.page_size
                self.mobile_show_chat = True
                self.show_message_search = False
                self.message_search_query = ""
                for i, chat in enumerate(self.chats):
                    if chat["id"] == existing_chat_id and chat["unread"] > 0:
                        self.chats[i]["unread"] = 0
                        break
            yield MessengerState.load_chat_messages
            return

        async with self:
            self.starting_chat = True
            self.toast_message = f"Starting a chat with @{target}..."

        try:
            if not target_id:
                profile = await asyncio.to_thread(
                    _fetch_profile_by_username_sync, target
                )
                if profile is None:
                    async with self:
                        self.starting_chat = False
                        self.toast_message = f"@{target} could not be found"
                    return
                target_id = profile["id"]
                async with self:
                    merged = dict(self.users)
                    merged[profile["username"]] = profile
                    self.users = merged
            if target_id == user_id:
                async with self:
                    self.starting_chat = False
                    self.toast_message = "You can't message yourself"
                return
            chat_id, _created = await asyncio.to_thread(
                _ensure_dm_chat_sync, user_id, target_id
            )
        except Exception as e:
            logging.exception(f"DM creation error: {e}")
            async with self:
                self.starting_chat = False
                self.toast_message = (
                    "We couldn't start that conversation. Please try again."
                )
            return

        try:
            chats, users = await asyncio.to_thread(_fetch_chats_sync, user_id)
        except Exception as e:
            logging.exception(f"Chat list load error after DM create: {e}")
            chats, users = [], {}

        async with self:
            if chats:
                self.chats = chats
                merged = dict(self.users)
                merged.update(users)
                self.users = merged
                self.load_error = ""
                self.data_initialized = True
            self.active_chat_id = chat_id
            self.visible_count = self.page_size
            self.mobile_show_chat = True
            self.show_message_search = False
            self.message_search_query = ""
            self.starting_chat = False
            self.toast_message = f"Chat with @{target} is ready"
        yield MessengerState.load_chat_messages

    @rx.event
    def dismiss_toast(self):
        self.toast_message = ""

    # ------------------------------------------------------------------
    # Derived data
    # ------------------------------------------------------------------
    @rx.var
    def filtered_chats(self) -> list[Chat]:
        q = self.chat_search_query.lower().strip()
        if not q:
            return self.chats
        results: list[Chat] = []
        for c in self.chats:
            if q in c["name"].lower() or q in c["username"].lower():
                results.append(c)
        return results

    @rx.var
    def active_chat(self) -> Chat:
        cid = self.active_chat_id
        if not cid:
            return EMPTY_CHAT
        for c in self.chats:
            if c["id"] == cid:
                return c
        return EMPTY_CHAT

    @rx.var
    def active_messages(self) -> list[Message]:
        msgs = self.messages_by_chat.get(self.active_chat_id, [])
        if not msgs:
            return []
        q = self.message_search_query.lower().strip()
        if q:
            out: list[Message] = []
            for m in msgs:
                if m["deleted_for_me"]:
                    continue
                if q in m["text"].lower():
                    out.append(m)
            return out
        total = len(msgs)
        start = max(0, total - self.visible_count)
        window = msgs[start:]
        return [m for m in window if not m["deleted_for_me"]]

    @rx.var
    def has_older_messages(self) -> bool:
        if self.message_search_query.strip():
            return False
        total = len(self.messages_by_chat.get(self.active_chat_id, []))
        return total > self.visible_count

    @rx.var
    def active_profile(self) -> UserData:
        user = self.users.get(self.profile_username)
        return user if user else EMPTY_USER

    @rx.var
    def total_unread(self) -> int:
        return sum(c["unread"] for c in self.chats)

    @rx.var
    def has_chats(self) -> bool:
        return len(self.chats) > 0
