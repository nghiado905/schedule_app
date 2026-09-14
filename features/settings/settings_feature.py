import flet as ft

from .settings_dialog import SettingsDialog


class SettingsFeature:
    def __init__(self, page: ft.Page):
        self.dialog = SettingsDialog(page)

    def button(self):
        return ft.IconButton(
            icon=ft.Icons.SETTINGS_OUTLINED,
            icon_color="#555A62",
            tooltip="Settings",
            on_click=lambda _: self.dialog.open(),
        )
    