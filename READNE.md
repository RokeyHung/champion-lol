# 🧠 ARAM Random Discord Bot

Một bot Discord sử dụng Python để tạo hình ảnh đội hình ARAM ngẫu nhiên từ dữ liệu tướng Liên Minh Huyền Thoại, xuất ảnh từ HTML thông qua PDF và convert sang PNG bằng Poppler.

## 🔧 Cài đặt

### 1. Clone project

```bash
git clone https://github.com/your-user/my_discord_bot.git
cd my_discord_bot
```

### 2. Tạo môi trường ảo và cài thư viện

```bash
python -m venv venv
venv\Scripts\activate # or source venv/Scripts/activate

pip install -r requirements.txt
```

### 3. Cài đặt Poppler (cho pdf2image)

> ⚠️ Bắt buộc nếu dùng Windows!

- Tải Poppler cho Windows:  
  👉 https://github.com/oschwartz10612/poppler-windows/releases

- Giải nén ra thư mục ví dụ: `C:\poppler`

- Thêm vào biến môi trường `Path`:  
  `C:\poppler\Library\bin`

- Kiểm tra:

```bash
where pdfinfo
```

---

### 4. Cài GTK Runtime (cho WeasyPrint)

> ⚠️ Chỉ cần nếu bạn gặp lỗi liên quan đến `gobject` khi dùng WeasyPrint.

- Tải tại:  
  👉 https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

- Cài đặt và thêm vào `Path`:  
  `C:\Program Files\GTK3-Runtime Win64\bin`

---

## ▶️ Chạy bot

```bash
python main.py
```

Khi gõ trong Discord:

```txt
!aram-random
```

Bot sẽ:

- Lấy dữ liệu tướng từ Riot
- Chia thành 2 đội ngẫu nhiên
- Render HTML → PDF → PNG
- Gửi ảnh vào kênh Discord
