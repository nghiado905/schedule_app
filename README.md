# Thời Khóa Biểu Mobile

> Ứng dụng thời khóa biểu Android viết bằng Python và Flet, lưu dữ liệu cục bộ bằng SQLite.

Ứng dụng được thiết kế để chạy trên Windows 10/11 và đóng gói thành APK Android. Dữ liệu bài học nằm trên thiết bị; dữ liệu vẫn còn sau khi đóng ứng dụng và chỉ mất khi xóa dữ liệu ứng dụng hoặc gỡ cài đặt.

## Tính năng

- Lịch ngày, tuần, tháng và năm.
- Tạo bài học bằng cách chạm vào ô thời gian trống.
- Chọn khoảng thời gian dài bằng thao tác nhấn giữ/kéo.
- Chỉnh sửa, xóa bài học và chọn màu bài học.
- Lưu trữ offline bằng SQLite.
- Chế độ sáng mặc định và dark mode trong phần Cài đặt.
- Giao diện được tổ chức theo feature-based UI và layered architecture.

## Công nghệ và phiên bản

| Thành phần | Phiên bản dùng cho dự án | Ghi chú |
|---|---:|---|
| Windows | 10 hoặc 11, 64-bit | Hệ điều hành phát triển |
| Python | `>= 3.10` | Khuyến nghị Python 3.12 64-bit |
| Flet | bản mới nhất trong môi trường ảo | UI và đóng gói Android |
| Java JDK | `17` | Bắt buộc để build Android |
| Android SDK Platform | `android-35` | Android API target của dự án |
| Android Build Tools | `35.0.0` | Công cụ build hiện tại |
| Android Platform Tools | bản mới nhất | Có `adb` để kiểm tra thiết bị |
| Android min SDK | `24` | Android 7.0 trở lên |
| Android ABI | `arm64-v8a` | Thiết bị Android 64-bit |

> Cấu hình build nằm trong [`pyproject.toml`](pyproject.toml). Flet yêu cầu Python 3.10 trở lên và Android build yêu cầu JDK 17 cùng Android SDK.

## Link cài đặt chính thức

