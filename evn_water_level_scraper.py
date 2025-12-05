"""
EVN Water Level Scraper for Sông Ba Hạ Reservoir - FINAL VERSION
Scrapes water level data from EVN website for a specified date range
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
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EVNWaterLevelScraper:
    """Scraper for EVN water level data"""
    
    def __init__(self, headless=False):
        """
        Initialize the scraper
        
        Args:
            headless (bool): Run browser in headless mode
        """
        # The actual data is in an iframe at this URL
        self.base_url = "https://hochuathuydien.evn.com.vn/PageHoChuaThuyDienEmbedEVN.aspx"
        self.driver = None
        self.headless = headless
        
    def setup_driver(self):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Initialize driver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        logger.info("WebDriver initialized successfully")
        
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")
    
    def build_url(self, date_str, reservoir_id="27"):
        """
        Build URL with parameters
        
        Args:
            date_str (str): Date in format 'DD/MM/YYYY HH:MM'
            reservoir_id (str): Reservoir ID (27 for Sông Ba Hạ)
            
        Returns:
            str: Complete URL
        """
        # URL format: /PageHoChuaThuyDienEmbedEVN.aspx?td={date}&hc={reservoir_id}
        url = f"{self.base_url}?td={date_str}&hc={reservoir_id}"
        return url
    
    def extract_table_data(self, reservoir_name="Sông Ba Hạ"):
        """
        Extract data from the table for a specific reservoir
        
        Args:
            reservoir_name (str): Name of the reservoir to extract
            
        Returns:
            dict: Extracted data or None
        """
        try:
            # Wait for table to load
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "tblgridtd"))
            )
            
            # Find all rows
            rows = table.find_elements(By.TAG_NAME, "tr")
            
            # Look for the row containing "Sông Ba Hạ"
            for row in rows:
                text = row.text
                if reservoir_name in text:
                    # Extract data from this row
                    cols = row.find_elements(By.TAG_NAME, "td")
                    
                    if len(cols) >= 11:
                        # Extract the text from each column
                        data = {
                            'Tên hồ': cols[0].text.split('\n')[0],  # Get just the name, not the timestamp
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
                        
                        logger.info(f"Extracted data for {reservoir_name}: {data['Thời điểm']}")
                        return data
            
            logger.warning(f"No data found for {reservoir_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting table data: {e}")
            return None
    
    def scrape_single_time(self, date_time, reservoir_name="Sông Ba Hạ"):
        """
        Scrape data for a single date/time
        
        Args:
            date_time (datetime): DateTime to scrape
            reservoir_name (str): Name of the reservoir
            
        Returns:
            dict: Scraped data or None
        """
        try:
            # Format date for URL
            date_str = date_time.strftime("%d/%m/%Y %H:%M")
            
            # Build URL
            url = self.build_url(date_str)
            
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(3)
            
            # Extract data
            data = self.extract_table_data(reservoir_name)
            
            if data:
                # Add the requested datetime
                data['Thời điểm yêu cầu'] = date_str
                
            return data
            
        except Exception as e:
            logger.error(f"Error scraping {date_time}: {e}")
            return None
    
    def scrape_date_range(self, start_date, end_date, reservoir_name="Sông Ba Hạ"):
        """
        Scrape data for a date range (hourly data from 00:00 to 23:00 each day)
        
        Args:
            start_date (datetime): Start date
            end_date (datetime): End date
            reservoir_name (str): Name of the reservoir
            
        Returns:
            pd.DataFrame: Combined data for the entire date range
        """
        all_data = []
        
        # Setup driver
        self.setup_driver()
        
        try:
            current_date = start_date
            
            while current_date <= end_date:
                # Scrape data for this time
                data = self.scrape_single_time(current_date, reservoir_name)
                
                if data:
                    all_data.append(data)
                
                # Move to next hour
                current_date += timedelta(hours=1)
                
                # Add small delay to avoid overwhelming the server
                time.sleep(1)
            
            # Create DataFrame
            if all_data:
                df = pd.DataFrame(all_data)
                logger.info(f"Total records collected: {len(df)}")
                return df
            else:
                logger.warning("No data collected")
                return None
                
        finally:
            self.close_driver()


def main():
    """Main execution function"""
    
    # Configuration
    RESERVOIR_NAME = "Sông Ba Hạ"
    START_DATE = datetime(2025, 11, 4, 0, 0)   # 04/11/2025 00:00
    END_DATE = datetime(2025, 11, 30, 23, 0)   # 30/11/2025 23:00
    OUTPUT_FILE = "song_ba_ha_water_level.csv"
    OUTPUT_EXCEL = "song_ba_ha_water_level.xlsx"
    
    # Create scraper instance
    scraper = EVNWaterLevelScraper(headless=False)  # Set to True for headless mode
    
    try:
        # Scrape data
        logger.info(f"Starting data collection for {RESERVOIR_NAME}")
        logger.info(f"Date range: {START_DATE} to {END_DATE}")
        logger.info(f"This will collect hourly data (00:00 to 23:00) for each day")
        
        df = scraper.scrape_date_range(START_DATE, END_DATE, RESERVOIR_NAME)
        
        if df is not None and not df.empty:
            # Save to CSV
            df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
            logger.info(f"Data saved to {OUTPUT_FILE}")
            
            # Save to Excel
            df.to_excel(OUTPUT_EXCEL, index=False, engine='openpyxl')
            logger.info(f"Data saved to {OUTPUT_EXCEL}")
            
            # Display summary
            print("\n" + "="*70)
            print("DATA COLLECTION SUMMARY")
            print("="*70)
            print(f"Reservoir: {RESERVOIR_NAME}")
            print(f"Date Range: {START_DATE.strftime('%d/%m/%Y %H:%M')} to {END_DATE.strftime('%d/%m/%Y %H:%M')}")
            print(f"Total Records: {len(df)}")
            print(f"Output Files:")
            print(f"  - CSV: {OUTPUT_FILE}")
            print(f"  - Excel: {OUTPUT_EXCEL}")
            print("\nFirst 5 records:")
            print(df.head())
            print("\nLast 5 records:")
            print(df.tail())
            print("\nData columns:")
            for col in df.columns:
                print(f"  - {col}")
        else:
            logger.error("No data was collected")
            
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
