"""
EVN Water Level Scraper cho Hồ Bản Vẽ
Lấy dữ liệu mực nước từ website EVN cho khoảng thời gian chỉ định
"""

import time
import pandas as pd
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import logging

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EVNWaterLevelScraper:
    """Scraper cho dữ liệu mực nước EVN"""
    
    def __init__(self, headless=False):
        """
        Khởi tạo scraper
        
        Args:
            headless (bool): Chạy browser ở chế độ ẩn
        """
        # URL cơ sở của iframe chứa dữ liệu
        self.base_url = "https://hochuathuydien.evn.com.vn/PageHoChuaThuyDienEmbedEVN.aspx"
        self.driver = None
        self.headless = headless
        
    def setup_driver(self):
        """Thiết lập Chrome WebDriver với các tùy chọn phù hợp"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Khởi tạo driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        logger.info("WebDriver đã được khởi tạo thành công")
        
    def close_driver(self):
        """Đóng WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver đã đóng")
    
    def build_url(self, date_str, reservoir_id="26"):
        """
        Xây dựng URL với các tham số
        
        Args:
            date_str (str): Ngày giờ theo định dạng 'DD/MM/YYYY HH:MM'
            reservoir_id (str): ID hồ chứa (26 cho Bản Vẽ)
            
        Returns:
            str: URL hoàn chỉnh
        """
        url = f"{self.base_url}?td={date_str}&hc={reservoir_id}"
        return url
    
    def extract_table_data(self, reservoir_name="Bản Vẽ"):
        """
        Trích xuất dữ liệu từ bảng cho một hồ chứa cụ thể
        
        Args:
            reservoir_name (str): Tên hồ chứa cần trích xuất
            
        Returns:
            dict: Dữ liệu đã trích xuất hoặc None
        """
        try:
            # Đợi bảng tải xong
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tblgridtd"))
            )
            
            # Tìm tất cả các hàng
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            # Tìm hàng chứa "Bản Vẽ"
            for row in rows:
                text = row.text
                if reservoir_name in text:
                    # Trích xuất dữ liệu từ hàng này
                    cols = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cols) >= 11:
                        # Trích xuất text từ mỗi cột
                        data = {
                            'Tên hồ': cols[0].text.split('\n')[0],  # Chỉ lấy tên, không lấy timestamp
                            'Thời điểm': cols[1].text,
                            'Htl (m)': cols[2].text,
                            'Hdbt (m)': cols[3].text,
                            'Hc (m)': cols[4].text,
                            'Qve (m3/s)': cols[5].text,
                            'ΣQx (m3/s)': cols[6].text,
                            'Qxt (m3/s)': cols[7].text,
                            'Qxm (m3/s)': cols[8].text,
                            'Ncxs': cols[9].text,
                            'Ncxm': cols[10].text
                        }
                        
                        logger.info(f"Đã trích xuất dữ liệu cho {reservoir_name}: {data['Thời điểm']}")
                        return data
            
            logger.warning(f"Không tìm thấy dữ liệu cho {reservoir_name}")
            return None
            
        except Exception as e:
            logger.error(f"Lỗi khi trích xuất dữ liệu bảng: {e}")
            return None
    
    def scrape_single_time(self, date_time, reservoir_name="Bản Vẽ"):
        """
        Lấy dữ liệu cho một thời điểm cụ thể
        
        Args:
            date_time (datetime): Thời điểm cần lấy dữ liệu
            reservoir_name (str): Tên hồ chứa
            
        Returns:
            dict: Dữ liệu đã lấy hoặc None
        """
        try:
            # Định dạng ngày cho URL
            date_str = date_time.strftime("%d/%m/%Y %H:%M")
            
            # Xây dựng URL
            url = self.build_url(date_str)
            
            logger.info(f"Đang truy cập: {url}")
            self.driver.get(url)
            
            # Đợi trang tải xong
            time.sleep(3)
            
            # Trích xuất dữ liệu
            data = self.extract_table_data(reservoir_name)
            
            if data:
                # Thêm thời điểm yêu cầu
                data['Thời điểm yêu cầu'] = date_str
                
            return data
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy dữ liệu {date_time}: {e}")
            return None
    
    def scrape_date_range(self, start_date, end_date, reservoir_name="Bản Vẽ"):
        """
        Lấy dữ liệu cho một khoảng thời gian (dữ liệu theo giờ từ 00:00 đến 23:00 mỗi ngày)
        
        Args:
            start_date (datetime): Ngày bắt đầu
            end_date (datetime): Ngày kết thúc
            reservoir_name (str): Tên hồ chứa
            
        Returns:
            pd.DataFrame: Dữ liệu kết hợp cho toàn bộ khoảng thời gian
        """
        all_data = []
        
        # Thiết lập driver
        self.setup_driver()
        
        try:
            current_date = start_date
            
            while current_date <= end_date:
                # Lấy dữ liệu cho thời điểm này
                data = self.scrape_single_time(current_date, reservoir_name)
                
                if data:
                    all_data.append(data)
                
                # Chuyển sang giờ tiếp theo
                current_date += timedelta(hours=1)
                
                # Thêm delay nhỏ để tránh quá tải server
                time.sleep(1)
            
            # Tạo DataFrame
            if all_data:
                df = pd.DataFrame(all_data)
                logger.info(f"Tổng số bản ghi đã thu thập: {len(df)}")
                return df
            else:
                logger.warning("Không thu thập được dữ liệu")
                return None
                
        finally:
            self.close_driver()


