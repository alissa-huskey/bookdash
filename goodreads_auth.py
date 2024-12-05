"""Script to login to goodreads."""

from random import randint, uniform
from time import sleep

from bookdash.browser import Browser

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium_stealth import stealth

from websockets import client  # noqa

from bookdash.elements.element import Element
from bookdash.config import GoodreadsConfig

bp = breakpoint
config = GoodreadsConfig()


def main():
    """Sign in to goodreads.com."""
    browser = Browser(user_data_dir="tmp/selenium", headless=False)

    # request user-facing signin page
    browser.get("https://www.goodreads.com/user/sign_in")

    # assume that the user is already signed in if they have cookies
    # or if redirected to the home page
    cookies = [c["name"] for c in browser.get_cookies()]
    if "session-id" in cookies or browser.current_url == "https://goodreads.com/":
        return

    # click the "Sign in with email" button
    signin_btn = browser.find_xpath("//button[normalize-space(text())='Sign in with email']")
    signin_btn.click()

    # fill in the form and submit it
    email_field = browser.find_xpath(".//input[@name='email']")
    browser.type_slowly(email_field, config.email)

    pwd_field = browser.find_xpath(".//input[@name='password']")
    browser.type_slowly(pwd_field, config.pwd)

    submit_btn = browser.find_xpath(".//input[@id='signInSubmit']")
    submit_btn.click()

    # check for normal signin error (ie. wrong password)
    error = browser.find_xpath(".//div[@id='passkey-error-alert']", quiet=True)
    assert not error or not error.is_displayed(), "Error loading signin page."

    # look for driver-related errors (ie. Javascript disabled)
    error = browser.find_xpath(".//div[@id='auth-error-message-box']", quiet=True)
    assert not error or not error.is_displayed(), "Error submitting credentials."

    # look for CAPTCHA
    assert browser.driver.title != f"Authentication required", "Problem submitting signin (possibly CAPTCHA)."

    assert browser.driver.current_url == "https://www.goodreads.com/", "Login (probably) unsuccessful."

    # for debugging (only needed when headless)
    #  browser.save_screenshot("screenshot.png")


if __name__ == "__main__":
    main()
