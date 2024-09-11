import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError

import json
import time
import random
import threading


@pytest.fixture(scope="module")
def browser():
    driver = webdriver.Chrome()
    driver.implicitly_wait(1)
    yield driver
    driver.quit()

def test_shop_title_link(browser):
    browser.get("http://localhost:5000")

    # Wait for the page to load and the link to show up
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "shop-title"))
    )

    initial_url = browser.current_url

    # Click the title
    browser.find_element(By.ID, "shop-title").click()
    
    # Wait for the page to load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    new_url = browser.current_url
    
    # Check if the URL is the same
    assert initial_url == new_url, f"Expected to stay on the home page, but got redirected to {new_url}"

def test_shop_title_link_style(browser):
    browser.get("http://localhost:5000")

    shop_title_link = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "shop-title"))
    )

    initial_color = shop_title_link.value_of_css_property('color')
    
    # Hover over the link
    ActionChains(browser).move_to_element(shop_title_link).perform()
    
    # Wait for the hover effect to apply
    time.sleep(0.5)
    
    # Get the color after hovering
    hover_color = shop_title_link.value_of_css_property('color')
    
    # Check that the color changed to blue
    assert hover_color != initial_color, f"Color did not change on hover!"
    assert 'rgba(0, 0, 255, 1)' in hover_color, f"Hover color is not blue, but {hover_color}"


def test_product_details(browser):
    browser.get("http://localhost:5000")

    # Click on the first product
    browser.find_element(By.CLASS_NAME, "product").click()

    # Wait for the product details to appear
    details = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "product-details"))
    )
    
    # Check if the details are visible
    assert details.is_displayed()
    
    # Check if the product name and description are not empty
    name = browser.find_element(By.ID, "detail-name")
    description = browser.find_element(By.ID, "detail-description")
    assert name.text != ""
    assert description.text != ""

def test_product_details_close(browser):
    browser.get("http://localhost:5000")
    
    # Click on the first product
    browser.find_element(By.CLASS_NAME, "product").click()

    # Wait for the product details to appear
    details = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "product-details"))
    )
    
    # Check if the details are visible
    assert details.is_displayed()
    
    # Find and click the close button
    browser.find_element(By.CSS_SELECTOR, "#product-details .close").click()
    
    # Wait for the product details to disappear
    WebDriverWait(browser, 10).until(
        EC.invisibility_of_element_located((By.ID, "product-details"))
    )
    
    # Check if the details are no longer visible
    assert not details.is_displayed()

def test_product_details_close_and_cross_color(browser):
    browser.get("http://localhost:5000")
    
    # Click on the first product
    browser.find_element(By.CLASS_NAME, "product").click()

    # Wait for the product details to appear
    details = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "product-details"))
    )

    # Find the close button
    close_button = browser.find_element(By.CSS_SELECTOR, "#product-details .close")
    
    # Check the initial color rgb(170, 170, 170)
    initial_color = browser.execute_script(
        "return window.getComputedStyle(arguments[0]).getPropertyValue('color')", 
        close_button
    )
    assert initial_color == "rgb(170, 170, 170)", f"Initial color is not grey, but {initial_color}"
    
    # Hover over the close button
    ActionChains(browser).move_to_element(close_button).perform()
    
    # Check the hover color rgb(0, 0, 0)
    time.sleep(0.5)
    hover_color = browser.execute_script(
        "return window.getComputedStyle(arguments[0]).getPropertyValue('color')", 
        close_button
    )
    assert hover_color == "rgb(0, 0, 0)", f"Hover color is not black, but {hover_color}"
    
    # Click the close button
    close_button.click()
    
    # Wait for the product details to disappear
    WebDriverWait(browser, 10).until(
        EC.invisibility_of_element_located((By.ID, "product-details"))
    )
    
    # Check if the details are no longer visible
    assert not details.is_displayed()

def test_product_details_close_by_clicking_outside(browser):
    browser.get("http://localhost:5000")

    # Click on the first product
    browser.find_element(By.CLASS_NAME, "product").click()

    # Wait for the product details to appear
    details = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "product-details"))
    )

    # Click a point over the title
    time.sleep(1)
    title = browser.find_element(By.ID, "shop-title")
    ActionChains(browser).move_to_element(title).move_by_offset(-25, -25).click().perform()
    
    # Wait for the product details to disappear
    time.sleep(1)
    WebDriverWait(browser, 10).until(
        EC.invisibility_of_element_located((By.ID, "product-details"))
    )
    
    # Check if the details are no longer visible
    assert not details.is_displayed()

