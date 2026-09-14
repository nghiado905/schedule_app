import flet as ft

from models.lesson import Lesson


def build_agenda_item(lesson: Lesson, on_click):
    return ft.Container(
        ft.Column(
            [
                ft.Text(lesson.start_at.strftime("%d/%m  %H:%M"), color=lesson.color, size=10),
                ft.Text(
                    lesson.title,
                    color="#F1F1F3",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
            spacing=2,
        ),
        padding=7,
        border_radius=7,
        bgcolor="#24252A",
        on_click=on_click,
    )
