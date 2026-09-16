"""Application shell for the mobile timetable app."""

import calendar
import os
from datetime import date, datetime, time, timedelta
from pathlib import Path

import flet as ft

from components.calendar_cell import build_mini_calendar_day
from components.lesson_card import build_agenda_item
from components.mode_button import build_mode_button
from components.sidebar import build_sidebar
from components.toolbar import build_toolbar
from constants import DARK_THEME, DAYS, DAY_WIDTH, END_HOUR, HOUR_HEIGHT, LESSON_PALETTE, LIGHT_THEME, START_HOUR
from features.calendar import render_day_view, render_month_view, render_week_view, render_year_view
from features.lessons import LessonDialogFeature
from features.screenshot import ScreenshotFeature
from features.settings import SettingsFeature
from models.lesson import Lesson
from models.fixed_lesson import FixedLesson
from repositories.lesson_repository import LessonRepository
from repositories.fixed_lesson_repository import FixedLessonRepository
from utils.date_utils import month_range, week_start, year_range


def get_database_path() -> Path:
    storage = os.getenv("FLET_APP_STORAGE_DATA")
    folder = Path(storage) if storage else Path(__file__).parent / "data"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "timetable.db"


class TimetableApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.repo = LessonRepository(str(get_database_path()))
        self.fixed_repo = FixedLessonRepository(str(get_database_path()))
        self.theme = LIGHT_THEME
        self.settings = SettingsFeature(page, self.set_dark_mode)
        self.screenshot = ScreenshotFeature(page, get_database_path().parent / "screenshots")
        self.lesson_dialog = LessonDialogFeature(page, self.repo, self.after_lesson_saved)
        self.selected = date.today()
        self.monday = week_start(self.selected)
        self.query = ""
        self.view_mode = "week"
        self.drag_selection = None
        self.is_compact = False
        self.fixed_mode = False
        self.fixed_selected: set[tuple[int, int]] = set()
        self.fixed_drag_selection = None

        page.title = "Thoi khoa bieu"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = self.theme["page"]
        page.padding = 0
        page.enable_screenshots = True
        page.on_resized = lambda _: self.on_resize()

        self.period_title = ft.Text(size=16, weight=ft.FontWeight.BOLD, color=self.theme["text"])
        self.side_month = ft.Text(size=25, weight=ft.FontWeight.BOLD, color=self.theme["sidebar_text"])
        self.mini_calendar = ft.Column(spacing=5, height=210)
        self.agenda = ft.ListView(spacing=5, expand=True)
        self.mode_row = ft.Row(spacing=6)
        self.board = ft.Row(spacing=0, vertical_alignment=ft.CrossAxisAlignment.START)
        self.board_scroll = ft.ListView([ft.Row([self.board], scroll=ft.ScrollMode.AUTO)], expand=True, padding=0)

        self.apply_responsive_size()
        self.sidebar = build_sidebar(self.side_month, self.mini_calendar, self.agenda, self.theme, self.sidebar_width())
        self.toolbar = build_toolbar(
            period_title=self.period_title,
            mode_row=self.mode_row,
            on_previous=lambda _: self.move_period(-1),
            on_today=lambda _: self.today(),
            on_next=lambda _: self.move_period(1),
            on_search=self.search,
            on_add=lambda _: self.open_editor(),
            on_fixed=lambda _: self.open_fixed_editor(),
            screenshot_button=self.screenshot.button(self.theme),
            settings_button=self.settings.button(self.theme),
            theme=self.theme,
            compact=self.is_compact,
        )
        self.calendar_panel = ft.Column([self.toolbar, self.board_scroll], spacing=0, expand=True)
        self.root_row = ft.Row([self.sidebar, self.calendar_panel], spacing=0, expand=True)
        page.add(ft.SafeArea(self.root_row, expand=True))
        self.refresh()

    def apply_responsive_size(self):
        width = self.page.width or 420
        self.is_compact = width < 760
        self.mini_calendar.height = 0 if self.is_compact else 210
        self.agenda.visible = not self.is_compact
        self.side_month.size = 16 if self.is_compact else 25
        self.period_title.size = 13 if self.is_compact else 16

    def sidebar_width(self) -> int:
        return 0 if self.is_compact else 255

    def day_column_width(self, column_count: int) -> int:
        width = self.page.width or 420
        if column_count == 1:
            return max(260, int(width - 72 - self.sidebar_width()))
        return 92 if self.is_compact else DAY_WIDTH

    def month_cell_width(self) -> int:
        return 82 if self.is_compact else 122

    def month_cell_height(self) -> int:
        return 92 if self.is_compact else 118

    def year_card_width(self) -> int:
        return 150 if self.is_compact else 190

    def year_card_height(self) -> int:
        return 168 if self.is_compact else 190

    def year_cards_per_row(self) -> int:
        return 2 if self.is_compact else 4

    def on_resize(self):
        previous_compact = self.is_compact
        self.apply_responsive_size()
        if previous_compact != self.is_compact:
            self.sidebar = build_sidebar(self.side_month, self.mini_calendar, self.agenda, self.theme, self.sidebar_width())
            self.root_row.controls[0] = self.sidebar
        self.refresh()

    def set_dark_mode(self, enabled: bool):
        self.theme = DARK_THEME if enabled else LIGHT_THEME
        self.page.theme_mode = ft.ThemeMode.DARK if enabled else ft.ThemeMode.LIGHT
        self.page.bgcolor = self.theme["page"]
        self.period_title.color = self.theme["text"]
        self.side_month.color = self.theme["sidebar_text"]
        self.apply_responsive_size()
        self.sidebar = build_sidebar(self.side_month, self.mini_calendar, self.agenda, self.theme, self.sidebar_width())
        self.toolbar = build_toolbar(
            period_title=self.period_title,
            mode_row=self.mode_row,
            on_previous=lambda _: self.move_period(-1),
            on_today=lambda _: self.today(),
            on_next=lambda _: self.move_period(1),
            on_search=self.search,
            on_add=lambda _: self.open_editor(),
            on_fixed=lambda _: self.open_fixed_editor(),
            screenshot_button=self.screenshot.button(self.theme),
            settings_button=self.settings.button(self.theme),
            theme=self.theme,
            compact=self.is_compact,
        )
        self.root_row.controls[0] = self.sidebar
        self.calendar_panel.controls[0] = self.toolbar
        self.refresh()

    def refresh(self):
        self.monday = week_start(self.selected)
        self.drag_selection = None
        self.render_mode_buttons()
        self.render_period_title()
        self.render_sidebar()

        if self.view_mode == "day":
            lessons = self.repo.list_for_day(self.selected)
            lessons += self.fixed_lessons_between(self.selected, self.selected)
            render_day_view(self, lessons)
        elif self.view_mode == "week":
            lessons = self.repo.list_between(self.monday, self.monday + timedelta(days=6))
            lessons += self.fixed_lessons_between(self.monday, self.monday + timedelta(days=6))
            render_week_view(self, lessons)
        elif self.view_mode == "month":
            start, end = month_range(self.selected)
            lessons = self.repo.list_between(start, end)
            lessons += self.fixed_lessons_between(start, end)
            render_month_view(self, lessons)
        else:
            start, end = year_range(self.selected)
            lessons = self.repo.list_between(start, end)
            lessons += self.fixed_lessons_between(start, end)
            render_year_view(self, lessons)

        self.page.update()

    def render_mode_buttons(self):
        labels = [("day", "Ngay"), ("week", "Tuan"), ("month", "Thang"), ("year", "Nam")]
        self.mode_row.controls = [
            build_mode_button(label, self.view_mode == mode, lambda _, value=mode: self.set_view_mode(value), self.theme)
            for mode, label in labels
        ]

    def render_period_title(self):
        if self.view_mode == "day":
            self.period_title.value = self.selected.strftime("%d/%m/%Y")
        elif self.view_mode == "week":
            self.period_title.value = f"{self.monday:%d/%m} - {(self.monday + timedelta(days=6)):%d/%m/%Y}"
        elif self.view_mode == "month":
            self.period_title.value = f"Thang {self.selected.month}/{self.selected.year}"
        else:
            self.period_title.value = str(self.selected.year)
        self.side_month.value = f"Thang {self.selected.month}  {self.selected.year}"

    def render_sidebar(self):
        start, end = month_range(self.selected)
        month_lessons = self.repo.list_between(start, end)
        self.agenda.controls.clear()
        if not month_lessons:
            self.agenda.controls.append(ft.Text("Chua co lich trong thang", color=self.theme["sidebar_muted"], size=12))
        for lesson in month_lessons[:8]:
            self.agenda.controls.append(build_agenda_item(lesson, lambda _, item=lesson: self.open_editor(item), self.theme))

        self.mini_calendar.controls.clear()
        self.mini_calendar.controls.append(
            ft.Row(
                [
                    ft.Container(
                        ft.Text(label, size=9, color=self.theme["sidebar_subtle"], text_align=ft.TextAlign.CENTER),
                        width=25,
                    )
                    for label in DAYS
                ],
                spacing=5,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
        )
        first_weekday, days_in_month = calendar.monthrange(self.selected.year, self.selected.month)
        cells = [None] * first_weekday + list(range(1, days_in_month + 1))
        cells += [None] * ((7 - len(cells) % 7) % 7)
        for start in range(0, len(cells), 7):
            week_cells = []
            for number in cells[start:start + 7]:
                if number is None:
                    week_cells.append(ft.Container(width=25, height=25))
                    continue
                value = date(self.selected.year, self.selected.month, number)
                week_cells.append(
                    build_mini_calendar_day(
                        number,
                        value == self.selected,
                        lambda _, selected_day=value: self.select_day(selected_day),
                        self.theme,
                    )
                )
            self.mini_calendar.controls.append(
                ft.Row(
                    week_cells,
                    spacing=5,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                )
            )

    def build_day_board(self, lessons: list[Lesson]):
        self.build_calendar_board([(self.selected, DAYS[self.selected.weekday()])], lessons)

    def build_week_board(self, lessons: list[Lesson]):
        days = [(self.monday + timedelta(days=offset), DAYS[offset]) for offset in range(7)]
        self.build_calendar_board(days, lessons)

    def fixed_lessons_for_week(self) -> list[Lesson]:
        return self.fixed_lessons_between(self.monday, self.monday + timedelta(days=6))

    def fixed_lessons_between(self, start: date, end: date) -> list[Lesson]:
        result = []
        fixed_items = self.fixed_repo.list_all()
        cursor = start
        while cursor <= end:
            for fixed in fixed_items:
                if fixed.weekday != cursor.weekday():
                    continue
                if fixed.effective_from and cursor < fixed.effective_from:
                    continue
                start_at = datetime.combine(cursor, fixed.start_time)
                end_day = cursor + timedelta(days=1) if fixed.end_time <= fixed.start_time else cursor
                result.append(
                    Lesson(
                        id=-fixed.id if fixed.id else None,
                        title=fixed.title,
                        start_at=start_at,
                        end_at=datetime.combine(end_day, fixed.end_time),
                        address=fixed.address,
                        room=fixed.room,
                        note=fixed.note,
                        color=fixed.color,
                    )
                )
            cursor += timedelta(days=1)
        return result

    def open_fixed_editor(self):
        self.fixed_mode = True
        self.fixed_selected = set()
        self.fixed_drag_selection = None
        self.calendar_panel.controls = [self.build_fixed_editor()]
        self.page.update()

    def close_fixed_editor(self):
        self.fixed_mode = False
        self.calendar_panel.controls = [self.toolbar, self.board_scroll]
        self.refresh()

    def build_fixed_editor(self):
        title = ft.Text("Lich co dinh", size=20, weight=ft.FontWeight.BOLD, color=self.theme["text"])
        hint = ft.Text("Chon o trong de tao lich. Bam vao card de sua hoac xoa.", color=self.theme["text_muted"])
        total_height = (END_HOUR - START_HOUR) * HOUR_HEIGHT
        column_width = self.day_column_width(7)
        fixed_by_day: dict[int, list[FixedLesson]] = {}
        for item in self.fixed_repo.list_all():
            fixed_by_day.setdefault(item.weekday, []).append(item)

        time_cells = [ft.Container(height=58)]
        for hour in range(START_HOUR, END_HOUR):
            time_cells.append(
                ft.Container(
                    ft.Text(f"{hour:02}:00", size=10, color=self.theme["text_subtle"]),
                    width=52,
                    height=HOUR_HEIGHT,
                    padding=ft.Padding.only(right=7, top=3),
                    alignment=ft.Alignment.TOP_RIGHT,
                    bgcolor=self.theme["surface_low"],
                    border=ft.Border(bottom=ft.BorderSide(1, self.theme["border"])),
                )
            )

        columns = [ft.Column(time_cells, spacing=0)]
        for weekday, label in enumerate(DAYS):
            stack_controls = []
            for slot in range(END_HOUR - START_HOUR):
                key = (weekday, slot)
                selected = key in self.fixed_selected
                stack_controls.append(
                    ft.Container(
                        top=slot * HOUR_HEIGHT,
                        left=0,
                        width=column_width,
                        height=HOUR_HEIGHT,
                        bgcolor=f"{self.theme['accent']}22" if selected else self.theme["surface"],
                        border=ft.Border(
                            bottom=ft.BorderSide(1, self.theme["border"]),
                            right=ft.BorderSide(1, self.theme["border"]),
                        ),
                    )
                )
            stack_controls.append(self.fixed_gesture_layer(weekday, column_width, total_height))
            for fixed in fixed_by_day.get(weekday, []):
                stack_controls.append(self.fixed_lesson_card(fixed, column_width, total_height))

            header = ft.Container(
                ft.Column(
                    [
                        ft.Text(label, size=10, color=self.theme["text_subtle"]),
                        ft.Icon(ft.Icons.PUSH_PIN_OUTLINED, size=17, color=self.theme["text"]),
                    ],
                    spacing=1,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=column_width,
                height=58,
                padding=7,
                bgcolor=self.theme["surface_high"],
                border=ft.Border(bottom=ft.BorderSide(1, self.theme["border"]), right=ft.BorderSide(1, self.theme["border"])),
            )
            columns.append(ft.Column([header, ft.Stack(stack_controls, width=column_width, height=total_height)], spacing=0))

        board = ft.ListView([ft.Row(columns, spacing=0, scroll=ft.ScrollMode.AUTO)], expand=True, padding=0)
        return ft.Column(
            [
                ft.Row([
                    ft.IconButton(ft.Icons.ARROW_BACK, on_click=lambda _: self.close_fixed_editor()),
                    title,
                    ft.Container(expand=True),
                    ft.Button("Done", icon=ft.Icons.CHECK, bgcolor=self.theme["accent"], color="#FFFFFF", on_click=lambda _: self.save_fixed_selection()),
                ]),
                hint,
                board,
            ],
            expand=True,
            spacing=8,
        )

    def fixed_lesson_card(self, fixed: FixedLesson, column_width: int, total_height: int):
        day = date.today()
        start_at = datetime.combine(day, fixed.start_time)
        end_day = day + timedelta(days=1) if fixed.end_time <= fixed.start_time else day
        lesson = Lesson(
            id=fixed.id,
            title=fixed.title,
            start_at=start_at,
            end_at=datetime.combine(end_day, fixed.end_time),
            address=fixed.address,
            room=fixed.room,
            note=fixed.note,
            color=fixed.color,
        )
        card = self.grid_lesson_card(lesson, column_width, total_height)
        card.on_click = lambda _, item=fixed: self.open_fixed_dialog(item)
        return card

    def fixed_gesture_layer(self, weekday: int, column_width: int, total_height: int):
        return ft.GestureDetector(
            content=ft.Container(width=column_width, height=total_height, bgcolor="#00000000"),
            top=0,
            left=0,
            on_double_tap_down=lambda event, day=weekday: self.double_tap_fixed_cell(day, self.event_y(event)),
            on_long_press_start=lambda event, day=weekday: self.start_fixed_drag(day, self.event_y(event)),
            on_long_press_move_update=lambda event, day=weekday: self.update_fixed_drag(day, self.event_y(event)),
            on_long_press_end=lambda event, day=weekday: self.finish_fixed_drag(day, self.event_y(event)),
        )

    def select_fixed_range(self, weekday: int, start_slot: int, end_slot: int):
        first = min(start_slot, end_slot)
        last = max(start_slot, end_slot)
        self.fixed_selected = {(weekday, slot) for slot in range(first, last + 1)}
        self.calendar_panel.controls = [self.build_fixed_editor()]
        self.page.update()

    def double_tap_fixed_cell(self, weekday: int, y: float):
        slot = self.slot_from_y(y)
        self.select_fixed_range(weekday, slot, slot)
        self.save_fixed_selection()

    def start_fixed_drag(self, weekday: int, y: float):
        slot = self.slot_from_y(y)
        self.fixed_drag_selection = {"weekday": weekday, "start_slot": slot, "end_slot": slot}

    def update_fixed_drag(self, weekday: int, y: float):
        if not self.fixed_drag_selection or self.fixed_drag_selection["weekday"] != weekday:
            return
        slot = self.slot_from_y(y)
        self.fixed_drag_selection["end_slot"] = slot

    def finish_fixed_drag(self, weekday: int, y: float):
        if not self.fixed_drag_selection or self.fixed_drag_selection["weekday"] != weekday:
            self.fixed_drag_selection = None
            self.refresh_fixed_surface()
            return
        slot = self.slot_from_y(y)
        start_slot = self.fixed_drag_selection["start_slot"]
        self.fixed_drag_selection = None
        self.select_fixed_range(weekday, start_slot, slot)
        self.save_fixed_selection()

    def save_fixed_selection(self):
        if not self.fixed_selected:
            self.close_fixed_editor()
            return
        slots = sorted(self.fixed_selected)
        weekdays = {weekday for weekday, _ in slots}
        first_slot = min(slot for _, slot in slots)
        last_slot = max(slot for _, slot in slots)
        default_start = time(START_HOUR + first_slot, 0)
        end_hour = START_HOUR + last_slot + 1
        default_end = time(end_hour, 0) if end_hour < 24 else time(23, 59)
        default_effective = date(self.selected.year, self.selected.month, 1)

        title = ft.TextField(label="Ten lich co dinh", autofocus=True)
        start = ft.TextField(label="Bat dau", value=default_start.strftime("%H:%M"), expand=True)
        finish = ft.TextField(label="Ket thuc", value=default_end.strftime("%H:%M"), expand=True)
        effective_from = ft.TextField(label="Ap dung tu ngay", value=default_effective.strftime("%Y-%m-%d"))
        room = ft.TextField(label="Phong hoc", value="")
        note = ft.TextField(label="Ghi chu", value="", multiline=True, min_lines=2)
        error = ft.Text(color=self.theme["danger"])

        def parse_clock(value: str) -> time:
            return datetime.strptime(value.strip(), "%H:%M").time()

        def save(_):
            try:
                start_time = parse_clock(start.value)
                end_time = parse_clock(finish.value)
                starts_on = datetime.strptime(effective_from.value.strip(), "%Y-%m-%d").date()
            except ValueError:
                error.value = "Gio phai la HH:MM, ngay phai la YYYY-MM-DD"
                self.page.update()
                return
            if not title.value.strip():
                error.value = "Ban chua nhap ten lich"
                self.page.update()
                return
            for weekday in sorted(weekdays):
                self.fixed_repo.save(FixedLesson(
                    weekday=weekday,
                    start_time=start_time,
                    end_time=end_time,
                    title=title.value.strip(),
                    room=room.value.strip(),
                    note=note.value.strip(),
                    effective_from=starts_on,
                ))
            self.page.pop_dialog()
            self.fixed_selected = set()
            self.refresh_fixed_surface()

        self.page.show_dialog(ft.AlertDialog(
            modal=True,
            title=ft.Text("Luu lich co dinh"),
            content=ft.Column([title, ft.Row([start, finish]), effective_from, room, note, error], tight=True),
            actions=[ft.TextButton("Huy", on_click=lambda _: self.page.pop_dialog()), ft.Button("Luu", on_click=save)],
        ))

    def open_fixed_dialog(self, fixed: FixedLesson):
        title = ft.TextField(label="Ten lich co dinh", value=fixed.title, autofocus=True)
        start = ft.TextField(label="Bat dau", value=fixed.start_time.strftime("%H:%M"), expand=True)
        finish = ft.TextField(label="Ket thuc", value=fixed.end_time.strftime("%H:%M"), expand=True)
        effective_from = ft.TextField(
            label="Ap dung tu ngay",
            value=(fixed.effective_from or date.today().replace(day=1)).strftime("%Y-%m-%d"),
        )
        room = ft.TextField(label="Phong hoc", value=fixed.room)
        note = ft.TextField(label="Ghi chu", value=fixed.note, multiline=True, min_lines=2)
        error = ft.Text(color=self.theme["danger"])

        def parse_clock(value: str) -> time:
            return datetime.strptime(value.strip(), "%H:%M").time()

        def save(_):
            try:
                start_time = parse_clock(start.value)
                end_time = parse_clock(finish.value)
                starts_on = datetime.strptime(effective_from.value.strip(), "%Y-%m-%d").date()
            except ValueError:
                error.value = "Gio phai la HH:MM, ngay phai la YYYY-MM-DD"
                self.page.update()
                return
            if not title.value.strip():
                error.value = "Ban chua nhap ten lich"
                self.page.update()
                return
            self.fixed_repo.save(FixedLesson(
                id=fixed.id,
                weekday=fixed.weekday,
                start_time=start_time,
                end_time=end_time,
                title=title.value.strip(),
                room=room.value.strip(),
                note=note.value.strip(),
                color=fixed.color,
                address=fixed.address,
                effective_from=starts_on,
            ))
            self.page.pop_dialog()
            self.refresh_fixed_surface()

        def delete(_):
            if fixed.id is not None:
                self.fixed_repo.delete(fixed.id)
            self.page.pop_dialog()
            self.refresh_fixed_surface()

        self.page.show_dialog(ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Lich co dinh - {DAYS[fixed.weekday]}"),
            content=ft.Column([title, ft.Row([start, finish]), effective_from, room, note, error], tight=True),
            actions=[
                ft.TextButton("Xoa", icon=ft.Icons.DELETE_OUTLINE, on_click=delete),
                ft.TextButton("Huy", on_click=lambda _: self.page.pop_dialog()),
                ft.Button("Luu", on_click=save),
            ],
        ))

    def refresh_fixed_surface(self):
        if self.fixed_mode:
            self.calendar_panel.controls = [self.build_fixed_editor()]
            self.page.update()
            return
        self.refresh()

    def build_calendar_board(self, days: list[tuple[date, str]], lessons: list[Lesson]):
        if self.query:
            lessons = [lesson for lesson in lessons if self.query in lesson.title.casefold()]

        total_height = (END_HOUR - START_HOUR) * HOUR_HEIGHT
        time_cells = [ft.Container(height=58)]
        for hour in range(START_HOUR, END_HOUR):
            time_cells.append(
                ft.Container(
                    ft.Text(f"{hour:02}:00", size=10, color=self.theme["text_subtle"]),
                    width=52,
                    height=HOUR_HEIGHT,
                    padding=ft.Padding.only(right=7, top=3),
                    alignment=ft.Alignment.TOP_RIGHT,
                    bgcolor=self.theme["surface_low"],
                    border=ft.Border(bottom=ft.BorderSide(1, self.theme["border"])),
                )
            )
        self.board.controls = [ft.Column(time_cells, spacing=0)]

        today = date.today()
        column_width = self.day_column_width(len(days))
        for current, day_name in days:
            is_today = current == today
            stack_controls = []
            for slot in range(END_HOUR - START_HOUR):
                stack_controls.append(
                    ft.Container(
                        top=slot * HOUR_HEIGHT,
                        left=0,
                        width=column_width,
                        height=HOUR_HEIGHT,
                        bgcolor=self.theme["today"] if is_today else self.theme["surface"],
                        border=ft.Border(
                            bottom=ft.BorderSide(1, self.theme["border"]),
                            right=ft.BorderSide(1, self.theme["border"]),
                        ),
                    )
                )
            stack_controls.append(self.grid_gesture_layer(current, column_width, total_height))
            if self.drag_selection and self.drag_selection["day"] == current:
                stack_controls.append(self.drag_preview(column_width))
            for lesson in lessons:
                if lesson.start_at.date() == current:
                    stack_controls.append(self.grid_lesson_card(lesson, column_width, total_height))

            header = ft.Container(
                ft.Column(
                    [
                        ft.Text(day_name, size=10, color=self.theme["text_subtle"]),
                        ft.Text(str(current.day), size=18, weight=ft.FontWeight.BOLD, color=self.theme["text"]),
                    ],
                    spacing=1,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=column_width,
                height=58,
                padding=7,
                bgcolor=self.theme["today"] if is_today else self.theme["surface_high"],
                border=ft.Border(bottom=ft.BorderSide(1, self.theme["border"]), right=ft.BorderSide(1, self.theme["border"])),
                on_click=lambda _, selected_day=current: self.select_day(selected_day),
            )
            self.board.controls.append(
                ft.Column([header, ft.Stack(stack_controls, width=column_width, height=total_height)], spacing=0)
            )

    def grid_gesture_layer(self, current: date, column_width: int, total_height: int):
        return ft.GestureDetector(
            content=ft.Container(width=column_width, height=total_height, bgcolor="#00000000"),
            top=0,
            left=0,
            on_tap_down=lambda event, selected_day=current: self.open_editor(
                initial=self.datetime_from_grid_position(selected_day, self.event_y(event))
            ),
            on_long_press_start=lambda event, selected_day=current: self.start_drag_create(selected_day, self.event_y(event)),
            on_long_press_move_update=lambda event, selected_day=current: self.update_drag_create(selected_day, self.event_y(event)),
            on_long_press_end=lambda event, selected_day=current: self.finish_drag_create(selected_day, self.event_y(event)),
        )

    def drag_preview(self, column_width: int):
        start_slot = min(self.drag_selection["start_slot"], self.drag_selection["end_slot"])
        end_slot = max(self.drag_selection["start_slot"], self.drag_selection["end_slot"]) + 1
        return ft.Container(
            top=start_slot * HOUR_HEIGHT + 2,
            left=3,
            width=column_width - 6,
            height=(end_slot - start_slot) * HOUR_HEIGHT - 4,
            bgcolor=f"{self.theme['danger']}33",
            border=ft.Border(left=ft.BorderSide(3, self.theme["danger"])),
            border_radius=5,
        )

    def grid_lesson_card(self, lesson: Lesson, column_width: int, total_height: int):
        start_minutes = (lesson.start_at.hour - START_HOUR) * 60 + lesson.start_at.minute
        duration = max(30, int((lesson.end_at - lesson.start_at).total_seconds() / 60))
        top = max(0, start_minutes / 60 * HOUR_HEIGHT)
        height = max(36, duration / 60 * HOUR_HEIGHT)
        if top >= total_height:
            return ft.Container()
        card_bg, title_color, meta_color = self.lesson_colors(lesson.color)
        return ft.Container(
            ft.Column(
                [
                    ft.Text(lesson.start_at.strftime("%H:%M"), size=9, color=meta_color, weight=ft.FontWeight.BOLD),
                    ft.Text(
                        lesson.title,
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color=title_color,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(lesson.room, size=9, color=title_color, opacity=0.75, visible=bool(lesson.room)),
                ],
                spacing=1,
            ),
            top=top + 2,
            left=3,
            width=column_width - 6,
            height=min(height - 4, total_height - top - 2),
            bgcolor=card_bg,
            padding=5,
            border_radius=5,
            border=ft.Border(left=ft.BorderSide(3, lesson.color)),
            on_click=lambda _, item=lesson: self.open_lesson_item(item),
        )

    def open_lesson_item(self, lesson: Lesson):
        if lesson.id is None or lesson.id > 0:
            self.open_editor(lesson)
            return
        fixed_id = -lesson.id
        fixed = next((item for item in self.fixed_repo.list_all() if item.id == fixed_id), None)
        if fixed:
            self.open_fixed_dialog(fixed)

    def lesson_colors(self, color: str):
        palette = LESSON_PALETTE.get(color, LESSON_PALETTE["#20A4E8"])
        if self.theme is DARK_THEME:
            return palette["dark_bg"], "#FFFFFF", color
        return palette["light_bg"], "#1F2937", palette["text"]

    def build_month_board(self, lessons: list[Lesson]):
        if self.query:
            lessons = [lesson for lesson in lessons if self.query in lesson.title.casefold()]
        lessons_by_day: dict[date, list[Lesson]] = {}
        for lesson in lessons:
            lessons_by_day.setdefault(lesson.start_at.date(), []).append(lesson)

        first = date(self.selected.year, self.selected.month, 1)
        cursor = week_start(first)
        rows = []
        for _ in range(6):
            row = []
            for _ in range(7):
                row.append(self.month_day_cell(cursor, lessons_by_day.get(cursor, [])))
                cursor += timedelta(days=1)
            rows.append(ft.Row(row, spacing=0))
            if cursor.month != self.selected.month and cursor.day >= 7:
                break

        header = ft.Row(
            [
                ft.Container(
                    ft.Text(label, size=11, color=self.theme["text_subtle"], text_align=ft.TextAlign.CENTER),
                    width=self.month_cell_width(),
                    padding=8,
                    bgcolor=self.theme["surface_low"],
                )
                for label in DAYS
            ],
            spacing=0,
        )
        self.board.controls = [ft.Column([header, *rows], spacing=0)]

    def month_day_cell(self, value: date, lessons: list[Lesson]):
        active_month = value.month == self.selected.month
        active_day = value == self.selected

        lesson_items = []

        for lesson in lessons[:3]:
            card_bg, title_color, _ = self.lesson_colors(lesson.color)
            lesson_items.append(
                ft.Container(
                    content=ft.Text(
                        lesson.title,
                        size=9,
                        color=title_color,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),

                    width=max(62, self.month_cell_width() - 14) if active_month else None,

                    bgcolor=card_bg,

                    border=ft.Border(
                        left=ft.BorderSide(
                            3,
                            lesson.color,
                        )
                    ),

                    padding=ft.Padding.symmetric(
                        horizontal=5,
                        vertical=3,
                    ),

                    border_radius=4,

                    on_click=(
                        (lambda _, item=lesson: self.open_editor(item))
                        if active_month
                        else None
                    ),
                )
            )

        if len(lessons) > 3:
            lesson_items.append(
                ft.Text(
                    f"+{len(lessons) - 3} lich",
                    size=9,
                    color=self.theme["text_muted"],
                )
            )

        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        str(value.day),
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=(
                            self.theme["danger"]
                            if active_day
                            else self.theme["text"]
                        ),
                    ),
                    *lesson_items,
                ],
                spacing=4,
            ),

            width=self.month_cell_width(),
            height=self.month_cell_height(),
            padding=7,

            bgcolor=(
                self.theme["surface"]
                if active_month
                else self.theme["surface_low"]
            ),

            border=ft.Border(
                bottom=ft.BorderSide(
                    1,
                    self.theme["border"],
                ),
                right=ft.BorderSide(
                    1,
                    self.theme["border"],
                ),
            ),

            on_click=lambda _, selected_day=value: self.select_day(
                selected_day
            ),
        )
    def build_year_board(self, lessons: list[Lesson]):
        lessons_by_month: dict[int, list[Lesson]] = {
            month: [] for month in range(1, 13)
        }

        for lesson in lessons:
            if self.query and self.query not in lesson.title.casefold():
                continue

            lessons_by_month[lesson.start_at.month].append(lesson)

        cards = [
            self.year_month_card(
                month,
                lessons_by_month[month],
            )
            for month in range(1, 13)
        ]

        per_row = self.year_cards_per_row()
        rows = [
            ft.Row(
                cards[index:index + per_row],
                spacing=12,
            )
            for index in range(0, 12, per_row)
        ]

        self.board.controls = [
            ft.Column(
                rows,
                spacing=12,
            )
        ]

    def year_month_card(
        self,
        month: int,
        lessons: list[Lesson],
    ):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        f"Thang {month}",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=self.theme["text"],
                    ),

                    ft.Text(
                        f"{len(lessons)} lich",
                        size=12,
                        color=self.theme["text_muted"],
                    ),

                    ft.Container(
                        height=1,
                        bgcolor=self.theme["border"],
                    ),

                    self.small_month(
                        month,
                        lessons,
                    ),
                ],
                spacing=8,
            ),

            width=self.year_card_width(),
            height=self.year_card_height(),
            padding=12,

            bgcolor=self.theme["surface"],

            border_radius=8,

            border=ft.Border.all(
                1,
                self.theme["border"],
            ),

            on_click=lambda _, selected_month=month: self.select_month(
                selected_month
            ),
        )
    def small_month(
        self,
        month: int,
        lessons: list[Lesson],
    ):
        grid = ft.GridView(
            runs_count=7,
            max_extent=19,
            spacing=1,
            run_spacing=1,
            height=94,
        )

        first_weekday, days_in_month = calendar.monthrange(
            self.selected.year,
            month,
        )

        lesson_days = {
            lesson.start_at.day
            for lesson in lessons
        }

        for _ in range(first_weekday):
            grid.controls.append(
                ft.Container()
            )

        for number in range(1, days_in_month + 1):
            has_lesson = number in lesson_days

            grid.controls.append(
                ft.Container(
                    content=ft.Text(
                        str(number),
                        size=8,
                        color=(
                            "#FFFFFF"
                            if has_lesson
                            else self.theme["text_muted"]
                        ),
                        text_align=ft.TextAlign.CENTER,
                    ),

                    width=18,
                    height=18,

                    alignment=ft.Alignment.CENTER,

                    bgcolor=(
                        self.theme["accent"]
                        if has_lesson
                        else None
                    ),

                    border_radius=9,

                    on_click=lambda _, day=number, selected_month=month:
                        self.select_day(
                            date(
                                self.selected.year,
                                selected_month,
                                day,
                            )
                        ),
                )
            )

        return grid

    @staticmethod
    def event_y(event) -> float:
        position = getattr(event, "local_position", None)
        if position is None:
            return 0
        return float(getattr(position, "y", 0) or 0)

    @staticmethod
    def slot_from_y(y: float) -> int:
        max_slot = END_HOUR - START_HOUR - 1
        return max(0, min(max_slot, int(y // HOUR_HEIGHT)))

    def datetime_from_grid_position(self, selected_day: date, y: float) -> datetime:
        slot = self.slot_from_y(y)
        return datetime.combine(selected_day, datetime.min.time()).replace(hour=START_HOUR + slot)

    def start_drag_create(self, selected_day: date, y: float):
        slot = self.slot_from_y(y)
        self.drag_selection = {"day": selected_day, "start_slot": slot, "end_slot": slot}
        self.page.update()

    def update_drag_create(self, selected_day: date, y: float):
        if not self.drag_selection or self.drag_selection["day"] != selected_day:
            return
        self.drag_selection["end_slot"] = self.slot_from_y(y)
        self.page.update()

    def finish_drag_create(self, selected_day: date, y: float):
        if not self.drag_selection or self.drag_selection["day"] != selected_day:
            self.drag_selection = None
            self.refresh()
            return
        self.drag_selection["end_slot"] = self.slot_from_y(y)
        start_slot = min(self.drag_selection["start_slot"], self.drag_selection["end_slot"])
        end_slot = max(self.drag_selection["start_slot"], self.drag_selection["end_slot"]) + 1
        self.drag_selection = None
        begins = datetime.combine(selected_day, datetime.min.time()).replace(hour=START_HOUR + start_slot)
        ends = datetime.combine(selected_day, datetime.min.time()).replace(hour=START_HOUR + end_slot)
        self.open_editor(initial=begins, initial_end=ends)

    def debug_action(self, action: str, **details):
        extra = " | ".join(f"{key}={value}" for key, value in details.items())
        message = (
            f"[DEBUG] {action} | view={self.view_mode} | selected={self.selected}"
        )
        if extra:
            message += f" | {extra}"
        print(message)

    def set_view_mode(self, mode: str):
        self.debug_action("SET_VIEW_MODE", target=mode)
        self.view_mode = mode
        self.refresh()

    def select_day(self, value: date):
        self.debug_action("SELECT_DAY", target=value)
        self.selected = value
        self.monday = week_start(value)
        self.refresh()

    def select_month(self, month: int):
        self.debug_action("SELECT_MONTH", target=month)
        self.selected = date(self.selected.year, month, 1)
        self.view_mode = "month"
        self.refresh()

    def search(self, event):
        value = (event.control.value or "").casefold().strip()
        self.debug_action("SEARCH", query=value)
        self.query = value
        self.refresh()

    def move_period(self, direction: int):
        self.debug_action("MOVE_PERIOD", direction=direction)
        if self.view_mode == "day":
            self.selected += timedelta(days=direction)
        elif self.view_mode == "week":
            self.selected += timedelta(days=direction * 7)
        elif self.view_mode == "month":
            month = self.selected.month + direction
            year = self.selected.year
            if month < 1:
                month, year = 12, year - 1
            elif month > 12:
                month, year = 1, year + 1
            day = min(self.selected.day, calendar.monthrange(year, month)[1])
            self.selected = date(year, month, day)
        else:
            self.selected = date(self.selected.year + direction, self.selected.month, self.selected.day)
        self.monday = week_start(self.selected)
        self.refresh()

    def today(self):
        self.debug_action("TODAY")
        self.selected = date.today()
        self.monday = week_start(self.selected)
        self.refresh()

    def open_editor(
        self,
        lesson: Lesson | None = None,
        initial: datetime | None = None,
        initial_end: datetime | None = None,
    ):
        self.debug_action(
            "OPEN_EDITOR",
            lesson_id=getattr(lesson, "id", None),
            initial=initial,
            initial_end=initial_end,
        )
        if lesson is None and initial is None:
            initial = datetime.combine(self.selected, datetime.now().time()).replace(second=0, microsecond=0)
        self.lesson_dialog.open(lesson=lesson, initial=initial, initial_end=initial_end)

    def after_lesson_saved(self, selected_day: date):
        self.selected = selected_day
        self.monday = week_start(selected_day)
        self.refresh()


def build_app(page: ft.Page):
    TimetableApp(page)


def run():
    ft.run(build_app)