def test_product_details_switch_without_blinking(browser):
    browser.get("http://localhost:5000")
    
    # Click on the first product
    browser.find_element(By.CLASS_NAME, "product").click()
    
    # Wait for the product details to appear
    details = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "product-details"))
    )

    # Get the initial product name
    initial_name = browser.find_element(By.ID, "detail-name").text
    
    # Define a function to check if the modal blinks
    def check_modal_blink():
        start_time = time.time()
        while time.time() - start_time < 1:  # Check for 1 second
            display = browser.execute_script(
                "return document.getElementById('product-details').style.display;"
            )
            if display == 'none':
                return True
            time.sleep(0.01)
        return False

    # Click on the second product
    browser.find_elements(By.CLASS_NAME, "product")[1].click()
    
    assert not check_modal_blink(), "Product details blinked when they should remain open"
    updated_name = browser.find_element(By.ID, "detail-name").text
    assert initial_name != updated_name, "Product name did not change"
    assert details.is_displayed(), "Product details are not visible after switching products"

def test_product_images_heights(browser):
    browser.get("http://localhost:5000")
    
    # Find all product images
    product_images = browser.find_elements(By.CSS_SELECTOR, ".product img")

    first_height = product_images[0].size['height']
    for img in product_images[1:]:
        assert img.size['height'] == first_height, f"Image height mismatch: {img.size['height']} != {first_height}"

def test_product_images_alignment(browser):
    browser.get("http://localhost:5000")

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product"))
    )

    product_images = browser.find_elements(By.CSS_SELECTOR, ".product img")

    # Group images by their y-coordinate (row)
    rows = {}
    for img in product_images:
        y = img.location['y']
        if y not in rows:
            rows[y] = []
        rows[y].append(img)
    
    leng = None

    # Check alignment within each row
    for row in rows.values():
        for i in range(1, len(row)):
            prev_image = row[i-1]
            curr_image = row[i]
            assert curr_image.location['x'] > prev_image.location['x'], f"Images not aligned horizontally within the row"
            if not leng:
                leng = curr_image.location['x'] - prev_image.location['x']
            else:
                assert abs((curr_image.location['x'] - prev_image.location['x']) - leng) < 2, f"Images have inconsistent spacing between them"

    # Check that rows are properly stacked
    leng = None
    sorted_y = sorted(rows.keys())
    for i in range(1, len(sorted_y)):
        print(leng)
        assert sorted_y[i] > sorted_y[i-1], f"Rows not properly stacked vertically"
        if not leng:
            leng = sorted_y[i] - sorted_y[i-1]
        else:
            assert abs((sorted_y[i] - sorted_y[i-1]) - leng) < 2, f"Rows have inconsistent spacing between them"


def test_add_to_cart(browser):
    browser.get("http://localhost:5000")
    
    # Click the "Add to Cart" button of the first product
    browser.find_element(By.CSS_SELECTOR, ".product button").click()

    # Wait for the cart to update
    cart_items = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "cart-items"))
    )
    
    # Check if the cart is not empty
    assert len(cart_items.find_elements(By.TAG_NAME, "li")) > 0

    # Check if the total is greater than zero
    total = browser.find_element(By.ID, "cart-total")
    assert float(total.text) > 0

def test_cart_remove_button_color(browser):
    browser.get("http://localhost:5000")

    # Add the first product to the cart
    browser.find_element(By.CSS_SELECTOR, ".product button").click()
    
    # Wait for the cart to update
    cart_items = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "cart-items"))
    )
    
    # Find the remove button
    remove_button = cart_items.find_element(By.CSS_SELECTOR, ".remove-btn")
    
    # Check the initial color (gray)
    initial_color = browser.execute_script(
        "return window.getComputedStyle(arguments[0]).getPropertyValue('background-color')", 
        remove_button
    )
    assert initial_color == "rgb(128, 128, 128)", f"Initial color is not gray, but {initial_color}"
    
    # Hover over the remove button
    ActionChains(browser).move_to_element(remove_button).perform()

    # Check the hover color (red)
    time.sleep(0.5)
    hover_color = browser.execute_script(
        "return window.getComputedStyle(arguments[0]).getPropertyValue('background-color')", 
        remove_button
    )
    assert hover_color == "rgb(255, 77, 77)", f"Hover color is not red, but {hover_color}"

