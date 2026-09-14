import flet as ft


def build_toolbar(
    period_title: ft.Text,
    mode_row: ft.Row,
    on_previous,
    on_today,
    on_next,
    on_search,
    on_add,
    settings_button,
):
    return ft.Container(
        ft.Row(
            [
                ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=on_previous),
                ft.Button("Hom nay", on_click=on_today),
                ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=on_next),
                period_title,
                ft.Container(expand=True),
                mode_row,
                ft.TextField(
                    hint_text="Tim mon hoc",
                    prefix_icon=ft.Icons.SEARCH,
                    width=170,
                    height=40,
                    on_change=on_search,
                ),
               ft.Button(
                    "Them chi tiet",
                    icon=ft.Icons.ADD,
                    bgcolor=ft.Colors.PRIMARY,
                    color=ft.Colors.ON_PRIMARY,
                    on_click=on_add,
                ),
                settings_button,
            ],
            spacing=7,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=10,
        bgcolor="#FFFFFF",
        border=ft.Border(bottom=ft.BorderSide(1, "#E4E5E7")),
    )
