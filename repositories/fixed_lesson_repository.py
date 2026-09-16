import sqlite3
from datetime import date, datetime, time
from pathlib import Path

from models.fixed_lesson import FixedLesson


class FixedLessonRepository:
    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        with sqlite3.connect(self.database_path) as db:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS fixed_lessons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    weekday INTEGER NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    title TEXT NOT NULL,
                    address TEXT NOT NULL DEFAULT '',
                    room TEXT NOT NULL DEFAULT '',
                    note TEXT NOT NULL DEFAULT '',
                    color TEXT NOT NULL DEFAULT '#20A4E8',
                    effective_from TEXT NOT NULL DEFAULT ''
                )
                """
            )
            columns = [row[1] for row in db.execute("PRAGMA table_info(fixed_lessons)").fetchall()]
            if "effective_from" not in columns:
                first_day = date.today().replace(day=1).isoformat()
                db.execute("ALTER TABLE fixed_lessons ADD COLUMN effective_from TEXT NOT NULL DEFAULT ''")
                db.execute(
                    "UPDATE fixed_lessons SET effective_from=? WHERE effective_from=''",
                    (first_day,),
                )

    def list_all(self) -> list[FixedLesson]:
        with sqlite3.connect(self.database_path) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute("SELECT * FROM fixed_lessons ORDER BY weekday, start_time").fetchall()
        return [self._from_row(row) for row in rows]

    def save(self, lesson: FixedLesson) -> FixedLesson:
        values = (
            lesson.weekday,
            lesson.start_time.strftime("%H:%M"),
            lesson.end_time.strftime("%H:%M"),
            lesson.title,
            lesson.address,
            lesson.room,
            lesson.note,
            lesson.color,
            (lesson.effective_from or date.today().replace(day=1)).isoformat(),
        )
        with sqlite3.connect(self.database_path) as db:
            if lesson.id is None:
                lesson.id = int(db.execute(
                    """INSERT INTO fixed_lessons
                    (weekday, start_time, end_time, title, address, room, note, color, effective_from)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    values,
                ).lastrowid)
            else:
                db.execute(
                    """UPDATE fixed_lessons SET weekday=?, start_time=?, end_time=?, title=?,
                    address=?, room=?, note=?, color=?, effective_from=? WHERE id=?""",
                    (*values, lesson.id),
                )
        return lesson

    def delete(self, lesson_id: int):
        with sqlite3.connect(self.database_path) as db:
            db.execute("DELETE FROM fixed_lessons WHERE id=?", (lesson_id,))

    @staticmethod
    def _from_row(row: sqlite3.Row) -> FixedLesson:
        return FixedLesson(
            id=row["id"], weekday=row["weekday"],
            start_time=datetime.strptime(row["start_time"], "%H:%M").time(),
            end_time=datetime.strptime(row["end_time"], "%H:%M").time(),
            title=row["title"], address=row["address"], room=row["room"],
            note=row["note"], color=row["color"],
            effective_from=(
                datetime.strptime(row["effective_from"], "%Y-%m-%d").date()
                if row["effective_from"]
                else date.today().replace(day=1)
            ),
        )
