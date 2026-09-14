import flet as ft


class SettingsDialog:
    def __init__(self, page: ft.Page):
        self.page = page

    def open(self):

        def toggle_dark_mode(e):
            self.page.theme_mode = ft.ThemeMode.DARK if e.control.value else ft.ThemeMode.LIGHT
            self.page.update()

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
                        ft.Text("Phan nay dang la UI settings, chua luu database.", size=12, color="#777A81"),
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
