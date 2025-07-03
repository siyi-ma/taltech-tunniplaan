from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import os
import random

def scrape_and_save_data(url, output_dir):
    # Set up Edge options
    edge_options = Options()
    edge_options.add_argument('--ignore-certificate-errors')
    edge_options.add_argument('--ignore-ssl-errors')
    edge_options.add_argument('--log-level=3')  # Suppress most logging messages

    # Initialize the WebDriver with options
    service = Service("C:/edgedriver_win64/msedgedriver.exe")  # Update the path to your Edge WebDriver
    driver = webdriver.Edge(service=service, options=edge_options)

    try:
        # Open the webpage
        driver.get(url)

        # Wait for the elements to be present
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "avaldus_andmerida")))
        WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tbl_cell")))

        # Find elements by class name
        left_column_elements = driver.find_elements(By.CLASS_NAME, "avaldus_andmerida")
        right_column_elements = driver.find_elements(By.CLASS_NAME, "tbl_cell")

        # Initialize a list to store the structured data
        data = []

        # Retrieve values from hidden inputs outside the loop
        keel_et_value = driver.find_element(By.ID, "KEEL_et").get_attribute("value")
        keel_en_value = driver.find_element(By.ID, "KEEL_en").get_attribute("value")

        # Loop through the elements and pair them
        for left, right in zip(left_column_elements, right_column_elements):
            left_text = left.get_attribute("innerText").strip()
            right_text = right.get_attribute("innerText").strip()

            # Exclude elements with the name "õppeaine maht AP" or "vastutav õppejõud"
            if left_text == "õppeaine maht AP" or left_text == "vastutav õppejõud" or left_text == "õppekeel":
                continue

            # Handle "Tunniplaani link" to scrape the href attribute and remove the suffix
            if left_text == "Tunniplaani link":
                href = right.find_element(By.TAG_NAME, "a").get_attribute("href")
                right_text = href.split("?")[0]  # Remove the suffix after "?"

            # Append the data as a dictionary
            data.append({"Left Column": left_text, "Right Column": right_text})

        # Append language info to the data list inside the loop
        data.append({"Left Column": "KEEL_et", "Right Column": keel_et_value})
        data.append({"Left Column": "KEEL_en", "Right Column": keel_en_value})

        # Generate a unique filename based on the course code or title
        course_code = url.split("/")[-1]  # Extract the course code from the URL
        output_file = os.path.join(output_dir, f"{course_code}.json")

        # Save the structured data to a JSON file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        print(f"Data saved to '{output_file}'.")

    finally:
        # Close the WebDriver
        driver.quit()

# --- NEW CODE: Load URLs from unique_ainekavaurl.json instead of static list ---
input_ainekavaurl_file = "C:/Users/siyi.ma/Downloads/25sdailytimetables_new/unique_ainekavaurl.json"
output_directory = "C:/Users/siyi.ma/Downloads/25sCourseData"
os.makedirs(output_directory, exist_ok=True)

with open(input_ainekavaurl_file, "r", encoding="utf-8") as f:
    course_urls = json.load(f)

# --- TESTING BLOCK: Run the loop for a random 10 courses ---
if __name__ == "__main__":
    success_count = 0
    fail_count = 0
    failed_courses = []

    test_sample = random.sample(course_urls, min(10, len(course_urls)))
    for course_url in test_sample:
        try:
            scrape_and_save_data(course_url, output_directory)
            success_count += 1
        except Exception as e:
            fail_count += 1
            failed_courses.append({"url": course_url, "reason": str(e)})
            print(f"Failed to scrape {course_url}: {e}")

    print("\nSummary of test run:")
    print(f"Total attempted: {len(test_sample)}")
    print(f"Successes: {success_count}")
    print(f"Failures: {fail_count}")
    if failed_courses:
        print("Failed course URLs and reasons:")
        for fail in failed_courses:
            print(f"- {fail['url']}: {fail['reason']}")