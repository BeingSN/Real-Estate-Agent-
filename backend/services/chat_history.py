import json
from datetime import datetime, timezone
from pathlib import Path

HISTORY_FILE = Path(__file__).parent.parent / "data" / "chat_history.json"
DEFAULT_SESSION_ID = "default"


def _load() -> dict:
    if not HISTORY_FILE.exists():
        return {"sessions": []}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"sessions": []}


def _save(data: dict):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_turn(turn_data: dict):
    data = _load()
    session = next(
        (s for s in data["sessions"] if s["session_id"] == DEFAULT_SESSION_ID),
        None,
    )
    if session is None:
        session = {
            "session_id": DEFAULT_SESSION_ID,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "turns": [],
        }
        data["sessions"].append(session)

    turn_data["turn_number"] = len(session["turns"]) + 1
    turn_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    session["turns"].append(turn_data)
    _save(data)


def get_all_history() -> dict:
    return _load()
