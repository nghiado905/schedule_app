import flet as ft


def build_mini_calendar_day(number: int, active: bool, on_click):
    return ft.Container(
        ft.Text(str(number), size=10, color="#FFFFFF", text_align=ft.TextAlign.CENTER),
        width=25,
        height=25,
        alignment=ft.Alignment.CENTER,
        bgcolor="#3578F6" if active else None,
        border_radius=13,
        on_click=on_click,
    )
