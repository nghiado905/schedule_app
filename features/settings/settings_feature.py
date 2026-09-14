import flet as ft

from .settings_dialog import SettingsDialog


class SettingsFeature:
    def __init__(self, page: ft.Page, on_dark_mode_changed):
        self.page = page
        self.dialog = SettingsDialog(page, on_dark_mode_changed)

    def button(self, theme):
        return ft.IconButton(
            icon=ft.Icons.SETTINGS_OUTLINED,
            icon_color=theme["text_muted"],
            tooltip="Settings",
            on_click=lambda _: self.dialog.open(),
        )
    
