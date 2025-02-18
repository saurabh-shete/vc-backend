from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def extract_title_by_class(driver):
    try:
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "text-body-medium.break-words")
            )
        )
        title = title_element.text.strip()
        return title
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
