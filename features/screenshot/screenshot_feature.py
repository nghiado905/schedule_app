from datetime import datetime
from pathlib import Path

import flet as ft


class ScreenshotFeature:
    def __init__(self, page: ft.Page, output_dir: Path):
        self.page = page
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.last_image_bytes: bytes | None = None
        self.last_file_name = "schedule.png"
        self.file_picker = ft.FilePicker()
        self.page.services.append(self.file_picker)

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
            self.last_image_bytes = image_bytes
            self.last_file_name = f"schedule-{datetime.now():%Y%m%d-%H%M%S}.png"
            self.show_preview()
        except Exception as exc:
            self.show_message(f"Khong chup duoc man hinh: {exc}")

    def show_preview(self):
        if not self.last_image_bytes:
            return
        image = ft.Image(
            src=self.last_image_bytes,
            fit=ft.BoxFit.CONTAIN,
            width=min((self.page.width or 420) - 48, 900),
            height=min((self.page.height or 720) - 190, 560),
        )
        self.page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Xem anh vua chup"),
                content=ft.Container(image, bgcolor="#111827", padding=8, border_radius=8),
                actions=[
                    ft.TextButton("Huy", on_click=lambda _: self.page.pop_dialog()),
                    ft.TextButton("Chup lai", icon=ft.Icons.CAMERA_ALT_OUTLINED, on_click=self.retake),
                    ft.Button("Luu anh", icon=ft.Icons.DOWNLOAD_OUTLINED, on_click=self.save_image),
                ],
            )
        )

    async def retake(self, _):
        self.page.pop_dialog()
        await self.capture(None)

    async def save_image(self, _):
        if self.last_image_bytes is None:
            return
        saved_path = self.output_dir / self.last_file_name
        saved_path.write_bytes(self.last_image_bytes)
        try:
            path = await self.file_picker.save_file(
                dialog_title="Tai anh lich",
                file_name=self.last_file_name,
                file_type=ft.FilePickerFileType.IMAGE,
                allowed_extensions=["png"],
                src_bytes=self.last_image_bytes,
            )
            self.page.pop_dialog()
            if path:
                self.show_message(f"Da luu anh: {path}")
            else:
                self.show_message(f"Da luu trong app: {saved_path}")
        except Exception as exc:
            self.page.pop_dialog()
            self.show_message(f"Da luu trong app: {saved_path}. Khong tai duoc anh: {exc}")

    def show_message(self, message: str):
        snack_bar = ft.SnackBar(ft.Text(message), duration=4000)
        self.page.show_dialog(snack_bar)
