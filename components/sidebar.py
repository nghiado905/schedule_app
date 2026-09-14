import flet as ft


def build_sidebar(side_month: ft.Text, mini_calendar: ft.GridView, agenda: ft.ListView):
    return ft.Container(
        ft.Column(
            [
                ft.Row([ft.Text("●  ●  ●", color="#FF655D", size=11), ft.Container(expand=True)]),
                side_month,
                mini_calendar,
                ft.Text("LICH SAP TOI", color="#989AA2", size=10, weight=ft.FontWeight.BOLD),
                agenda,
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CIRCLE, size=8, color="#18B978"),
                        ft.Text("Du lieu cuc bo", color="#C7C9CE", size=12),
                    ]
                ),
            ],
            spacing=8,
        ),
        width=255,
        bgcolor="#17181C",
        padding=14,
    )
