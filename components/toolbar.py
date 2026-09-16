import flet as ft

def build_toolbar(
    period_title: ft.Text,
    mode_row: ft.Row,
    on_previous,
    on_today,
    on_next,
    on_search,
    on_add,
    on_fixed,
    screenshot_button,
    settings_button,
    theme,
    compact: bool = False,
):
    search = ft.TextField(
        hint_text="Tim mon hoc",
        prefix_icon=ft.Icons.SEARCH,
        width=116 if compact else 170,
        height=40,
        color=theme["text"],
        border_color=theme["border"],
        focused_border_color=theme["accent"],
        bgcolor=theme["surface"],
        on_change=on_search,
    )
    add_button = ft.Button(
        "Them" if compact else "Them chi tiet",
        icon=ft.Icons.ADD,
        bgcolor=theme["accent"],
        color="#FFFFFF",
        on_click=on_add,
    )
    fixed_button = ft.IconButton(
        icon=ft.Icons.PUSH_PIN_OUTLINED,
        icon_color=theme["text"],
        tooltip="Lich co dinh",
        on_click=on_fixed,
    ) if compact else ft.Button(
        "Lich co dinh",
        icon=ft.Icons.PUSH_PIN_OUTLINED,
        bgcolor=theme["surface_high"],
        color=theme["text"],
        on_click=on_fixed,
    )

    if compact:
        content = ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(ft.Icons.CHEVRON_LEFT, icon_color=theme["text"], on_click=on_previous),
                        ft.Button("Hom nay", color=theme["text"], bgcolor=theme["surface_high"], on_click=on_today),
                        ft.IconButton(ft.Icons.CHEVRON_RIGHT, icon_color=theme["text"], on_click=on_next),
                        period_title,
                        ft.Container(expand=True),
                        screenshot_button,
                        settings_button,
                    ],
                    spacing=4,
                ),
                ft.Row(
                    [mode_row, search, add_button, fixed_button],
                    spacing=6,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ],
            spacing=6,
        )
        return ft.Container(
            content,
            padding=8,
            bgcolor=theme["toolbar"],
            border=ft.Border(bottom=ft.BorderSide(1, theme["border"])),
        )

    return ft.Container(
        ft.Row(
            [
                ft.IconButton(ft.Icons.CHEVRON_LEFT, icon_color=theme["text"], on_click=on_previous),
                ft.Button("Hom nay", color=theme["text"], bgcolor=theme["surface_high"], on_click=on_today),
                ft.IconButton(ft.Icons.CHEVRON_RIGHT, icon_color=theme["text"], on_click=on_next),
                period_title,
                ft.Container(expand=True),
                mode_row,
                search,
                add_button,
                fixed_button,
                screenshot_button,
                settings_button,
            ],
            spacing=7,
            scroll=ft.ScrollMode.AUTO,
        ),
        padding=10,
        bgcolor=theme["toolbar"],
        border=ft.Border(bottom=ft.BorderSide(1, theme["border"])),
    )
