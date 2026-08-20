import reflex as rx
from typing import TypedDict
import random


class UserData(TypedDict):
    username: str
    display_name: str
    bio: str
    avatar_seed: str
    online: bool
    last_seen: str


class Reaction(TypedDict):
    emoji: str
    users: list[str]


class Message(TypedDict):
    id: str
    chat_id: str
    sender: str
    text: str
    type: str
    media_url: str
    file_name: str
    file_size: str
    timestamp: str
    reply_to: str
    reply_preview: str
    reply_sender: str
    edited: bool
    deleted_for_everyone: bool
    deleted_for_me: bool
    reactions: list[Reaction]
    read_by: list[str]
    forwarded: bool
    pinned: bool


class Chat(TypedDict):
    id: str
    type: str
    name: str
    username: str
    avatar_seed: str
    participants: list[str]
    unread: int
    last_message: str
    last_time: str
    pinned: bool
    muted: bool
    typing: bool
    online: bool
    last_seen: str


SEED_USERS: dict[str, UserData] = {
    "emma": {
        "username": "emma",
        "display_name": "Emma Chen",
        "bio": "Product designer • Coffee enthusiast ☕",
        "avatar_seed": "emma",
        "online": True,
        "last_seen": "online",
    },
    "marcus": {
        "username": "marcus",
        "display_name": "Marcus Reed",
        "bio": "Engineering @ Inolas. Building tools people love.",
        "avatar_seed": "marcus",
        "online": True,
        "last_seen": "online",
    },
    "sofia": {
        "username": "sofia",
        "display_name": "Sofia Alvarez",
        "bio": "Photographer 📷 Travel · Nature",
        "avatar_seed": "sofia",
        "online": False,
        "last_seen": "last seen 12 min ago",
    },
    "david": {
        "username": "david",
        "display_name": "David Kim",
        "bio": "Startup founder. Runner. Dad.",
        "avatar_seed": "david",
        "online": False,
        "last_seen": "last seen 2 hours ago",
    },
    "priya": {
        "username": "priya",
        "display_name": "Priya Shah",
        "bio": "Design systems ✨",
        "avatar_seed": "priya",
        "online": True,
        "last_seen": "online",
    },
    "alex": {
        "username": "alex",
        "display_name": "Alex Novak",
        "bio": "Backend eng • Rust · Go",
        "avatar_seed": "alex",
        "online": False,
        "last_seen": "last seen yesterday",
    },
    "lily": {
        "username": "lily",
        "display_name": "Lily Park",
        "bio": "UX writer with a soft spot for puns.",
        "avatar_seed": "lily",
        "online": True,
        "last_seen": "online",
    },
    "noah": {
        "username": "noah",
        "display_name": "Noah Bennett",
        "bio": "Fitness coach 💪",
        "avatar_seed": "noah",
        "online": False,
        "last_seen": "last seen 3 days ago",
    },
    "zara": {
        "username": "zara",
        "display_name": "Zara Ahmed",
        "bio": "Illustrator & maker",
        "avatar_seed": "zara",
        "online": True,
        "last_seen": "online",
    },
    "leo": {
        "username": "leo",
        "display_name": "Leo Martins",
        "bio": "Music producer 🎧",
        "avatar_seed": "leo",
        "online": False,
        "last_seen": "last seen 5 min ago",
    },
}


def _mk_msg(
    mid: str,
    chat_id: str,
    sender: str,
    text: str,
    timestamp: str,
    mtype: str = "text",
    media_url: str = "",
    file_name: str = "",
    file_size: str = "",
    reply_to: str = "",
    reply_preview: str = "",
    reply_sender: str = "",
    edited: bool = False,
    reactions: list[Reaction] | None = None,
    read_by: list[str] | None = None,
    forwarded: bool = False,
    pinned: bool = False,
) -> Message:
    return Message(
        id=mid,
        chat_id=chat_id,
        sender=sender,
        text=text,
        type=mtype,
        media_url=media_url,
        file_name=file_name,
        file_size=file_size,
        timestamp=timestamp,
        reply_to=reply_to,
        reply_preview=reply_preview,
        reply_sender=reply_sender,
        edited=edited,
        deleted_for_everyone=False,
        deleted_for_me=False,
        reactions=reactions or [],
        read_by=read_by or [],
        forwarded=forwarded,
        pinned=pinned,
    )


