import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from utils.helpers import wait_for_element, wait_for_elements, click_element, take_screenshot

# --- Localizadores (Locators) ---
# Login
USERNAME_INPUT = (By.ID, "user-name")
PASSWORD_INPUT = (By.ID, "password")
LOGIN_BUTTON = (By.ID, "login-button")

# Inventario / Catálogo
HEADER_SECONDARY = (By.CLASS_NAME, "header_secondary_container")
INVENTORY_ITEMS = (By.CLASS_NAME, "inventory_item")
PRODUCT_NAME = (By.CLASS_NAME, "inventory_item_name")
PRODUCT_PRICE = (By.CLASS_NAME, "inventory_item_price")
MENU_BUTTON = (By.ID, "react-burger-menu-btn")
FILTER_DROPDOWN = (By.CLASS_NAME, "product_sort_container")

# Interacción Carrito
ADD_TO_CART_BUTTON = (By.XPATH, "(//button[contains(@class, 'btn_inventory')])[1]")
CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")
CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
CART_ITEM_NAME = (By.CLASS_NAME, "inventory_item_name")


@pytest.fixture
def driver(request):
    """Fixture para inicializar el WebDriver antes de cada test y cerrarlo al finalizar."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    # Inicialización automatizada del driver usando webdriver-manager
    # En las versiones nuevas ya no hace falta meter el Service(ChromeDriverManager().install())
    # Selenium se encarga de buscar el driver correcto automáticamente.
    driver = webdriver.Chrome(options=options)
    
    yield driver
    
    # Lógica post-test: si el test falló, tomamos screenshot de evidencia
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        take_screenshot(driver, request.node.name)
        
    driver.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook de Pytest para checkear el estado del resultado del test (pasa/falla)"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ==============================================================================
# CASOS DE PRUEBA
# ==============================================================================

def test_login_exitoso(driver):
    """Caso 1: Validar Login Exitoso con credenciales estándar."""
    driver.get("https://www.saucedemo.com/")
    
    # Flujo de Login
    wait_for_element(driver, USERNAME_INPUT).send_keys("standard_user")
    wait_for_element(driver, PASSWORD_INPUT).send_keys("secret_sauce")
    click_element(driver, LOGIN_BUTTON)
    
    # Validaciones obligatorias
    assert "/inventory.html" in driver.current_url, "La URL no corresponde al inventario."
    
    header_title = wait_for_element(driver, HEADER_SECONDARY).text
    assert "Products" in header_title, "El título de la sección de productos no está visible."
    assert "Swag Labs" in driver.title, "El título de la pestaña de la página es incorrecto."


def test_verificacion_catalogo(driver):
    """Caso 2: Verificar elementos del catálogo y listar primer producto."""
    # Precondición: Loguearse de manera independiente
    driver.get("https://www.saucedemo.com/")
    wait_for_element(driver, USERNAME_INPUT).send_keys("standard_user")
    wait_for_element(driver, PASSWORD_INPUT).send_keys("secret_sauce")
    click_element(driver, LOGIN_BUTTON)
    
    # Valida título general de la app
    assert "Swag Labs" in driver.title
    
    # Valida presencia de productos (comprueba que existan elementos en la lista)
    products = wait_for_elements(driver, INVENTORY_ITEMS)
    assert len(products) > 0, "No se encontraron productos en el catálogo."
    
    # Listar nombre y precio del primer elemento visible
    first_product_name = products[0].find_element(*PRODUCT_NAME).text
    first_product_price = products[0].find_element(*PRODUCT_PRICE).text
    print(f"\n[INFO] Primer producto del catálogo: {first_product_name} - Precio: {first_product_price}")
    
    # Validar que componentes críticos de la UI estén presentes
    assert wait_for_element(driver, MENU_BUTTON).is_displayed(), "El menú lateral no está presente."
    assert wait_for_element(driver, FILTER_DROPDOWN).is_displayed(), "El filtro de productos no está presente."


def test_interaccion_y_verificacion_carrito(driver):
    """Caso 3: Añadir primer producto al carrito y verificar su persistencia."""
    # Precondición: Loguearse
    driver.get("https://www.saucedemo.com/")
    wait_for_element(driver, USERNAME_INPUT).send_keys("standard_user")
    wait_for_element(driver, PASSWORD_INPUT).send_keys("secret_sauce")
    click_element(driver, LOGIN_BUTTON)
    
    # Obtener el nombre del primer producto antes de agregarlo
    products = wait_for_elements(driver, INVENTORY_ITEMS)
    expected_product_name = products[0].find_element(*PRODUCT_NAME).text
    
    # Agregar el primer producto al carrito
    click_element(driver, ADD_TO_CART_BUTTON)
    
    # Verificar que el contador del carrito se incremente a "1"
    badge_text = wait_for_element(driver, CART_BADGE).text
    assert badge_text == "1", f"El contador del carrito debería ser 1 pero es {badge_text}."
    
    # Navegar al carrito de compras
    click_element(driver, CART_LINK)
    assert "/cart.html" in driver.current_url, "No se redirigió correctamente a la página del carrito."
    
    # Comprobar que el producto añadido coincida con el que está en el carrito
    item_in_cart_name = wait_for_element(driver, CART_ITEM_NAME).text
    assert item_in_cart_name == expected_product_name, f"El producto en el carrito ({item_in_cart_name}) no coincide con el esperado ({expected_product_name})."