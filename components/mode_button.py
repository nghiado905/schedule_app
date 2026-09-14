import flet as ft


def build_mode_button(label: str, active: bool, on_click, theme):
    return ft.Container(
            content=ft.Text(
            label,
            color="#FFFFFF" if active else theme["text_muted"],
            weight=ft.FontWeight.BOLD if active else None,
        ),
       bgcolor=theme["accent"] if active else theme["surface_high"],
        padding=ft.Padding.symmetric(
            horizontal=12,
            vertical=7,
        ),
        border_radius=8,
        on_click=on_click,
    )
