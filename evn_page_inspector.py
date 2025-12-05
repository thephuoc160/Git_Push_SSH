"""
EVN Page Inspector - Helps identify the correct selectors for scraping
This script will open the EVN page and print out all the relevant elements
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import json


def inspect_evn_page():
    """Inspect the EVN page structure"""
    
    url = "https://www.evn.com.vn/c3/thong-tin-ho-thuy-dien/Muc-nuoc-cac-ho-thuy-dien-117-123.aspx"
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')
    
    # Initialize driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print(f"Navigating to {url}")
        driver.get(url)
        
        # Wait for page to load
        time.sleep(5)
        
        print("\n" + "="*80)
        print("PAGE INSPECTION REPORT")
        print("="*80)
        
        # Check for iframes
        print("\n1. CHECKING FOR IFRAMES:")
        print("-" * 80)
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframe(s)")
        
        for i, iframe in enumerate(iframes):
            print(f"\nIframe {i}:")
            print(f"  ID: {iframe.get_attribute('id')}")
            print(f"  Name: {iframe.get_attribute('name')}")
            print(f"  Src: {iframe.get_attribute('src')}")
            print(f"  Class: {iframe.get_attribute('class')}")
        
        # Function to inspect current context
        def inspect_context(context_name="Main Page"):
            print(f"\n2. INSPECTING {context_name.upper()}:")
            print("-" * 80)
            
            # Check for select/dropdown elements
            print("\nSelect/Dropdown elements:")
            selects = driver.find_elements(By.TAG_NAME, "select")
            for i, select in enumerate(selects):
                print(f"\n  Select {i}:")
                print(f"    ID: {select.get_attribute('id')}")
                print(f"    Name: {select.get_attribute('name')}")
                print(f"    Class: {select.get_attribute('class')}")
                
                # Get options
                options = select.find_elements(By.TAG_NAME, "option")
                print(f"    Options ({len(options)}):")
                for opt in options[:10]:  # Show first 10 options
                    print(f"      - {opt.text}")
            
            # Check for input elements (date pickers)
            print("\nInput elements:")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for i, inp in enumerate(inputs):
                inp_type = inp.get_attribute('type')
                if inp_type in ['text', 'date', 'datetime-local', 'datetime']:
                    print(f"\n  Input {i}:")
                    print(f"    ID: {inp.get_attribute('id')}")
                    print(f"    Name: {inp.get_attribute('name')}")
                    print(f"    Type: {inp_type}")
                    print(f"    Class: {inp.get_attribute('class')}")
                    print(f"    Placeholder: {inp.get_attribute('placeholder')}")
            
            # Check for buttons
            print("\nButton elements:")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for i, btn in enumerate(buttons):
                print(f"\n  Button {i}:")
                print(f"    ID: {btn.get_attribute('id')}")
                print(f"    Name: {btn.get_attribute('name')}")
                print(f"    Class: {btn.get_attribute('class')}")
                print(f"    Text: {btn.text}")
            
            # Check for tables
            print("\nTable elements:")
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"Found {len(tables)} table(s)")
            
            for i, table in enumerate(tables):
                print(f"\n  Table {i}:")
                print(f"    ID: {table.get_attribute('id')}")
                print(f"    Class: {table.get_attribute('class')}")
                
                # Get headers
                headers = table.find_elements(By.TAG_NAME, "th")
                if headers:
                    print(f"    Headers: {[h.text for h in headers]}")
                
                # Get first few rows
                rows = table.find_elements(By.TAG_NAME, "tr")
                print(f"    Total rows: {len(rows)}")
                
                if len(rows) > 1:
                    print("    First data row:")
                    first_data_row = rows[1] if len(rows) > 1 else rows[0]
                    cols = first_data_row.find_elements(By.TAG_NAME, "td")
                    print(f"      {[col.text for col in cols]}")
        
        # Inspect main page
        inspect_context("Main Page")
        
        # Try to switch to each iframe and inspect
        for i, iframe in enumerate(iframes):
            try:
                driver.switch_to.frame(iframe)
                inspect_context(f"Iframe {i}")
                driver.switch_to.default_content()
            except Exception as e:
                print(f"\nCould not inspect iframe {i}: {e}")
                driver.switch_to.default_content()
        
        # Save page source for manual inspection
        print("\n3. SAVING PAGE SOURCE:")
        print("-" * 80)
        with open("evn_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page source saved to: evn_page_source.html")
        
        # Save screenshot
        driver.save_screenshot("evn_page_screenshot.png")
        print("Screenshot saved to: evn_page_screenshot.png")
        
        # Execute JavaScript to get more info
        print("\n4. JAVASCRIPT INSPECTION:")
        print("-" * 80)
        
        # Check for common JavaScript frameworks/libraries
        js_checks = {
            "jQuery": "typeof jQuery !== 'undefined'",
            "Angular": "typeof angular !== 'undefined'",
            "React": "typeof React !== 'undefined'",
            "Vue": "typeof Vue !== 'undefined'",
        }
        
        for framework, check in js_checks.items():
            result = driver.execute_script(f"return {check}")
            print(f"{framework}: {'Found' if result else 'Not found'}")
        
        # Try to find data in JavaScript variables
        print("\nChecking for data in window object...")
        try:
            window_vars = driver.execute_script("return Object.keys(window).filter(k => k.toLowerCase().includes('data') || k.toLowerCase().includes('reservoir'))")
            if window_vars:
                print(f"Potential data variables: {window_vars}")
        except:
            pass
        
        print("\n" + "="*80)
        print("INSPECTION COMPLETE")
        print("="*80)
        print("\nPlease review the output above to identify:")
        print("1. The correct selector for the reservoir dropdown")
        print("2. The correct selectors for date inputs")
        print("3. The correct selector for the search/submit button")
        print("4. The correct selector for the data table")
        print("\nKeep the browser window open to manually inspect elements...")
        
        input("\nPress Enter to close the browser...")
        
    except Exception as e:
        print(f"Error during inspection: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()


if __name__ == "__main__":
    inspect_evn_page()
