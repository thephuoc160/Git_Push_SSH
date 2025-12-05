# EVN Water Level Scraper

Script Python để lấy dữ liệu mực nước hồ thủy điện từ website EVN.

## Yêu cầu

- Python 3.8 trở lên
- Chrome browser
- ChromeDriver (tương thích với phiên bản Chrome của bạn)

## Cài đặt

1. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

2. Tải ChromeDriver:
   - Truy cập: https://chromedriver.chromium.org/downloads
   - Tải phiên bản tương thích với Chrome của bạn
   - Đặt ChromeDriver vào PATH hoặc cùng thư mục với script

## Sử dụng

### Bước 1: Kiểm tra cấu trúc trang web

Chạy script inspector để xác định các selector cần thiết:

```bash
python evn_page_inspector.py
```

Script này sẽ:
- Mở trang web EVN
- Phân tích cấu trúc HTML
- Tìm các iframe, dropdown, input, button, và table
- Lưu page source và screenshot để kiểm tra
- In ra thông tin chi tiết về các element

### Bước 2: Cập nhật selector trong script chính

Sau khi chạy inspector, cập nhật các selector trong file `evn_water_level_scraper.py`:

```python
# Ví dụ các selector cần cập nhật:
select_element = self.driver.find_element(By.ID, "reservoir_select")  # ID của dropdown chọn hồ
start_date_input = self.driver.find_element(By.ID, "start_date_input")  # ID của input ngày bắt đầu
end_date_input = self.driver.find_element(By.ID, "end_date_input")  # ID của input ngày kết thúc
search_button = self.driver.find_element(By.ID, "search_button")  # ID của nút tìm kiếm
```

### Bước 3: Chạy scraper

Sau khi cập nhật các selector, chạy script chính:

```bash
python evn_water_level_scraper.py
```

## Cấu hình

Trong file `evn_water_level_scraper.py`, bạn có thể thay đổi các thông số:

```python
# Tên hồ thủy điện
RESERVOIR_NAME = "Sông Ba Hạ"

# Khoảng thời gian lấy dữ liệu
START_DATE = datetime(2025, 11, 4, 0, 0)   # 04/11/2025 00:00
END_DATE = datetime(2025, 11, 30, 23, 0)   # 30/11/2025 23:00

# File output
OUTPUT_FILE = "song_ba_ha_water_level.csv"

# Chế độ headless (chạy ngầm không hiện browser)
scraper = EVNWaterLevelScraper(headless=False)  # Đổi thành True để chạy ngầm
```

## Kết quả

Dữ liệu sẽ được lưu vào file CSV với các thông tin:
- Thời gian (từng giờ từ 00:00 đến 23:00 mỗi ngày)
- Mực nước hồ
- Các thông số khác (tùy thuộc vào cấu trúc bảng dữ liệu)

## Xử lý lỗi

Nếu gặp lỗi:

1. **ChromeDriver không tương thích**: Cập nhật ChromeDriver phù hợp với phiên bản Chrome
2. **Không tìm thấy element**: Chạy lại inspector và cập nhật selector
3. **Timeout**: Tăng thời gian chờ trong script
4. **Dữ liệu trong iframe**: Script đã xử lý iframe, nhưng có thể cần điều chỉnh

## Lưu ý

- Script sẽ lấy dữ liệu theo từng ngày để đảm bảo lấy đủ 24 giờ mỗi ngày
- Có delay giữa các request để tránh quá tải server
- Dữ liệu được lưu với encoding UTF-8-BOM để hiển thị đúng tiếng Việt trong Excel

## Cấu trúc file

```
.
├── evn_water_level_scraper.py   # Script chính để scrape dữ liệu
├── evn_page_inspector.py        # Script kiểm tra cấu trúc trang
├── requirements.txt             # Danh sách thư viện cần thiết
├── README.md                    # File hướng dẫn này
└── song_ba_ha_water_level.csv   # File kết quả (sau khi chạy)
```

## Hỗ trợ

Nếu cần hỗ trợ, vui lòng:
1. Chạy inspector script và kiểm tra output
2. Kiểm tra file log để xem lỗi chi tiết
3. Đảm bảo Chrome và ChromeDriver tương thích
