import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from threading import RLock


class JSONStore:
    """Simple threadsafe JSON file store for app state."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self._lock = RLock()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({
                "projects": {},
                "active_project": None,
                "tone_of_voice": "",
            })

    def _read(self) -> Dict[str, Any]:
        with self._lock:
            if not self.path.exists():
                return {}
            try:
                return json.loads(self.path.read_text("utf-8"))
            except json.JSONDecodeError:
                return {}

    def _write(self, data: Dict[str, Any]) -> None:
        with self._lock:
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2))
            tmp.replace(self.path)

    # High-level helpers
    def get_state(self) -> Dict[str, Any]:
        return self._read()

    def set_state(self, state: Dict[str, Any]) -> None:
        self._write(state)

    # Project CRUD
    def list_projects(self) -> List[str]:
        state = self._read()
        return sorted(list(state.get("projects", {}).keys()))

    def get_active_project(self) -> Optional[str]:
        return self._read().get("active_project")

    def set_active_project(self, name: Optional[str]) -> None:
        state = self._read()
        state["active_project"] = name
        self._write(state)

    def create_project(self, name: str) -> None:
        state = self._read()
        projects = state.setdefault("projects", {})
        if name not in projects:
            projects[name] = {
                "sessions": [],  # each session: {id, items: [{input, instructions, output, liked, meta}]}
                "likes": [],
            }
        state["active_project"] = name
        self._write(state)

    def delete_project(self, name: str) -> None:
        state = self._read()
        projects = state.get("projects", {})
        if name in projects:
            del projects[name]
            if state.get("active_project") == name:
                state["active_project"] = next(iter(projects.keys()), None)
            self._write(state)

    # Sessions and history
    def append_history_item(self, project: str, session_id: str, item: Dict[str, Any]) -> None:
        state = self._read()
        proj = state.setdefault("projects", {}).setdefault(project, {"sessions": [], "likes": []})
        # find or create session
        for session in proj["sessions"]:
            if session["id"] == session_id:
                session["items"].append(item)
                break
        else:
            proj["sessions"].append({"id": session_id, "items": [item]})
        self._write(state)

    def list_sessions(self, project: str) -> List[Dict[str, Any]]:
        state = self._read()
        proj = state.get("projects", {}).get(project, {"sessions": []})
        return proj.get("sessions", [])

    def like_item(self, project: str, item: Dict[str, Any]) -> None:
        state = self._read()
        proj = state.setdefault("projects", {}).setdefault(project, {"sessions": [], "likes": []})
        proj["likes"].append(item)
        self._write(state)

    def list_likes(self, project: str) -> List[Dict[str, Any]]:
        state = self._read()
        proj = state.get("projects", {}).get(project, {"likes": []})
        return proj.get("likes", [])

    # Tone of voice
    def get_tone_of_voice(self) -> str:
        return self._read().get("tone_of_voice", "")

    def set_tone_of_voice(self, text: str) -> None:
        state = self._read()
        state["tone_of_voice"] = text
        self._write(state)
