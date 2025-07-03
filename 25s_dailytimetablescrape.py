from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import os
import time
import csv
import json
import re

# Input and output directories
# input_directory = "C:/Users/siyi.ma/OneDrive - Tallinna Tehnikaülikool/M_õppetöö/TunniplaaniAI"
input_directory = "C:/Users/siyi.ma/Downlaods/25sCourselinks" 
output_directory = "C:/Users/siyi.ma/Downloads/25sdailytimetables_new"
os.makedirs(output_directory, exist_ok=True)

# Read static_tabs from the txt file with status message
# tabs_file = os.path.join(input_directory, "failed_timetable_groups.txt")
tabs_file = r"C:\Users\siyi.ma\Downloads\25sCourselinks\failed_timetable_groups.txt"
# tabs_file = r"C:\Users\siyi.ma\OneDrive - Tallinna Tehnikaülikool\M_õppetöö\TunniplaaniAI\25s\taltech_tpg25s.txt"
try:
    with open(tabs_file, "r", encoding="utf-8") as f:
        static_tabs = [line.strip() for line in f if line.strip()]
    print(f"Successfully found input directory and opened text file: {tabs_file}")
except Exception as e:
    print(f"Error: Unable to locate or open the text file at {tabs_file}. Exception: {e}")
    exit(1)

