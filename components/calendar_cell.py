import flet as ft


def build_mini_calendar_day(number: int, active: bool, on_click, theme):
    return ft.Container(
        ft.Text(str(number), size=10, color="#FFFFFF" if active else theme["sidebar_muted"], text_align=ft.TextAlign.CENTER),
        width=25,
        height=25,
        alignment=ft.Alignment.CENTER,
        bgcolor=theme["accent"] if active else None,
        border_radius=13,
        on_click=on_click,
    )
