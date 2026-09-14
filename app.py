"""Application shell for the mobile timetable app."""

import calendar
import os
from datetime import date, datetime, timedelta
from pathlib import Path

import flet as ft

from components.calendar_cell import build_mini_calendar_day
from components.lesson_card import build_agenda_item
from components.mode_button import build_mode_button
from components.sidebar import build_sidebar
from components.toolbar import build_toolbar
from constants import DAYS, DAY_WIDTH, END_HOUR, HOUR_HEIGHT, START_HOUR
from features.calendar import render_day_view, render_month_view, render_week_view, render_year_view
from features.lessons import LessonDialogFeature
from features.settings import SettingsFeature
from models.lesson import Lesson
from repositories.lesson_repository import LessonRepository
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
        self.settings = SettingsFeature(page)
        self.lesson_dialog = LessonDialogFeature(page, self.repo, self.after_lesson_saved)
        self.selected = date.today()
        self.monday = week_start(self.selected)
        self.query = ""
        self.view_mode = "week"
        self.drag_selection = None

        page.title = "Thoi khoa bieu"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.bgcolor = "#F7F7FA"
        page.padding = 0

        self.period_title = ft.Text(size=16, weight=ft.FontWeight.BOLD, color="#25272C")
        self.side_month = ft.Text(size=25, weight=ft.FontWeight.BOLD, color="#F7F7F8")
        self.mini_calendar = ft.GridView(runs_count=7, max_extent=28, spacing=2, run_spacing=2, height=178)
        self.agenda = ft.ListView(spacing=5, expand=True)
        self.mode_row = ft.Row(spacing=6)
        self.board = ft.Row(spacing=0, vertical_alignment=ft.CrossAxisAlignment.START)
        self.board_scroll = ft.ListView([ft.Row([self.board], scroll=ft.ScrollMode.AUTO)], expand=True, padding=0)

        sidebar = build_sidebar(self.side_month, self.mini_calendar, self.agenda)
        toolbar = build_toolbar(
            period_title=self.period_title,
            mode_row=self.mode_row,
            on_previous=lambda _: self.move_period(-1),
            on_today=lambda _: self.today(),
            on_next=lambda _: self.move_period(1),
            on_search=self.search,
            on_add=lambda _: self.open_editor(),
            settings_button=self.settings.button(),
        )
        calendar_panel = ft.Column([toolbar, self.board_scroll], spacing=0, expand=True)
        page.add(ft.SafeArea(ft.Row([sidebar, calendar_panel], spacing=0, expand=True), expand=True))
        self.refresh()

    def refresh(self):
        self.monday = week_start(self.selected)
        self.drag_selection = None
        self.render_mode_buttons()
        self.render_period_title()
        self.render_sidebar()

        if self.view_mode == "day":
            render_day_view(self, self.repo.list_for_day(self.selected))
        elif self.view_mode == "week":
            render_week_view(self, self.repo.list_between(self.monday, self.monday + timedelta(days=6)))
        elif self.view_mode == "month":
            start, end = month_range(self.selected)
            render_month_view(self, self.repo.list_between(start, end))
        else:
            start, end = year_range(self.selected)
            render_year_view(self, self.repo.list_between(start, end))

        self.page.update()

    def render_mode_buttons(self):
        labels = [("day", "Ngay"), ("week", "Tuan"), ("month", "Thang"), ("year", "Nam")]
        self.mode_row.controls = [
            build_mode_button(label, self.view_mode == mode, lambda _, value=mode: self.set_view_mode(value))
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
            self.agenda.controls.append(ft.Text("Chua co lich trong thang", color="#AAAEB7", size=12))
        for lesson in month_lessons[:8]:
            self.agenda.controls.append(build_agenda_item(lesson, lambda _, item=lesson: self.open_editor(item)))

        self.mini_calendar.controls.clear()
        for label in DAYS:
            self.mini_calendar.controls.append(ft.Text(label, size=9, color="#989AA2", text_align=ft.TextAlign.CENTER))
        first_weekday, days_in_month = calendar.monthrange(self.selected.year, self.selected.month)
        for _ in range(first_weekday):
            self.mini_calendar.controls.append(ft.Container())
        for number in range(1, days_in_month + 1):
            value = date(self.selected.year, self.selected.month, number)
            active = value == self.selected
            self.mini_calendar.controls.append(
                build_mini_calendar_day(number, active, lambda _, selected_day=value: self.select_day(selected_day))
            )

    def build_day_board(self, lessons: list[Lesson]):
        self.build_calendar_board([(self.selected, DAYS[self.selected.weekday()])], lessons)

    def build_week_board(self, lessons: list[Lesson]):
        days = [(self.monday + timedelta(days=offset), DAYS[offset]) for offset in range(7)]
        self.build_calendar_board(days, lessons)

    def build_calendar_board(self, days: list[tuple[date, str]], lessons: list[Lesson]):
        if self.query:
            lessons = [lesson for lesson in lessons if self.query in lesson.title.casefold()]

        total_height = (END_HOUR - START_HOUR) * HOUR_HEIGHT
        time_cells = [ft.Container(height=58)]
        for hour in range(START_HOUR, END_HOUR):
            time_cells.append(
                ft.Container(
                    ft.Text(f"{hour:02}:00", size=10, color="#85888F"),
                    width=52,
                    height=HOUR_HEIGHT,
                    padding=ft.Padding.only(right=7, top=3),
                    alignment=ft.Alignment.TOP_RIGHT,
                    border=ft.Border(bottom=ft.BorderSide(1, "#E7E8EA")),
                )
            )
        self.board.controls = [ft.Column(time_cells, spacing=0)]

        today = date.today()
        column_width = 360 if len(days) == 1 else DAY_WIDTH
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
                        bgcolor="#EEF5FF" if is_today else "#FFFFFF",
                        border=ft.Border(
                            bottom=ft.BorderSide(1, "#E7E8EA"),
                            right=ft.BorderSide(1, "#E7E8EA"),
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
                        ft.Text(day_name, size=10, color="#777A81"),
                        ft.Text(str(current.day), size=18, weight=ft.FontWeight.BOLD, color="#25272C"),
                    ],
                    spacing=1,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=column_width,
                height=58,
                padding=7,
                bgcolor="#EEF5FF" if is_today else "#FFFFFF",
                border=ft.Border(bottom=ft.BorderSide(1, "#E4E5E7"), right=ft.BorderSide(1, "#E4E5E7")),
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
            bgcolor="#DF292922",
            border=ft.Border(left=ft.BorderSide(3, "#DF2929")),
            border_radius=5,
        )

    def grid_lesson_card(self, lesson: Lesson, column_width: int, total_height: int):
        start_minutes = (lesson.start_at.hour - START_HOUR) * 60 + lesson.start_at.minute
        duration = max(30, int((lesson.end_at - lesson.start_at).total_seconds() / 60))
        top = max(0, start_minutes / 60 * HOUR_HEIGHT)
        height = max(36, duration / 60 * HOUR_HEIGHT)
        if top >= total_height:
            return ft.Container()
        return ft.Container(
            ft.Column(
                [
                    ft.Text(lesson.start_at.strftime("%H:%M"), size=9, color=lesson.color),
                    ft.Text(
                        lesson.title,
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color="#20242A",
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(lesson.room, size=9, color="#555A62", visible=bool(lesson.room)),
                ],
                spacing=1,
            ),
            top=top + 2,
            left=3,
            width=column_width - 6,
            height=min(height - 4, total_height - top - 2),
            bgcolor=f"{lesson.color}2A",
            padding=5,
            border_radius=5,
            border=ft.Border(left=ft.BorderSide(3, lesson.color)),
            on_click=lambda _, item=lesson: self.open_editor(item),
        )

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
                ft.Container(ft.Text(label, size=11, color="#777A81", text_align=ft.TextAlign.CENTER), width=122, padding=8)
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
            lesson_items.append(
                ft.Container(
                    content=ft.Text(
                        lesson.title,
                        size=9,
                        color=ft.Colors.ON_SURFACE,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),

                    width=110 if active_month else None,

                    bgcolor=f"{lesson.color}2A",

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
                    color=ft.Colors.ON_SURFACE_VARIANT,
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
                            "#DF2929"
                            if active_day
                            else ft.Colors.ON_SURFACE
                        ),
                    ),
                    *lesson_items,
                ],
                spacing=4,
            ),

            width=122,
            height=118,
            padding=7,

            bgcolor=(
                ft.Colors.SURFACE
                if active_month
                else ft.Colors.SURFACE_CONTAINER_LOW
            ),

            border=ft.Border(
                bottom=ft.BorderSide(
                    1,
                    ft.Colors.OUTLINE_VARIANT,
                ),
                right=ft.BorderSide(
                    1,
                    ft.Colors.OUTLINE_VARIANT,
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

        rows = [
            ft.Row(
                cards[index:index + 4],
                spacing=12,
            )
            for index in range(0, 12, 4)
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
                        color=ft.Colors.ON_SURFACE,
                    ),

                    ft.Text(
                        f"{len(lessons)} lich",
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),

                    ft.Container(
                        height=1,
                        bgcolor=ft.Colors.OUTLINE_VARIANT,
                    ),

                    self.small_month(
                        month,
                        lessons,
                    ),
                ],
                spacing=8,
            ),

            width=190,
            height=190,
            padding=12,

            bgcolor=ft.Colors.SURFACE_CONTAINER_LOW,

            border_radius=8,

            border=ft.Border.all(
                1,
                ft.Colors.OUTLINE_VARIANT,
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
                            else ft.Colors.ON_SURFACE_VARIANT
                        ),
                        text_align=ft.TextAlign.CENTER,
                    ),

                    width=18,
                    height=18,

                    alignment=ft.Alignment.CENTER,

                    bgcolor=(
                        "#3578F6"
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