def test_product_hover_background_change(browser):
    browser.get("http://localhost:5000")

    # Ensure we have at least one product
    products = browser.find_elements(By.CLASS_NAME, "product")
    assert len(products) > 0, "No products found on the page"
    
    for index, product in enumerate(products):
        initial_color = browser.execute_script(
            "return window.getComputedStyle(arguments[0]).getPropertyValue('background-color')", 
            product
        )
        
        # Hover over the product
        ActionChains(browser).move_to_element(product).perform()
        time.sleep(0.1)
        
        # Get the background color after hovering
        hover_color = browser.execute_script(
            "return window.getComputedStyle(arguments[0]).getPropertyValue('background-color')", 
            product
        )
        
        # Check if the color has changed
        assert initial_color != hover_color, f"Background color did not change on hover for product {index + 1}. Initial: {initial_color}, Hover: {hover_color}"
        
        # Check if the new color is gray (you may need to adjust the RGB values based on your exact implementation)
        assert hover_color == "rgb(160, 160, 160)", f"Hover color is not light gray for product {index + 1}, but {hover_color}"
        
        # Move the mouse away from the product to reset the hover state
        ActionChains(browser).move_to_element(browser.find_element(By.ID, "shop-title")).move_by_offset(-25, -25).click().perform()
        time.sleep(0.1)

        hover_color = browser.execute_script(
            "return window.getComputedStyle(arguments[0]).getPropertyValue('background-color')", 
            product
        )

        assert initial_color == hover_color, f"Background color did not change back after removing hover for product {index + 1}. Initial: {initial_color}, After removing hover: {hover_color}"


def test_minus_button_inactive_for_single_item(browser):
    browser.get("http://localhost:5000")  # Adjust URL if needed
    
    # Wait for the products to load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product"))
    )

    # Add the first product to the cart
    browser.find_element(By.CSS_SELECTOR, ".product button").click()
    
    # Wait for the cart to update
    cart_items = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "cart-items"))
    )

    # Check if minus button is disabled and greyed out
    minus_button = cart_items.find_element(By.NAME, "minus_button")
    assert minus_button.get_attribute("disabled"), "Minus button is not disabled for a single item"
    button_opacity = browser.execute_script("return window.getComputedStyle(arguments[0]).getPropertyValue('opacity')", minus_button)
    assert float(button_opacity) < 1, f"Minus button opacity is not reduced (current opacity: {button_opacity})"

def test_add_multiple_quantities_of_same_item(browser):
    browser.get("http://localhost:5000")
    
    # Add the first product to the cart multiple times
    times = 3
    add_to_cart_button = browser.find_element(By.CSS_SELECTOR, ".product button")
    for _ in range(times):
        add_to_cart_button.click()
        time.sleep(0.5)
    
    # Check if the quantity in the cart is correct
    cart_item = browser.find_element(By.CSS_SELECTOR, "#cart-items li")
    quantity = int(cart_item.find_element(By.CLASS_NAME, "item-quantity").text)
    assert quantity == times, f"Expected quantity 3, but got {quantity}"
    
    # Check if the total price is correct
    price = float(browser.find_element(By.CSS_SELECTOR, ".product p").text.split("$")[1])
    expected_total = price * times
    actual_total = float(browser.find_element(By.ID, "cart-total").text)
    assert abs(actual_total - expected_total) < 0.01, f"Expected total {expected_total}, but got {actual_total}"

def test_add_multiple_items_to_cart(browser):
    browser.get("http://localhost:5000")

    # Add the first product to the cart
    browser.find_element(By.CSS_SELECTOR, ".product button").click()

    # Wait for the cart to update
    cart_items = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "cart-items"))
    )
    
    # Generate a random number of additional clicks (1 to 10)
    additional_clicks = random.randint(1, 10)
    for _ in range(additional_clicks):
        cart_items.find_element(By.NAME, "plus_button").click()
        time.sleep(0.1)
    
    # Find the quantity display element and get its text
    quantity_element = cart_items.find_element(By.CLASS_NAME, "item-quantity")
    actual_quantity = int(quantity_element.text)
    
    # Assert that the amount matches the expected total
    expected_total = additional_clicks + 1
    assert actual_quantity == expected_total, f"Expected {expected_total} items, but found {actual_quantity}"
    
    # Assert that the total price is correct
    single_item_price = float(browser.find_element(By.CSS_SELECTOR, ".product p").text.split("$")[1])
    expected_total_price = single_item_price * expected_total
    total_price_element = browser.find_element(By.ID, "cart-total")
    actual_total_price = float(total_price_element.text)
    assert abs(actual_total_price - expected_total_price) < 0.01, f"Expected total price {expected_total_price}, but found {actual_total_price}"