try:
    # Set up Edge options
    edge_options = Options()
    edge_options.add_argument('--ignore-certificate-errors')
    edge_options.add_argument('--ignore-ssl-errors')
    edge_options.add_argument('--log-level=3')

    # Initialize the WebDriver with options
    service = Service("C:/edgedriver_win64/msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=edge_options)

    # Open the webpage
    print("Opening webpage...")
    driver.get("https://tunniplaan.taltech.ee/#/public")

    # Wait for the page to load
    wait = WebDriverWait(driver, 20)

    # After loading the page and before the for loop
    all_tabs = driver.find_elements(By.PARTIAL_LINK_TEXT, "")
    print("Available tabs on the page:")
    for t in all_tabs:
        print(t.text)

    # 20250703 not necessary to Click the "Teaduskonnad" main tab automatically 
    # The warning appears because the tab is already active or another element is overlaying it, causing Selenium to fail the click.
    # try:
    #     teaduskonnad_tab = wait.until(
    #         EC.element_to_be_clickable((By.XPATH, '/html/body/app-main/div[2]/div/app-tt-public/div[2]/app-tt-public-tabs/div/tabset/ul/li[1]/a/span'))
    #     )
    #     driver.execute_script("arguments[0].scrollIntoView();", teaduskonnad_tab)
    #     time.sleep(0.5)
    #     teaduskonnad_tab.click()
    #     print("Main tab 'Teaduskonnad' clicked automatically.")
    #     time.sleep(2)
    # except Exception as e:
    #     print(f"Warning: Could not click main tab 'Teaduskonnad' automatically. Exception: {e}")

    success_count = 0
    fail_count = 0
    failed_tabs = []

    for tab_name in static_tabs:
        try:
            print(f"Looking for tab: {tab_name}")
            tab = wait.until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, tab_name)))
            # Try to scroll the tab bar if present
            try:
                tab_bar = driver.find_element(By.CSS_SELECTOR, ".nav-light-ul")
                driver.execute_script("arguments[0].scrollLeft = arguments[0].scrollWidth", tab_bar)
                time.sleep(0.3)
            except Exception:
                pass
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", tab)
            time.sleep(0.5)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            ActionChains(driver).move_to_element(tab).pause(0.3).perform()
            time.sleep(0.3)
            # If tab is a <span>, click its parent <a>
            if tab.tag_name == "span":
                tab = tab.find_element(By.XPATH, "..")
            try:
                tab.click()
            except Exception as click_e:
                print(f"Normal click failed for {tab_name}, trying JS click. Reason: {click_e}")
                driver.execute_script("arguments[0].click();", tab)
            time.sleep(2)

            # Click the "Kuupäevaline vaade" button using XPath by text
            try:
                time.sleep(1)  # Wait for the tab content to load
                daily_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Kuupäevaline vaade')]")
                ))
                # Scroll up to avoid tab bar overlay
                driver.execute_script("window.scrollBy(0, -100);")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", daily_btn)
                time.sleep(0.2)
                try:
                    daily_btn.click()
                except Exception as click_e:
                    print(f"Normal click failed for {tab_name}, trying JS click. Reason: {click_e}")
                    driver.execute_script("arguments[0].click();", daily_btn)
                print(f"'Kuupäevaline vaade' button clicked for {tab_name}.")
                time.sleep(2)
            except Exception as e:
                print(f"Error: Could not click 'Kuupäevaline vaade' for {tab_name}: {e}")
                fail_count += 1
                failed_tabs.append(tab_name)
                continue

            # Wait for any table to appear after clicking the button
            try:
                timetable_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table")))
                timetable_html = timetable_table.get_attribute("outerHTML")

                # Parse the table HTML and convert to JSON
                soup = BeautifulSoup(timetable_html, "html.parser")
                table = soup.find("table")
                headers = [th.get_text(strip=True) for th in table.find_all("th")]

                rows = []
                weekday_date_pattern = re.compile(r"^([A-Za-zÕÄÖÜõäöü]+)\s+(\d{2}\.\d{2}\.\d{4})$")

                current_section = None  # Track the current section header

                for tr in table.find_all("tr")[1:]:  # skip header row
                    # Check if this row is a section header (h3 inside td with colspan)
                    h3 = tr.find("h3")
                    if h3:
                        current_section = h3.get_text(strip=True)
                        continue  # Skip to next row

                    cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                    if not cells or len(cells) < len(headers):
                        continue
                    row_dict = dict(zip(headers, cells))

                    # --- Rename fields to remove special characters ---
                    field_map = {
                        "Keel": "keel",
                        "Tüüp": "tyyp",
                        "Õppejõud": "oppejoud",
                        "Ruum": "ruum",
                        "Õppenädalad": "oppenadalad",
                        "Rühmad": "ryhmad",
                        "Ainekava": "ainekavaurl",
                        "timetable_group": "tpg"
                    }
                    # Extract ainekavaurl from the <a> tag's href if present
                    ainekavaurl = ""
                    ainekava_td = tr.find_all("td")
                    if len(ainekava_td) >= headers.index("Ainekava") and "Ainekava" in headers:
                        ainekava_idx = headers.index("Ainekava")
                        a_tag = ainekava_td[ainekava_idx].find("a")
                        if a_tag and a_tag.has_attr("href"):
                            ainekavaurl = a_tag["href"]
                    # Rename fields
                    for old, new in field_map.items():
                        if old in row_dict:
                            if old == "Ainekava":
                                row_dict[new] = ainekavaurl
                            else:
                                row_dict[new] = row_dict[old]
                            del row_dict[old]

                    # Add timetable group name (renamed)
                    row_dict["tpg"] = tab_name

                    # Extract date from section header if available
                    if current_section and len(current_section) >= 10:
                        date_candidate = current_section[-10:]
                        # Simple check for date format dd.mm.yyyy
                        if re.match(r"\d{2}\.\d{2}\.\d{4}", date_candidate):
                            row_dict["date"] = date_candidate

                    # Further parse "Õppeaine" into "ainekood" and "aine", then remove "Õppeaine"
                    if "Õppeaine" in row_dict:
                        aine_raw = row_dict["Õppeaine"]
                        if "-" in aine_raw:
                            ainekood, aine = aine_raw.split("-", 1)
                            row_dict["ainekood"] = ainekood.strip()
                            row_dict["aine"] = aine.strip()
                        else:
                            row_dict["ainekood"] = aine_raw.strip()
                            row_dict["aine"] = ""
                        del row_dict["Õppeaine"]  # Remove the original field

                    # Parse "Aeg" into start and end time, ignore special characters like *
                    if "Aeg" in row_dict:
                        aeg_raw = row_dict["Aeg"]
                        # Remove any non-digit, non-colon, non-dash, non-space characters (like *)
                        aeg_clean = re.sub(r"[^\d:\-\s]", "", aeg_raw)
                        if "-" in aeg_clean:
                            start, end = aeg_clean.split("-", 1)
                            row_dict["start"] = start.strip()
                            row_dict["end"] = end.strip()
                        del row_dict["Aeg"]

                    rows.append(row_dict)

                # Remove empty keys/values from each row before saving
                rows = [
                    {k: v for k, v in row.items() if k.strip() and str(v).strip()}
                    for row in rows
                ]

                # Save as JSON
                output_json = os.path.join(output_directory, f"{tab_name}_daily_timetable.json")
                with open(output_json, "w", encoding="utf-8") as f:
                    json.dump(rows, f, ensure_ascii=False, indent=2)
                print(f"Saved daily timetable JSON for {tab_name} to {output_json}")

            except Exception as e:
                # Debug: print all tables found
                tables = driver.find_elements(By.TAG_NAME, "table")
                print(f"Error: Could not find daily timetable table for {tab_name}: {e}")
                print(f"Found {len(tables)} tables after clicking 'Kuupäevaline vaade' for {tab_name}")
                for idx, t in enumerate(tables):
                    print(f"Table {idx} HTML:\n{t.get_attribute('outerHTML')[:500]}")
                fail_count += 1
                failed_tabs.append(tab_name)
                continue

            # Do not save the table HTML to a file, Ctrl+K then Ctrl+C to comment out the following lines and Ctrl+K then Ctrl+U to uncomment if needed
            # output_file = os.path.join(output_directory, f"{tab_name}_daily_timetable.html")
            # with open(output_file, "w", encoding="utf-8") as file:
            #     file.write(timetable_html)
            # print(f"Saved daily timetable HTML for {tab_name} to {output_file}")
            success_count += 1

        except Exception as e:
            print(f"Error processing tab {tab_name}: {e}")
            fail_count += 1
            failed_tabs.append(tab_name)
            continue

finally:
    # Close the WebDriver
    driver.quit()

    # Summary
    print("\nScraping summary:")
    print(f"Successfully scraped: {success_count}")
    print(f"Failed: {fail_count}")

    # Write failed timetable groups to a txt file
    failed_file = os.path.join(output_directory, "failed_timetable_groups.txt")
    if failed_tabs:
        with open(failed_file, "w", encoding="utf-8") as f:
            for tab in failed_tabs:
                f.write(tab + "\n")
        print(f"Failed timetable groups are listed in: {failed_file}")
    else:
        print("No failed timetable groups.")