"""
История помидоров: сохранение, статистика за день/неделю/месяц, экспорт CSV/JSON.
"""

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


@dataclass
class PomodoroRecord:
    """Одна запись: один завершённый интервал (работа или перерыв)."""

    started_at: str
    finished_at: str
    duration_seconds: int
    mode: str  # "work" | "short_break" | "long_break"
    task_name: str = ""


def _data_path() -> Path:
    from PySide6.QtCore import QStandardPaths
    loc = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
    folder = Path(loc) / "Personal_Dashboard" / "Pomodoro"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "history.json"


def _load_history() -> list[dict]:
    p = _data_path()
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_history(records: list[dict]) -> None:
    p = _data_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


def add_record(record: PomodoroRecord) -> None:
    records = _load_history()
    records.append(asdict(record))
    _save_history(records)


def get_records_from(dt: datetime) -> list[PomodoroRecord]:
    cutoff = dt.isoformat()
    records = _load_history()
    out = []
    for r in records:
        if r.get("started_at", "") >= cutoff:
            out.append(PomodoroRecord(
                started_at=r["started_at"],
                finished_at=r["finished_at"],
                duration_seconds=r["duration_seconds"],
                mode=r.get("mode", "work"),
                task_name=r.get("task_name", ""),
            ))
    return out


def get_today_count() -> int:
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    records = get_records_from(today)
    return sum(1 for r in records if r.mode == "work")


def get_week_count() -> int:
    week_ago = datetime.now() - timedelta(days=7)
    records = get_records_from(week_ago)
    return sum(1 for r in records if r.mode == "work")


def get_month_count() -> int:
    month_ago = datetime.now() - timedelta(days=30)
    records = get_records_from(month_ago)
    return sum(1 for r in records if r.mode == "work")


def get_all_records() -> list[PomodoroRecord]:
    records = _load_history()
    return [
        PomodoroRecord(
            started_at=r["started_at"],
            finished_at=r["finished_at"],
            duration_seconds=r["duration_seconds"],
            mode=r.get("mode", "work"),
            task_name=r.get("task_name", ""),
        )
        for r in records
    ]


def export_csv(file_path: Path) -> bool:
    try:
        records = _load_history()
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["started_at", "finished_at", "duration_seconds", "mode", "task_name"])
            w.writeheader()
            w.writerows(records)
        return True
    except Exception:
        return False


def export_json(file_path: Path) -> bool:
    try:
        records = _load_history()
        file_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False