def test_add_random_items_and_check_total(browser):
    browser.get("http://localhost:5000")
    
    # Wait for the products to load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product"))
    )
    
    products = browser.find_elements(By.CLASS_NAME, "product")
    total_expected = 0
    items_added = 0
    
    # Add 10 random items to the cart
    num_items = 10
    for _ in range(num_items):
        # Select a random product
        product = random.choice(products)
        
        # Get the price of the product
        price = float(product.find_element(By.CSS_SELECTOR, "p").text.split("$")[1])
        
        # Add the product to the cart
        product.find_element(By.TAG_NAME, "button").click()

        total_expected += price
        items_added += 1
        time.sleep(0.5)
    
    # Get the actual total from the cart
    cart_total_element = browser.find_element(By.ID, "cart-total")
    total_actual = float(cart_total_element.text)
    
    # Check if the totals are correct
    assert abs(total_actual - total_expected) < 0.01, f"Expected total {total_expected}, but got {total_actual}"
    
    # Check if the cart count is correct
    cart_count = 0
    i = 0
    cart_items = browser.find_elements(By.ID, "cart-items")[0]
    print(cart_items)
    for line in cart_items.get_attribute("innerHTML").split("\n"):
        print(line)
        if not "item-quantity" in line:
            continue
        cart_count += int(line.split('"item-quantity">')[1].split("<")[0])
        i += 1
    print(i)

    assert cart_count == num_items, f"Expected {num_items} items in cart, but got {cart_count}"

def test_remove_items_from_cart(browser):
    browser.get("http://localhost:5000")
    
    # Add two different products to the cart
    products = browser.find_elements(By.CLASS_NAME, "product")
    for product in products[:2]:
        product.find_element(By.TAG_NAME, "button").click()
        time.sleep(0.5)
    
    # Remove the first item
    browser.find_elements(By.CSS_SELECTOR, "#cart-items .remove-btn")[0].click()
    
    # Check if the cart has only one item left
    time.sleep(0.5)
    cart_items = browser.find_elements(By.CSS_SELECTOR, "#cart-items li")
    assert len(cart_items) == 1, f"Expected 1 item in cart, but found {len(cart_items)}"

def test_add_and_decrease_product_quantity(browser):
    browser.get("http://localhost:5000")
    
    # Wait for the products to load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product"))
    )
    
    # Find the first product and its price
    product = browser.find_element(By.CLASS_NAME, "product")
    price_text = product.find_element(By.CSS_SELECTOR, "p").text
    price = float(price_text.split("$")[1])
    
    # Add the product to the cart twice
    add_to_cart_button = product.find_element(By.TAG_NAME, "button")
    add_to_cart_button.click()
    time.sleep(0.5)
    add_to_cart_button.click()
    time.sleep(0.5)
    
    # Wait for the cart to update
    WebDriverWait(browser, 10).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#cart-items .item-quantity"), "2")
    )
    
    # Check if the quantity in the cart is correct
    cart_item = browser.find_element(By.CSS_SELECTOR, "#cart-items li")
    quantity = int(cart_item.find_element(By.CLASS_NAME, "item-quantity").text)
    assert quantity == 2, f"Expected quantity 2, but got {quantity}"
    
    # Check if the total price is correct
    expected_total = price * 2
    cart_total = float(browser.find_element(By.ID, "cart-total").text)
    assert abs(cart_total - expected_total) < 0.01, f"Expected total {expected_total}, but got {cart_total}"
    
    # Find and click the minus button
    cart_item.find_element(By.CSS_SELECTOR, "button[name='minus_button']").click()

    # Wait for the cart to update
    WebDriverWait(browser, 10).until(
        EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#cart-items .item-quantity"), "1")
    )
    
    # Check if the quantity has decreased
    cart_item = browser.find_element(By.CSS_SELECTOR, "#cart-items li")
    new_quantity = int(cart_item.find_element(By.CLASS_NAME, "item-quantity").text)
    assert new_quantity == 1, f"Expected quantity 1 after decrease, but got {new_quantity}"

    # Check if the total price has updated correctly
    expected_new_total = price
    new_cart_total = float(browser.find_element(By.ID, "cart-total").text)
    assert abs(new_cart_total - expected_new_total) < 0.01, f"Expected new total {expected_new_total}, but got {new_cart_total}"