def _seed_chats() -> list[Chat]:
    return [
        Chat(
            id="c_emma",
            type="dm",
            name="Emma Chen",
            username="emma",
            avatar_seed="emma",
            participants=["me", "emma"],
            unread=3,
            last_message="See you tomorrow! 👋",
            last_time="2m",
            pinned=True,
            muted=False,
            typing=True,
            online=True,
            last_seen="online",
        ),
        Chat(
            id="c_design",
            type="group",
            name="Design Team",
            username="",
            avatar_seed="team-design",
            participants=["me", "priya", "lily", "emma"],
            unread=1,
            last_message="Priya: Updated the mockups 🎨",
            last_time="12m",
            pinned=True,
            muted=False,
            typing=False,
            online=True,
            last_seen="4 members",
        ),
        Chat(
            id="c_marcus",
            type="dm",
            name="Marcus Reed",
            username="marcus",
            avatar_seed="marcus",
            participants=["me", "marcus"],
            unread=0,
            last_message="Sounds good to me",
            last_time="1h",
            pinned=False,
            muted=False,
            typing=False,
            online=True,
            last_seen="online",
        ),
        Chat(
            id="c_sofia",
            type="dm",
            name="Sofia Alvarez",
            username="sofia",
            avatar_seed="sofia",
            participants=["me", "sofia"],
            unread=0,
            last_message="Thanks so much!",
            last_time="3h",
            pinned=False,
            muted=True,
            typing=False,
            online=False,
            last_seen="last seen 12 min ago",
        ),
        Chat(
            id="c_trip",
            type="group",
            name="Weekend Trip",
            username="",
            avatar_seed="team-trip",
            participants=["me", "alex", "noah", "zara", "leo"],
            unread=0,
            last_message="Alex: Booked the hotel 🏨",
            last_time="Yesterday",
            pinned=False,
            muted=False,
            typing=False,
            online=False,
            last_seen="5 members",
        ),
        Chat(
            id="c_david",
            type="dm",
            name="David Kim",
            username="david",
            avatar_seed="david",
            participants=["me", "david"],
            unread=0,
            last_message="Let's catch up soon",
            last_time="Mon",
            pinned=False,
            muted=False,
            typing=False,
            online=False,
            last_seen="last seen 2 hours ago",
        ),
        Chat(
            id="c_lily",
            type="dm",
            name="Lily Park",
            username="lily",
            avatar_seed="lily",
            participants=["me", "lily"],
            unread=0,
            last_message="Voice message",
            last_time="Sun",
            pinned=False,
            muted=False,
            typing=False,
            online=True,
            last_seen="online",
        ),
    ]


