import flet as ft

from models.lesson import Lesson


def build_agenda_item(lesson: Lesson, on_click, theme):
    return ft.Container(
        ft.Column(
            [
                ft.Text(lesson.start_at.strftime("%d/%m  %H:%M"), color=lesson.color, size=10),
                ft.Text(
                    lesson.title,
                    color=theme["sidebar_text"],
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
        bgcolor=theme["sidebar_card"],
        on_click=on_click,
    )
