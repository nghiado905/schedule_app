import flet as ft


def build_mode_button(label: str, active: bool, on_click):
    return ft.Container(
            content=ft.Text(
            label,
            color=(
                ft.Colors.ON_PRIMARY
                if active
                else ft.Colors.ON_SURFACE_VARIANT
            ),
            weight=ft.FontWeight.BOLD if active else None,
        ),
       bgcolor=(
            ft.Colors.PRIMARY
            if active
            else ft.Colors.SURFACE_CONTAINER
        ),
        padding=ft.Padding.symmetric(
            horizontal=12,
            vertical=7,
        ),
        border_radius=8,
        on_click=on_click,
    )
