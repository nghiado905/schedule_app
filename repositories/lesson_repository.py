import sqlite3
from datetime import date, datetime, time
from pathlib import Path

from models.lesson import Lesson


class LessonRepository:
    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    start_at TEXT NOT NULL,
                    end_at TEXT NOT NULL,
                    room TEXT NOT NULL DEFAULT '',
                    address TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    color TEXT NOT NULL DEFAULT '#20A4E8',
                    priority TEXT NOT NULL DEFAULT 'normal'
                )
                """
            )
            self._ensure_columns(db)

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _ensure_columns(db: sqlite3.Connection):
        existing_columns = {
            row["name"] for row in db.execute("PRAGMA table_info(lessons)").fetchall()
        }
        migrations = {
            "address": "ALTER TABLE lessons ADD COLUMN address TEXT NOT NULL DEFAULT ''",
            "room": "ALTER TABLE lessons ADD COLUMN room TEXT NOT NULL DEFAULT ''",
            "note": "ALTER TABLE lessons ADD COLUMN note TEXT NOT NULL DEFAULT ''",
            "color": "ALTER TABLE lessons ADD COLUMN color TEXT NOT NULL DEFAULT '#20A4E8'",
            "priority": "ALTER TABLE lessons ADD COLUMN priority TEXT NOT NULL DEFAULT 'normal'",
        }
        for column_name, statement in migrations.items():
            if column_name not in existing_columns:
                db.execute(statement)

    def list_for_day(self, selected_date: date) -> list[Lesson]:
        start = datetime.combine(selected_date, time.min).isoformat()
        end = datetime.combine(selected_date, time.max).isoformat()
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM lessons WHERE start_at BETWEEN ? AND ? ORDER BY start_at",
                (start, end),
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def list_between(self, start_date: date, end_date: date) -> list[Lesson]:
        start = datetime.combine(start_date, time.min).isoformat()
        end = datetime.combine(end_date, time.max).isoformat()
        with self._connect() as db:
            rows = db.execute(
                "SELECT * FROM lessons WHERE start_at BETWEEN ? AND ? ORDER BY start_at",
                (start, end),
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def save(self, lesson: Lesson) -> Lesson:
        values = (
            lesson.title, lesson.start_at.isoformat(), lesson.end_at.isoformat(), lesson.address,
            lesson.room, lesson.note, lesson.color, lesson.priority,
        )
        with self._connect() as db:
            if lesson.id is None:
                cursor = db.execute(
                    """INSERT INTO lessons
                    (title, start_at, end_at, address, room, note, color, priority)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    values,
                )
                lesson.id = int(cursor.lastrowid)
            else:
                db.execute(
                    """UPDATE lessons SET title=?, start_at=?, end_at=?, address=?, room=?,
                    note=?, color=?, priority=? WHERE id=?""",
                    (*values, lesson.id),
                )
        return lesson

    def delete(self, lesson_id: int):
        with self._connect() as db:
            db.execute("DELETE FROM lessons WHERE id=?", (lesson_id,))

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Lesson:
        return Lesson(
            id=row["id"], title=row["title"],
            start_at=datetime.fromisoformat(row["start_at"]),
            end_at=datetime.fromisoformat(row["end_at"]),
            address=row["address"],
            room=row["room"], note=row["note"], color=row["color"],
            priority=row["priority"],
        )