def _seed_messages() -> dict[str, list[Message]]:
    return {
        "c_emma": [
            _mk_msg(
                "m1",
                "c_emma",
                "emma",
                "Hey! Are we still on for coffee tomorrow?",
                "10:12 AM",
                read_by=["me"],
            ),
            _mk_msg(
                "m2",
                "c_emma",
                "me",
                "Absolutely! 10am at Blue Bottle?",
                "10:14 AM",
                read_by=["emma"],
            ),
            _mk_msg(
                "m3",
                "c_emma",
                "emma",
                "Perfect. I'll bring the sketches we talked about.",
                "10:15 AM",
                reactions=[Reaction(emoji="❤️", users=["me"])],
                read_by=["me"],
            ),
            _mk_msg(
                "m4",
                "c_emma",
                "me",
                "Amazing. Can't wait to see them!",
                "10:16 AM",
                read_by=["emma"],
                reply_to="m3",
                reply_sender="Emma Chen",
                reply_preview="Perfect. I'll bring the sketches we talked about.",
            ),
            _mk_msg(
                "m5",
                "c_emma",
                "emma",
                "Shared the inspiration board 🎨",
                "10:22 AM",
                read_by=["me"],
            ),
            _mk_msg(
                "m6",
                "c_emma",
                "emma",
                "Here's the inspiration board 🎨",
                "10:23 AM",
                read_by=["me"],
            ),
            _mk_msg(
                "m7",
                "c_emma",
                "me",
                "This is stunning 🔥",
                "10:25 AM",
                read_by=["emma"],
                reactions=[Reaction(emoji="🔥", users=["emma"])],
            ),
            _mk_msg(
                "m8",
                "c_emma",
                "emma",
                "See you tomorrow! 👋",
                "10:30 AM",
                read_by=[],
            ),
        ],
        "c_design": [
            _mk_msg(
                "m1",
                "c_design",
                "priya",
                "Morning team! Just pushed the v2 mockups.",
                "9:02 AM",
                pinned=True,
                read_by=["me", "emma", "lily"],
            ),
            _mk_msg(
                "m2",
                "c_design",
                "lily",
                "Love the new empty states 👏",
                "9:05 AM",
                read_by=["me", "priya"],
            ),
            _mk_msg(
                "m3",
                "c_design",
                "emma",
                "The typography feels so much tighter now.",
                "9:08 AM",
                read_by=["me", "priya", "lily"],
            ),
            _mk_msg(
                "m4",
                "c_design",
                "priya",
                "",
                "9:15 AM",
                mtype="document",
                file_name="Inolas-Design-System-v2.pdf",
                file_size="4.2 MB",
                read_by=["me"],
            ),
            _mk_msg(
                "m5",
                "c_design",
                "me",
                "Reviewing now — will drop comments by EOD.",
                "9:20 AM",
                read_by=["priya", "emma"],
            ),
            _mk_msg(
                "m6",
                "c_design",
                "priya",
                "Updated the mockups 🎨",
                "12:30 PM",
                read_by=[],
            ),
        ],
        "c_marcus": [
            _mk_msg(
                "m1",
                "c_marcus",
                "marcus",
                "Yo can you review my PR?",
                "8:30 AM",
                read_by=["me"],
            ),
            _mk_msg(
                "m2",
                "c_marcus",
                "me",
                "On it in 5",
                "8:32 AM",
                read_by=["marcus"],
            ),
            _mk_msg(
                "m3",
                "c_marcus",
                "marcus",
                "Sounds good to me",
                "9:00 AM",
                read_by=["me"],
            ),
        ],
        "c_sofia": [
            _mk_msg(
                "m1",
                "c_sofia",
                "sofia",
                "The prints arrived! They look incredible.",
                "Yesterday",
                read_by=["me"],
            ),
            _mk_msg(
                "m2",
                "c_sofia",
                "me",
                "So glad! You crushed it.",
                "Yesterday",
                read_by=["sofia"],
            ),
            _mk_msg(
                "m3",
                "c_sofia",
                "sofia",
                "Thanks so much!",
                "3h",
                read_by=["me"],
            ),
        ],
        "c_trip": [
            _mk_msg(
                "m1",
                "c_trip",
                "zara",
                "Who's driving on Saturday?",
                "Sun",
                read_by=["me"],
            ),
            _mk_msg(
                "m2",
                "c_trip",
                "noah",
                "I can! Room for 3 more.",
                "Sun",
                read_by=["me", "zara"],
            ),
            _mk_msg(
                "m3",
                "c_trip",
                "leo",
                "Bringing the playlist 🎶",
                "Sun",
                read_by=["me"],
            ),
            _mk_msg(
                "m4",
                "c_trip",
                "alex",
                "Booked the hotel 🏨",
                "Yesterday",
                read_by=["me"],
                pinned=True,
            ),
        ],
        "c_david": [
            _mk_msg(
                "m1",
                "c_david",
                "david",
                "Let's catch up soon",
                "Mon",
                read_by=["me"],
            ),
        ],
        "c_lily": [
            _mk_msg(
                "m1",
                "c_lily",
                "lily",
                "",
                "Sun",
                mtype="voice",
                file_size="0:42",
                read_by=["me"],
            ),
        ],
    }


