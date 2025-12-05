"""
Quick test to inspect the iframe page structure
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


def quick_inspect():
    """Quick inspection of the iframe page"""
    
    url = "https://hochuathuydien.evn.com.vn/PageHoChuaThuyDienEmbedEVN.aspx"
    
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"Navigating to {url}")
        driver.get(url)
        
        time.sleep(5)
        
        print("\n" + "="*80)
        print("IFRAME PAGE INSPECTION")
        print("="*80)
        
        # Check for select elements
        print("\n1. SELECT ELEMENTS (Reservoir dropdown):")
        print("-" * 80)
        selects = driver.find_elements(By.TAG_NAME, "select")
        for i, select in enumerate(selects):
            print(f"\nSelect {i}:")
            print(f"  ID: {select.get_attribute('id')}")
            print(f"  Name: {select.get_attribute('name')}")
            
            options = select.find_elements(By.TAG_NAME, "option")
            print(f"  Number of options: {len(options)}")
            print("  First 15 options:")
            for opt in options[:15]:
                print(f"    - {opt.text}")
        
        # Check for input elements
        print("\n2. INPUT ELEMENTS (Date pickers):")
        print("-" * 80)
        inputs = driver.find_elements(By.TAG_NAME, "input")
        for i, inp in enumerate(inputs):
            inp_id = inp.get_attribute('id')
            inp_name = inp.get_attribute('name')
            inp_type = inp.get_attribute('type')
            inp_class = inp.get_attribute('class')
            
            if inp_id or inp_name:
                print(f"\nInput {i}:")
                print(f"  ID: {inp_id}")
                print(f"  Name: {inp_name}")
                print(f"  Type: {inp_type}")
                print(f"  Class: {inp_class}")
        
        # Check for buttons
        print("\n3. BUTTONS:")
        print("-" * 80)
        buttons = driver.find_elements(By.TAG_NAME, "button")
        inputs_submit = driver.find_elements(By.CSS_SELECTOR, "input[type='submit'], input[type='button']")
        
        all_buttons = buttons + inputs_submit
        for i, btn in enumerate(all_buttons):
            print(f"\nButton {i}:")
            print(f"  ID: {btn.get_attribute('id')}")
            print(f"  Name: {btn.get_attribute('name')}")
            print(f"  Value: {btn.get_attribute('value')}")
            print(f"  Text: {btn.text}")
        
        # Check for tables
        print("\n4. TABLES:")
        print("-" * 80)
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"Found {len(tables)} table(s)")
        
        for i, table in enumerate(tables):
            print(f"\nTable {i}:")
            print(f"  ID: {table.get_attribute('id')}")
            print(f"  Class: {table.get_attribute('class')}")
            
            headers = table.find_elements(By.TAG_NAME, "th")
            if headers:
                print(f"  Headers: {[h.text for h in headers]}")
            
            rows = table.find_elements(By.TAG_NAME, "tr")
            print(f"  Total rows: {len(rows)}")
            
            if len(rows) > 1:
                print("  First 3 data rows:")
                for row_idx in range(1, min(4, len(rows))):
                    cols = rows[row_idx].find_elements(By.TAG_NAME, "td")
                    print(f"    Row {row_idx}: {[col.text[:30] for col in cols]}")
        
        # Save page source
        with open("iframe_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\n5. Page source saved to: iframe_page_source.html")
        
        # Save screenshot
        driver.save_screenshot("iframe_page_screenshot.png")
        print("6. Screenshot saved to: iframe_page_screenshot.png")
        
        print("\n" + "="*80)
        print("Keep browser open for manual inspection...")
        input("\nPress Enter to close...")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()


if __name__ == "__main__":
    quick_inspect()