def test_add_two_items_remove_one_check_total(browser):
    browser.get("http://localhost:5000")
    
    # Wait for the products to load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product"))
    )
    
    # Find the first two products and their prices
    products = browser.find_elements(By.CLASS_NAME, "product")[:2]
    prices = []
    for product in products:
        price_text = product.find_element(By.CSS_SELECTOR, "p").text
        prices.append(float(price_text.split("$")[1]))
        time.sleep(0.5)
        add_to_cart_button = product.find_element(By.TAG_NAME, "button")
        add_to_cart_button.click()
        time.sleep(0.5)

    # Wait for the cart to update
    WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#cart-items li"))
    )
    
    # Check if both items are in the cart
    cart_items = browser.find_elements(By.CSS_SELECTOR, "#cart-items li")
    assert len(cart_items) == 2, f"Expected 2 items in cart, but got {len(cart_items)}"
    
    # Check if the total price is correct
    expected_total = sum(prices)
    cart_total = float(browser.find_element(By.ID, "cart-total").text)
    assert abs(cart_total - expected_total) < 0.01, f"Expected total {expected_total}, but got {cart_total}"
    
    # Find and click the remove button for the first item
    cart_items[0].find_element(By.CSS_SELECTOR, "button.remove-btn").click()

    # Wait for the cart to update
    WebDriverWait(browser, 10).until(
        EC.staleness_of(cart_items[0])
    )
    
    # Check if only one item remains in the cart
    updated_cart_items = browser.find_elements(By.CSS_SELECTOR, "#cart-items li")
    assert len(updated_cart_items) == 1, f"Expected 1 item in cart after removal, but got {len(updated_cart_items)}"
    
    # Check if the total price has updated correctly
    expected_new_total = prices[1]  # Price of the second item
    new_cart_total = float(browser.find_element(By.ID, "cart-total").text)
    assert abs(new_cart_total - expected_new_total) < 0.01, f"Expected new total {expected_new_total}, but got {new_cart_total}"

def test_buy_button_off_on_off_state(browser):
    browser.get("http://localhost:5000")
    
    # Wait for the products to load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product"))
    )
    
    # Find the buy button
    buy_button = browser.find_element(By.ID, "buy-button")
    
    # Check that the buy button is initially inactive
    assert buy_button.get_attribute("disabled"), "Buy button should be inactive when cart is empty"
    
    # Add the first product to the cart
    browser.find_element(By.CSS_SELECTOR, ".product button").click()
    
    # Wait for the cart to update
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "cart-items"))
    )
    
    # Check that the buy button is now active
    assert not buy_button.get_attribute("disabled"), "Buy button should be active when cart has items"
    
    # Find and click the remove button
    browser.find_element(By.CSS_SELECTOR, "#cart-items .remove-btn").click()
    
    # Wait for the cart to update
    WebDriverWait(browser, 10).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "#cart-items li"))
    )
    
    # Check that the buy button is inactive again
    assert buy_button.get_attribute("disabled"), "Buy button should be inactive when cart is emptied"

def test_buy_process_and_cart_reset(browser):
    browser.get("http://localhost:5000")
    
    # Wait for the products to load
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product"))
    )
    
    # Add the first product to the cart
    browser.find_element(By.CSS_SELECTOR, ".product button").click()
    
    # Wait for the cart to update
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "cart-items"))
    )
    
    # Find and click the Buy button
    buy_button = browser.find_element(By.ID, "buy-button")
    buy_button.click()
    
    # Wait for the alert to be present
    WebDriverWait(browser, 10).until(EC.alert_is_present())
    
    # Switch to the alert and accept it
    alert = Alert(browser)
    alert.accept()
    
    # Wait for the cart to update (it should be empty now)
    WebDriverWait(browser, 10).until(
        EC.invisibility_of_element_located((By.CSS_SELECTOR, "#cart-items li"))
    )
    
    # Check if the cart is empty
    cart_items = browser.find_elements(By.CSS_SELECTOR, "#cart-items li")
    assert len(cart_items) == 0, "Cart should be empty after purchase"
    
    # Check if the cart total is zero
    cart_total = browser.find_element(By.ID, "cart-total")
    assert float(cart_total.text) == 0, f"Cart total should be zero, but is {cart_total.text}"
    
    # Check if the buy button is inactive again
    buy_button = browser.find_element(By.ID, "buy-button")
    assert buy_button.get_attribute("disabled"), "Buy button should be inactive when cart is empty"
