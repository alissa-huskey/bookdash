"""Script to login to goodreads."""

from random import randint, uniform
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium_stealth import stealth

from websockets import client  # noqa

from bookdash._private import GOODREADS_EMAIL, GOODREADS_PWD
from bookdash.elements.element import Element

bp = breakpoint


def make_driver():
    """Create and configure a web driver."""
    global driver

    agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

    options = webdriver.ChromeOptions()

    options.add_argument("--headless")

    options.add_argument(f"--user-agent={agent}")
    options.add_argument(f"--window-size=100,100")

    # this is responsible for saving and loading cookies
    options.add_argument("user-data-dir=tmp/selenium")

    # evade CAPCHA detection
    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    driver.set_window_size(600, 800)
    driver.set_window_position(x=0, y=0)

    # evade CAPCHA detection
    stealth(
        driver,
        languages=["en-US", "en"],
        vendor="Google Inc. (Apple)",
        platform="macos",
        webgl_vendor="Google Inc. (Apple)",
        renderer="ANGLE (Apple, ANGLE Metal Renderer: Apple M1 Max, Unspecified Version)",
        fix_hairline=True,
    )

    # useful debugging URLs
    #  driver.get("https://www.httpbin.org/headers")
    #  driver.get("https://users.nexusmods.com/")
    #  driver.get("https://bot.sannysoft.com/")

    return driver


def driver_settings():
    """Return a dictionary of driver's enabled features. (For debug
    purposes.)"""
    enabled = {}
    elm = request("https://www.whatismybrowser.com/")
    enabled["js"] = elm.first(".//a[@id='javascript-detection']/span/text()")
    enabled["cookies"] = elm.first(".//a[@id='cookies-detection']/span/text()")
    enabled["cookies-thirdparty"] = elm.first(".//a[@id='third-party-cookies-detection']/span/text()")

    return {k: ("Yes" in v) for k, v in settings.items()}

def request(url):
    """Send a request and return a parsed Element."""
    global driver
    driver.get(url)
    return Element(driver.page_source)

def type_slowly(field, text):
    """Simulate human typing by sending text one character at a time followed by a delay."""
    for c in text:
        sleep(uniform(0.1, 0.2))
        field.send_keys(c)

def wait():
    """Sleep for a random fraction of a second to simulate human pauses."""
    seconds = 1/randint(1,99)
    sleep(seconds)

def main():
    """Sign in to goodreads.com."""
    browser = make_driver()

    # TODO: figure out how to check if authenticated (ideally if there are cookies)
    #  request("https://goodreads.com")
    #  bp()

    # request user-facing signin page
    elm = request("https://www.goodreads.com/user/sign_in")

    signin_btn = browser.find_element(By.XPATH, "//button[normalize-space(text())='Sign in with email']")
    signin_btn.click()

    # fill in the form and submit it
    email_field = browser.find_element(By.XPATH, ".//input[@name='email']")
    type_slowly(email_field, GOODREADS_EMAIL)

    pwd_field = browser.find_element(By.XPATH, ".//input[@name='password']")
    type_slowly(pwd_field, GOODREADS_PWD)

    wait()
    submit_btn = browser.find_element(By.XPATH, ".//input[@id='signInSubmit']")
    submit_btn.click()

    # check for normal signin error (ie. wrong password)
    try:
        error = browser.find_element(By.XPATH, ".//div[@id='passkey-error-alert']")
        assert not error.is_displayed(), "Error loading signin page."
    except NoSuchElementException:
        ...

    # look for driver-related errors (ie. Javascript disabled)
    try:
        error = browser.find_element(By.XPATH, ".//div[@id='auth-error-message-box']")
        assert not error.is_displayed(), "Error submitting credentials."
    except NoSuchElementException:
        ...

    # look for CAPTCHA
    assert browser.title != f"Authentication required", "Problem submitting signin (possibly CAPTCHA)."

    # for debugging (only needed when headless)
    #  browser.save_screenshot("screenshot.png")


if __name__ == "__main__":
    main()

