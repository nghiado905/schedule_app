import flet as ft

from constants import THEME


class SettingsDialog:
    def __init__(self, page: ft.Page, on_dark_mode_changed):
        self.page = page
        self.on_dark_mode_changed = on_dark_mode_changed

    def open(self):

        def toggle_dark_mode(e):
            self.on_dark_mode_changed(bool(e.control.value))

        is_dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        theme_switch = ft.Switch(label="Dark mode", value=is_dark_mode, on_change=toggle_dark_mode)
        notification_switch = ft.Switch(label="Bat thong bao", value=True)
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Settings"),
            content=ft.Container(
                ft.Column(
                    [
                        theme_switch,
                        notification_switch,
                        ft.Text("Phan nay dang la UI settings, chua luu database.", size=12, color=THEME["text_subtle"]),
                    ],
                    tight=True,
                    spacing=12,
                ),
                width=360,
            ),
            actions=[
                ft.TextButton("Huy", on_click=lambda _: self.page.pop_dialog()),
                ft.Button("Luu", on_click=lambda _: self.page.pop_dialog()),
            ],
        )
        self.page.show_dialog(dialog)
