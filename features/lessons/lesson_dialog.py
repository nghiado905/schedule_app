from datetime import date, datetime, timedelta
from typing import Callable

import flet as ft

from constants import COLORS, THEME
from models.lesson import Lesson
from repositories.lesson_repository import LessonRepository


class LessonDialogFeature:
    def __init__(
        self,
        page: ft.Page,
        repository: LessonRepository,
        on_saved: Callable[[date], None],
    ):
        self.page = page
        self.repository = repository
        self.on_saved = on_saved

    def open(
        self,
        lesson: Lesson | None = None,
        initial: datetime | None = None,
        initial_end: datetime | None = None,
    ):
        source = lesson.start_at if lesson else initial
        if source is None:
            source = datetime.combine(date.today(), datetime.now().time()).replace(second=0, microsecond=0)
        end = lesson.end_at if lesson else initial_end or source + timedelta(hours=1)
        chosen = [lesson.color if lesson else COLORS[0]]

        title = ft.TextField(label="Ten mon hoc / cong viec", value=lesson.title if lesson else "", autofocus=True)
        address = ft.TextField(label="Dia chi / link hoc truc tuyen", value=lesson.address if lesson else "")
        day = ft.TextField(label="Ngay (YYYY-MM-DD)", value=source.strftime("%Y-%m-%d"))
        start = ft.TextField(label="Bat dau", value=source.strftime("%H:%M"), expand=True)
        finish = ft.TextField(label="Ket thuc", value=end.strftime("%H:%M"), expand=True)
        room = ft.TextField(label="Phong hoc", value=lesson.room if lesson else "")
        note = ft.TextField(label="Ghi chu", value=lesson.note if lesson else "", multiline=True, min_lines=2)
        error = ft.Text(color=THEME["danger"], size=12)
        swatches = self._color_swatches(chosen)

        def save(_):
            try:
                selected_day = datetime.strptime(day.value.strip(), "%Y-%m-%d").date()
                begins = datetime.combine(selected_day, datetime.strptime(start.value.strip(), "%H:%M").time())
                ends = datetime.combine(selected_day, datetime.strptime(finish.value.strip(), "%H:%M").time())
                if not title.value.strip():
                    raise ValueError("Ban chua nhap ten lich")
                if ends <= begins:
                    raise ValueError("Gio ket thuc phai sau gio bat dau")
            except ValueError as exc:
                error.value = str(exc)
                self.page.update()
                return

            self.repository.save(
                Lesson(
                    id=lesson.id if lesson else None,
                    title=title.value.strip(),
                    address=address.value.strip(),
                    start_at=begins,
                    end_at=ends,
                    room=room.value.strip(),
                    note=note.value.strip(),
                    color=chosen[0],
                )
            )
            self.page.pop_dialog()
            self.on_saved(selected_day)

        def delete(_):
            if lesson and lesson.id is not None:
                self.repository.delete(lesson.id)
            self.page.pop_dialog()
            self.on_saved(lesson.start_at.date() if lesson else date.today())

        actions = []
        if lesson:
            actions.append(ft.TextButton("Xoa", icon=ft.Icons.DELETE_OUTLINE, on_click=delete, style=ft.ButtonStyle(color=THEME["danger"])))
        actions += [ft.TextButton("Huy", on_click=lambda _: self.page.pop_dialog()), ft.Button("Luu", on_click=save)]

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Sua lich" if lesson else "Them lich"),
            content=ft.Container(
                ft.Column(
                    [
                        title,
                        address,
                        day,
                        ft.Row([start, finish]),
                        room,
                        note,
                        ft.Text("Mau lich", weight=ft.FontWeight.BOLD),
                        ft.Row(swatches),
                        error,
                    ],
                    tight=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=420,
            ),
            actions=actions,
        )
        self.page.show_dialog(dialog)

    def _color_swatches(self, chosen: list[str]):
        swatches = []

        def choose(e):
            chosen[0] = e.control.data
            for item in swatches:
                item.border = ft.Border.all(3, THEME["text"]) if item.data == chosen[0] else None
            self.page.update()

        for color in COLORS:
            swatches.append(
                ft.Container(
                    width=34,
                    height=34,
                    bgcolor=color,
                    border_radius=17,
                    data=color,
                    border=ft.Border.all(3, THEME["text"]) if color == chosen[0] else None,
                    on_click=choose,
                )
            )
        return swatches
