from datetime import datetime
from pathlib import Path

import flet as ft


class ScreenshotFeature:
    def __init__(self, page: ft.Page, output_dir: Path):
        self.page = page
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def button(self, theme):
        return ft.IconButton(
            icon=ft.Icons.CAMERA_ALT_OUTLINED,
            icon_color=theme["text"],
            tooltip="Chup man hinh",
            on_click=self.capture,
        )

    async def capture(self, _):
        try:
            image_bytes = await self.page.take_screenshot(pixel_ratio=2)
            path = self.output_dir / f"schedule-{datetime.now():%Y%m%d-%H%M%S}.png"
            path.write_bytes(image_bytes)
            self.show_message(f"Da luu anh: {path}")
        except Exception as exc:
            self.show_message(f"Khong chup duoc man hinh: {exc}")

    def show_message(self, message: str):
        snack_bar = ft.SnackBar(ft.Text(message), duration=4000)
        self.page.show_dialog(snack_bar)