class MessengerState(rx.State):
    # Layout / navigation
    active_view: str = "chats"  # chats | search | settings | profile
    active_chat_id: str = ""
    show_profile_panel: bool = False
    profile_username: str = ""
    mobile_show_chat: bool = False

    # Data
    users: dict[str, UserData] = SEED_USERS
    chats: list[Chat] = _seed_chats()
    messages_by_chat: dict[str, list[Message]] = _seed_messages()

    # Search
    search_query: str = ""
    chat_search_query: str = ""
    message_search_query: str = ""
    show_message_search: bool = False

    # Composer
    composer_text: str = ""
    reply_to_id: str = ""
    reply_to_preview: str = ""
    reply_to_sender: str = ""
    edit_message_id: str = ""
    show_attach_menu: bool = False
    show_emoji_panel: bool = False
    show_sticker_panel: bool = False

    # Message actions
    active_message_menu: str = ""

    # Forward
    show_forward_modal: bool = False
    forward_message_id: str = ""
    forward_targets: list[str] = []

    # Delete confirm
    show_delete_modal: bool = False
    delete_message_id: str = ""

    # Privacy
    privacy_username_visible: bool = True
    privacy_last_seen: str = "everyone"  # everyone | contacts | nobody
    privacy_online_status: bool = True
    privacy_profile_photo: str = "everyone"
    privacy_read_receipts: bool = True
    blocked_users: list[str] = []
    reported_users: list[str] = []

    # Toasts
    toast_message: str = ""

    # Pagination / lazy loading
    page_size: int = 30
    visible_count: int = 30

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
        if self.active_chat_id != chat_id:
            self.active_chat_id = chat_id
            self.visible_count = self.page_size
        self.mobile_show_chat = True
        if self.show_profile_panel:
            self.show_profile_panel = False
        if self.show_message_search:
            self.show_message_search = False
            self.message_search_query = ""
        if self.reply_to_id:
            self.reply_to_id = ""
            self.reply_to_preview = ""
            self.reply_to_sender = ""
        if self.edit_message_id:
            self.edit_message_id = ""
        # Mark as read only if needed (avoid touching list when already 0)
        idx = self._find_chat_index(chat_id)
        if idx >= 0 and self.chats[idx]["unread"] > 0:
            self.chats[idx]["unread"] = 0

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
    def toggle_attach_menu(self):
        self.show_attach_menu = not self.show_attach_menu
        self.show_emoji_panel = False
        self.show_sticker_panel = False

    @rx.event
    def toggle_emoji_panel(self):
        self.show_emoji_panel = not self.show_emoji_panel
        self.show_attach_menu = False
        self.show_sticker_panel = False

    @rx.event
    def toggle_sticker_panel(self):
        self.show_sticker_panel = not self.show_sticker_panel
        self.show_attach_menu = False
        self.show_emoji_panel = False

    @rx.event
    def insert_emoji(self, emoji: str):
        self.composer_text = f"{self.composer_text}{emoji}"

    @rx.event
    def send_sticker(self, sticker: str):
        if not self.active_chat_id:
            return
        self._append_message(
            _mk_msg(
                mid=f"m{random.randint(10000, 99999)}",
                chat_id=self.active_chat_id,
                sender="me",
                text=sticker,
                timestamp="now",
                mtype="sticker",
                read_by=[],
            )
        )
        self.show_sticker_panel = False

    @rx.event
    def send_gif(self, url: str):
        if not self.active_chat_id:
            return
        self._append_message(
            _mk_msg(
                mid=f"m{random.randint(10000, 99999)}",
                chat_id=self.active_chat_id,
                sender="me",
                text="",
                timestamp="now",
                mtype="gif",
                media_url=url,
                read_by=[],
            )
        )
        self.show_attach_menu = False

    @rx.event
    def attach_type(self, kind: str):
        if not self.active_chat_id:
            return
        samples = {
            "image": ("Shared a photo 📷", "text", "", "", ""),
            "video": ("Shared a video 🎬", "text", "", "", ""),
            "document": ("", "document", "", "Project-Brief.pdf", "2.1 MB"),
            "voice": ("", "voice", "", "", "0:17"),
        }
        text, mtype, media_url, file_name, file_size = samples.get(
            kind, ("", "text", "", "", "")
        )
        self._append_message(
            _mk_msg(
                mid=f"m{random.randint(10000, 99999)}",
                chat_id=self.active_chat_id,
                sender="me",
                text=text,
                timestamp="now",
                mtype=mtype,
                media_url=media_url,
                file_name=file_name,
                file_size=file_size,
                read_by=[],
            )
        )
        self.show_attach_menu = False

    def _append_message(self, msg: Message):
        chat_id = msg["chat_id"]
        if chat_id not in self.messages_by_chat:
            self.messages_by_chat[chat_id] = []
        self.messages_by_chat[chat_id].append(msg)
        preview = msg["text"] if msg["text"] else f"[{msg['type']}]"
        idx = self._find_chat_index(chat_id)
        if idx >= 0:
            self.chats[idx]["last_message"] = f"You: {preview}"
            self.chats[idx]["last_time"] = "now"
        # Keep newly appended message visible without recomputing window
        if chat_id == self.active_chat_id:
            self.visible_count = max(self.visible_count + 1, self.page_size)

    @rx.event
    def send_message(self):
        if not self.active_chat_id:
            return
        text = self.composer_text.strip()
        if not text:
            return
        if self.edit_message_id:
            msgs = self.messages_by_chat.get(self.active_chat_id, [])
            for i, m in enumerate(msgs):
                if m["id"] == self.edit_message_id:
                    msgs[i]["text"] = text
                    msgs[i]["edited"] = True
                    break
            self.messages_by_chat[self.active_chat_id] = msgs
            self.edit_message_id = ""
        else:
            msg = _mk_msg(
                mid=f"m{random.randint(10000, 99999)}",
                chat_id=self.active_chat_id,
                sender="me",
                text=text,
                timestamp="now",
                reply_to=self.reply_to_id,
                reply_preview=self.reply_to_preview,
                reply_sender=self.reply_to_sender,
                read_by=[],
            )
            self._append_message(msg)
        self.composer_text = ""
        self.reply_to_id = ""
        self.reply_to_preview = ""
        self.reply_to_sender = ""

    @rx.event
    def start_reply(self, message_id: str):
        msgs = self.messages_by_chat.get(self.active_chat_id, [])
        for m in msgs:
            if m["id"] == message_id:
                self.reply_to_id = message_id
                self.reply_to_preview = (
                    m["text"] if m["text"] else f"[{m['type']}]"
                )
                sender = m["sender"]
                if sender == "me":
                    self.reply_to_sender = "You"
                else:
                    user = self.users.get(sender, {})
                    self.reply_to_sender = (
                        user.get("display_name", sender) if user else sender
                    )
                break
        self.active_message_menu = ""

    @rx.event
    def cancel_reply(self):
        self.reply_to_id = ""
        self.reply_to_preview = ""
        self.reply_to_sender = ""

    @rx.event
    def start_edit(self, message_id: str):
        msgs = self.messages_by_chat.get(self.active_chat_id, [])
        for m in msgs:
            if m["id"] == message_id and m["sender"] == "me":
                self.edit_message_id = message_id
                self.composer_text = m["text"]
                break
        self.active_message_menu = ""

    @rx.event
    def cancel_edit(self):
        self.edit_message_id = ""
        self.composer_text = ""

    @rx.event
    def toggle_message_menu(self, message_id: str):
        self.active_message_menu = (
            "" if self.active_message_menu == message_id else message_id
        )

    @rx.event
    def close_message_menu(self):
        self.active_message_menu = ""

    @rx.event
    def react_to_message(self, message_id: str, emoji: str):
        msgs = self.messages_by_chat.get(self.active_chat_id, [])
        for i, m in enumerate(msgs):
            if m["id"] == message_id:
                reactions = list(m["reactions"])
                found = False
                for j, r in enumerate(reactions):
                    if r["emoji"] == emoji:
                        found = True
                        users = list(r["users"])
                        if "me" in users:
                            users.remove("me")
                        else:
                            users.append("me")
                        if users:
                            reactions[j] = Reaction(emoji=emoji, users=users)
                        else:
                            reactions.pop(j)
                        break
                if not found:
                    reactions.append(Reaction(emoji=emoji, users=["me"]))
                msgs[i]["reactions"] = reactions
                break
        self.messages_by_chat[self.active_chat_id] = msgs
        self.active_message_menu = ""

    @rx.event
    def toggle_pin_message(self, message_id: str):
        msgs = self.messages_by_chat.get(self.active_chat_id, [])
        for i, m in enumerate(msgs):
            if m["id"] == message_id:
                msgs[i]["pinned"] = not m["pinned"]
                break
        self.messages_by_chat[self.active_chat_id] = msgs
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
        self.close_delete_modal()

    @rx.event
    def delete_for_everyone(self):
        msgs = self.messages_by_chat.get(self.active_chat_id, [])
        for i, m in enumerate(msgs):
            if m["id"] == self.delete_message_id:
                msgs[i]["deleted_for_everyone"] = True
                msgs[i]["text"] = ""
                break
        self.messages_by_chat[self.active_chat_id] = msgs
        self.close_delete_modal()

    @rx.event
    def open_forward_modal(self, message_id: str):
        self.forward_message_id = message_id
        self.forward_targets = []
        self.show_forward_modal = True
        self.active_message_menu = ""

    @rx.event
    def close_forward_modal(self):
        self.show_forward_modal = False
        self.forward_message_id = ""
        self.forward_targets = []

    @rx.event
    def toggle_forward_target(self, chat_id: str):
        if chat_id in self.forward_targets:
            self.forward_targets.remove(chat_id)
        else:
            self.forward_targets.append(chat_id)

    @rx.event
    def submit_forward(self):
        if not self.forward_message_id or not self.forward_targets:
            self.close_forward_modal()
            return
        source_msg = None
        for msgs in self.messages_by_chat.values():
            for m in msgs:
                if m["id"] == self.forward_message_id:
                    source_msg = m
                    break
            if source_msg:
                break
        if not source_msg:
            self.close_forward_modal()
            return
        for target in self.forward_targets:
            new_msg = _mk_msg(
                mid=f"m{random.randint(10000, 99999)}",
                chat_id=target,
                sender="me",
                text=source_msg["text"],
                timestamp="now",
                mtype=source_msg["type"],
                media_url=source_msg["media_url"],
                file_name=source_msg["file_name"],
                file_size=source_msg["file_size"],
                forwarded=True,
                read_by=[],
            )
            if target not in self.messages_by_chat:
                self.messages_by_chat[target] = []
            self.messages_by_chat[target].append(new_msg)
            for i, c in enumerate(self.chats):
                if c["id"] == target:
                    preview = (
                        source_msg["text"]
                        if source_msg["text"]
                        else f"[{source_msg['type']}]"
                    )
                    self.chats[i]["last_message"] = f"You: {preview}"
                    self.chats[i]["last_time"] = "now"
        self.toast_message = f"Forwarded to {len(self.forward_targets)} chat(s)"
        self.close_forward_modal()

    @rx.event
    def open_profile(self, username: str):
        self.profile_username = username
        self.show_profile_panel = True

    @rx.event
    def close_profile(self):
        self.show_profile_panel = False

    @rx.event
    def message_user(self, username: str):
        # find or create dm
        chat_id = f"c_{username}"
        exists = any(c["id"] == chat_id for c in self.chats)
        if not exists:
            user = self.users.get(username)
            if user:
                self.chats.insert(
                    0,
                    Chat(
                        id=chat_id,
                        type="dm",
                        name=user["display_name"],
                        username=user["username"],
                        avatar_seed=user["avatar_seed"],
                        participants=["me", username],
                        unread=0,
                        last_message="",
                        last_time="now",
                        pinned=False,
                        muted=False,
                        typing=False,
                        online=user["online"],
                        last_seen=user["last_seen"],
                    ),
                )
                self.messages_by_chat[chat_id] = []
        self.active_chat_id = chat_id
        self.active_view = "chats"
        self.show_profile_panel = False
        self.mobile_show_chat = True
        self.search_query = ""

    @rx.event
    def block_user(self, username: str):
        if username not in self.blocked_users:
            self.blocked_users.append(username)
        self.toast_message = f"Blocked @{username}"
        self.show_profile_panel = False

    @rx.event
    def unblock_user(self, username: str):
        if username in self.blocked_users:
            self.blocked_users.remove(username)
        self.toast_message = f"Unblocked @{username}"

    @rx.event
    def report_user(self, username: str):
        if username not in self.reported_users:
            self.reported_users.append(username)
        self.toast_message = f"Reported @{username}"

    @rx.event
    def toggle_pin_chat(self, chat_id: str):
        for i, c in enumerate(self.chats):
            if c["id"] == chat_id:
                self.chats[i]["pinned"] = not c["pinned"]
                break

    @rx.event
    def toggle_mute_chat(self, chat_id: str):
        for i, c in enumerate(self.chats):
            if c["id"] == chat_id:
                self.chats[i]["muted"] = not c["muted"]
                break

    @rx.event
    def set_privacy(self, key: str, value: str):
        if key == "username_visible":
            self.privacy_username_visible = value == "true"
        elif key == "last_seen":
            self.privacy_last_seen = value
        elif key == "online_status":
            self.privacy_online_status = value == "true"
        elif key == "profile_photo":
            self.privacy_profile_photo = value
        elif key == "read_receipts":
            self.privacy_read_receipts = value == "true"

    @rx.event
    def toggle_privacy_bool(self, key: str):
        if key == "username_visible":
            self.privacy_username_visible = not self.privacy_username_visible
        elif key == "online_status":
            self.privacy_online_status = not self.privacy_online_status
        elif key == "read_receipts":
            self.privacy_read_receipts = not self.privacy_read_receipts

    @rx.event
    def dismiss_toast(self):
        self.toast_message = ""

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
    def search_results(self) -> list[UserData]:
        q = self.search_query.lower().strip().lstrip("@")
        if not q:
            return []
        results: list[UserData] = []
        for u in self.users.values():
            if q in u["username"].lower() or q in u["display_name"].lower():
                results.append(u)
                if len(results) >= 20:
                    break
        return results

    @rx.var
    def active_chat(self) -> Chat:
        cid = self.active_chat_id
        if not cid:
            return Chat(
                id="",
                type="dm",
                name="",
                username="",
                avatar_seed="",
                participants=[],
                unread=0,
                last_message="",
                last_time="",
                pinned=False,
                muted=False,
                typing=False,
                online=False,
                last_seen="",
            )
        for c in self.chats:
            if c["id"] == cid:
                return c
        return Chat(
            id="",
            type="dm",
            name="",
            username="",
            avatar_seed="",
            participants=[],
            unread=0,
            last_message="",
            last_time="",
            pinned=False,
            muted=False,
            typing=False,
            online=False,
            last_seen="",
        )

    @rx.var
    def active_messages(self) -> list[Message]:
        msgs = self.messages_by_chat.get(self.active_chat_id, [])
        if not msgs:
            return []
        q = self.message_search_query.lower().strip()
        if q:
            # Search scans the full history, but only when user is actively searching
            out: list[Message] = []
            for m in msgs:
                if m["deleted_for_me"]:
                    continue
                if q in m["text"].lower():
                    out.append(m)
            return out
        # Fast path: slice the tail window without touching the full list
        total = len(msgs)
        start = max(0, total - self.visible_count)
        window = msgs[start:]
        # Filter deleted_for_me only within the small window
        has_deleted = False
        for m in window:
            if m["deleted_for_me"]:
                has_deleted = True
                break
        if not has_deleted:
            return window
        return [m for m in window if not m["deleted_for_me"]]

    @rx.var
    def has_older_messages(self) -> bool:
        if self.message_search_query.strip():
            return False
        total = len(self.messages_by_chat.get(self.active_chat_id, []))
        return total > self.visible_count

    @rx.var
    def pinned_messages(self) -> list[Message]:
        msgs = self.messages_by_chat.get(self.active_chat_id, [])
        if not msgs:
            return []
        out: list[Message] = []
        for m in msgs:
            if (
                m["pinned"]
                and not m["deleted_for_me"]
                and not m["deleted_for_everyone"]
            ):
                out.append(m)
        return out

    @rx.var
    def active_profile(self) -> UserData:
        u = self.users.get(self.profile_username)
        if u:
            return u
        return UserData(
            username="",
            display_name="",
            bio="",
            avatar_seed="",
            online=False,
            last_seen="",
        )

    @rx.var
    def is_active_user_blocked(self) -> bool:
        return self.profile_username in self.blocked_users

    @rx.var
    def total_unread(self) -> int:
        return sum(c["unread"] for c in self.chats)

    @rx.var
    def blocked_users_data(self) -> list[UserData]:
        return [self.users[u] for u in self.blocked_users if u in self.users]
