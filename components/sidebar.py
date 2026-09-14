import flet as ft

def build_sidebar(side_month: ft.Text, mini_calendar: ft.GridView, agenda: ft.ListView, theme):
    return ft.Container(
        ft.Column(
            [
                ft.Row([ft.Text("●  ●  ●", color="#FF655D", size=11), ft.Container(expand=True)]),
                side_month,
                mini_calendar,
                ft.Text("LICH SAP TOI", color=theme["sidebar_subtle"], size=10, weight=ft.FontWeight.BOLD),
                agenda,
                ft.Row(
                    [
                        ft.Icon(ft.Icons.CIRCLE, size=8, color=theme["success"]),
                        ft.Text("Du lieu cuc bo", color=theme["sidebar_muted"], size=12),
                    ]
                ),
            ],
            spacing=8,
        ),
        width=255,
        bgcolor=theme["sidebar"],
        padding=14,
    )