- [Python cho Windows](https://www.python.org/downloads/windows/) - chọn Windows installer 64-bit.
- [Eclipse Temurin JDK 17](https://adoptium.net/temurin/releases/?version=17) - chọn JDK, Windows, x64, MSI.
- [Android Studio](https://developer.android.com/studio) - cách dễ nhất để cài Android SDK.
- [Android Command-line Tools](https://developer.android.com/studio#command-tools) - lựa chọn nhẹ nếu không muốn cài Android Studio.
- [Flet Installation](https://flet.dev/docs/getting-started/installation/) - tài liệu cài Flet.
- [Flet Android Build](https://flet.dev/docs/publish/android/) - tài liệu đóng gói APK/AAB.

## Cấu trúc dự án

```text
schedule_app/
├── main.py                    # Điểm khởi chạy ứng dụng
├── app.py                     # App shell, state và điều hướng
├── constants.py               # Theme và hằng số giao diện
├── pyproject.toml             # Cấu hình Python/Flet/Android
├── requirements.txt           # Phụ thuộc Python
├── models/                    # Data models
├── repositories/              # Lưu trữ SQLite
├── components/                # Thành phần UI dùng lại
├── features/                  # Calendar, lessons, settings
└── utils/                     # Hàm tiện ích
```

## Cài đặt trên Windows

### 1. Mở PowerShell tại thư mục dự án

```powershell
cd D:\be_dev\schedule_app
```

### 2. Kiểm tra Python

```powershell
py --version
py -m pip --version
```

Nếu `py` chưa tồn tại, cài Python từ link chính thức ở trên và nhớ bật tùy chọn **Add python.exe to PATH**.

### 3. Tạo môi trường ảo và cài thư viện

```powershell
cd D:\be_dev\schedule_app

py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu máy chỉ có Python 3.10 hoặc 3.11, thay `py -3.12` bằng phiên bản đang có.

### 4. Kiểm tra Flet

```powershell
.\.venv\Scripts\flet.exe --version
.\.venv\Scripts\flet.exe doctor
```

## Chạy ứng dụng ở chế độ phát triển

Chạy trên máy tính:

```powershell
cd D:\be_dev\schedule_app
.\.venv\Scripts\flet.exe run main.py
```

Chạy thử trên điện thoại Android qua Flet app:

```powershell
.\.venv\Scripts\flet.exe run --android main.py
```

Điện thoại và máy tính cần kết nối cùng một mạng Wi-Fi. Cách này phù hợp để xem nhanh giao diện trước khi build APK.

## Cấu hình Java và Android SDK

### Cách 1: Máy đã cài Android Studio

Flet thường tự tìm SDK ở:

```text
C:\Users\<TênWindows>\AppData\Local\Android\Sdk
```

Trong Android Studio, mở **SDK Manager** và cài:

- Android SDK Platform 35.
- Android SDK Build-Tools 35.0.0.
- Android SDK Platform-Tools.
- Android SDK Command-line Tools.

### Cách 2: Dùng SDK hiện có của máy này

SDK hiện tại của dự án:

```text
C:\Users\MINHNGHIA\AppData\Local\Android\Sdk
```

JDK hiện tại:

```text
C:\Program Files\Java\jdk-17
```

Thiết lập biến môi trường cho **cửa sổ PowerShell hiện tại**:

```powershell
$env:PYTHONUTF8="1"
$env:JAVA_HOME="C:\Program Files\Java\jdk-17"
$env:ANDROID_HOME="C:\Users\MINHNGHIA\AppData\Local\Android\Sdk"
$env:ANDROID_SDK_ROOT=$env:ANDROID_HOME
$env:Path="$env:JAVA_HOME\bin;$env:ANDROID_HOME\platform-tools;$env:ANDROID_HOME\cmdline-tools\latest\bin;$env:Path"
```

Kiểm tra:

```powershell
java -version
adb version
Get-ChildItem "$env:ANDROID_HOME\platforms"
Get-ChildItem "$env:ANDROID_HOME\build-tools"
```

Kết quả cần có ít nhất:

```text
platforms\android-35
build-tools\35.0.0
platform-tools\adb.exe
```

Để lưu biến môi trường vĩnh viễn cho các cửa sổ PowerShell sau này:

```powershell
[Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk-17", "User")
[Environment]::SetEnvironmentVariable("ANDROID_HOME", "C:\Users\MINHNGHIA\AppData\Local\Android\Sdk", "User")
[Environment]::SetEnvironmentVariable("ANDROID_SDK_ROOT", "C:\Users\MINHNGHIA\AppData\Local\Android\Sdk", "User")
```

Sau khi dùng lệnh trên, đóng và mở lại PowerShell để nhận biến môi trường mới.

## Build APK

Từ thư mục dự án, chạy:

```powershell
cd D:\be_dev\schedule_app

$env:PYTHONUTF8="1"
$env:JAVA_HOME="C:\Program Files\Java\jdk-17"
$env:ANDROID_HOME="C:\Users\MINHNGHIA\AppData\Local\Android\Sdk"
$env:ANDROID_SDK_ROOT=$env:ANDROID_HOME
$env:Path="$env:JAVA_HOME\bin;$env:ANDROID_HOME\platform-tools;$env:ANDROID_HOME\cmdline-tools\latest\bin;$env:Path"

.\.venv\Scripts\flet.exe build apk --split-per-abi -v
```

APK sau khi build thành công nằm trong:

```text
D:\be_dev\schedule_app\build\apk\
```

Vì project chỉ cấu hình `arm64-v8a`, file APK phù hợp thường có tên tương tự:

```text
thoi-khoa-bieu-arm64-v8a.apk
```

Cài trực tiếp lên điện thoại đã bật USB debugging:

```powershell
adb install -r .\build\apk\thoi-khoa-bieu-arm64-v8a.apk
```

Build file AAB để đưa lên Google Play:

```powershell
.\.venv\Scripts\flet.exe build aab -v
```

## Lỗi Android SDK thường gặp

### `Package platforms not found` hoặc `Package build-tools not found`

Một số bản Android CLI mới cảnh báo `sdkmanager` đã deprecated và không còn xử lý cú pháp package cũ giống trước. Nếu SDK đã có đủ thư mục `android-35` và `35.0.0`, hãy bỏ qua bước cài lại package và chạy build trực tiếp bằng lệnh ở trên.

Nếu vẫn lỗi, kiểm tra đúng biến môi trường:

```powershell
$env:ANDROID_HOME
Test-Path "$env:ANDROID_HOME\platforms\android-35"
Test-Path "$env:ANDROID_HOME\build-tools\35.0.0"
```

### `JAVA_HOME is invalid`

`JAVA_HOME` phải trỏ tới thư mục chứa `bin\java.exe`, không trỏ thẳng vào file `.exe`:

```powershell
Test-Path "$env:JAVA_HOME\bin\java.exe"
```

### Không thấy điện thoại

```powershell
adb devices
```

Nếu danh sách trống, bật **Developer options** và **USB debugging** trên điện thoại, sau đó chấp nhận hộp thoại cấp quyền USB.

## Git

```powershell
cd D:\be_dev\schedule_app
git init
git add .
git commit -m "Initial Android timetable app"
```

Thêm repository từ xa:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/thoi-khoa-bieu-mobile.git
git branch -M main
git push -u origin main
```

## Quy ước phát triển

Khi thêm tính năng mới, giữ `app.py` ở vai trò điều phối. Nên tạo theo cấu trúc:

```text
components/your_button.py
features/your_feature/your_feature.py
features/your_feature/your_dialog.py
```

Sau khi sửa code, kiểm tra cú pháp:

```powershell
.\.venv\Scripts\python.exe -m compileall app.py components features constants.py
```

## Tài liệu tham khảo

- [Flet Documentation](https://flet.dev/docs/)
- [Flet Installation](https://flet.dev/docs/getting-started/installation/)
- [Flet Android Packaging](https://flet.dev/docs/publish/android/)
- [Android Studio và SDK](https://developer.android.com/studio)
- [Python Documentation](https://docs.python.org/3/)