def main():
    """Hàm thực thi chính"""
    
    # Cấu hình
    RESERVOIR_NAME = "Bản Vẽ"
    START_DATE = datetime(2025, 7, 15, 0, 0)    # 15/07/2025 00:00
    END_DATE = datetime(2025, 7, 31, 23, 0)     # 31/07/2025 23:00
    OUTPUT_FILE = "ban_ve_water_level.csv"
    OUTPUT_EXCEL = "ban_ve_water_level.xlsx"
    
    # Tạo instance scraper
    scraper = EVNWaterLevelScraper(headless=False)  # Đổi thành True để chạy ẩn
    
    try:
        # Lấy dữ liệu
        logger.info(f"Bắt đầu thu thập dữ liệu cho {RESERVOIR_NAME}")
        logger.info(f"Khoảng thời gian: {START_DATE} đến {END_DATE}")
        logger.info(f"Sẽ thu thập dữ liệu theo giờ (00:00 đến 23:00) cho mỗi ngày")
        
        df = scraper.scrape_date_range(START_DATE, END_DATE, RESERVOIR_NAME)
        
        if df is not None and not df.empty:
            # Lưu vào CSV
            df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
            logger.info(f"Dữ liệu đã được lưu vào {OUTPUT_FILE}")
            
            # Lưu vào Excel
            df.to_excel(OUTPUT_EXCEL, index=False, engine='openpyxl')
            logger.info(f"Dữ liệu đã được lưu vào {OUTPUT_EXCEL}")
            
            # Hiển thị tóm tắt
            print("\n" + "="*70)
            print("TÓM TẮT THU THẬP DỮ LIỆU")
            print("="*70)
            print(f"Hồ chứa: {RESERVOIR_NAME}")
            print(f"Khoảng thời gian: {START_DATE.strftime('%d/%m/%Y %H:%M')} đến {END_DATE.strftime('%d/%m/%Y %H:%M')}")
            print(f"Tổng số bản ghi: {len(df)}")
            print(f"File kết quả:")
            print(f"  - CSV: {OUTPUT_FILE}")
            print(f"  - Excel: {OUTPUT_EXCEL}")
            print("\n5 bản ghi đầu tiên:")
            print(df.head())
            print("\n5 bản ghi cuối cùng:")
            print(df.tail())
            print("\nCác cột dữ liệu:")
            for col in df.columns:
                print(f"  - {col}")
        else:
            logger.error("Không thu thập được dữ liệu")
            
    except Exception as e:
        logger.error(f"Lỗi trong quá trình thực thi: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
