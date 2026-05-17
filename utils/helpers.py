import os
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def wait_for_element(driver, locator, timeout=10):
    """Espera explícita a que un elemento esté visible en el DOM."""
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))

def wait_for_elements(driver, locator, timeout=10):
    """Espera explícita a que al menos un elemento de la lista esté presente."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located(locator))

def click_element(driver, locator, timeout=10):
    """Espera que el elemento sea clickeable y hace click."""
    element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))
    element.click()

def take_screenshot(driver, test_name):
    """Toma una captura de pantalla automática y la guarda en la carpeta reports/."""
    report_dir = "reports"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(report_dir, f"fail_{test_name}_{timestamp}.png")
    driver.save_screenshot(filepath)
    print(f"\n[EVIDENCIA] Captura de pantalla guardada en: {filepath}")