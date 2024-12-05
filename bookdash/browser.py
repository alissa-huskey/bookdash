"""Headless web browser via selenium webdriver."""

from functools import cached_property, partialmethod
from random import uniform
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from seleniumwire import webdriver
from seleniumwire.request import Response

from bookdash import forward_attr

bp = breakpoint


class Browser():
    """Headless web browser."""

    DELAY_RANGE = (0.1, 0.2)

    USERAGENT = (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.3 6 "
        "(KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    )

    started = False

    def __init__(self, headless=True, user_data_dir=None):
        self.headless = headless
        self.user_data_dir = user_data_dir

    @property
    def options(self):
        """Return driver options."""
        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument("--headless")

        # this is responsible for saving and loading cookies
        # NOTE: if it remains None, there is no cookie handling
        #       the user will most likely get flagged for frequent logins
        if self.user_data_dir:
            options.add_argument(f"user-data-dir={self.user_data_dir}")

        options.add_argument(f"--user-agent={self.USERAGENT}")
        options.add_argument(f"--window-size=100,100")

        # evade CAPCHA detection
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        return options

    @cached_property
    def driver(self):
        """Return a web driver."""
        driver = webdriver.Chrome(options=self.options)

        # nicer window size and position,
        # also may evade CAPCHA detection
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

        self.started = True

        # useful debugging URLs
        #  driver.get("https://www.httpbin.org/headers")
        #  driver.get("https://users.nexusmods.com/")
        #  driver.get("https://bot.sannysoft.com/")

        return driver

    def _mk_driver_getter(attr):
        """Return a getter function."""
        def _driver_getter(self):
            """Get an attribute from self.driver."""
            return getattr(self.driver, attr)
        return _driver_getter

    back = property(_mk_driver_getter("back"))
    current_url = property(_mk_driver_getter("current_url"))
    forward = property(_mk_driver_getter("forward"))
    get_cookies = property(_mk_driver_getter("get_cookies"))
    last_request = property(_mk_driver_getter("last_request"))
    name = property(_mk_driver_getter("name"))
    page_source = property(_mk_driver_getter("page_source"))
    refresh = property(_mk_driver_getter("refresh"))
    requests = property(_mk_driver_getter("requests"))
    save_screenshot = property(_mk_driver_getter("save_screenshot"))
    session_id = property(_mk_driver_getter("session_id"))
    wait_for_request = property(_mk_driver_getter("wait_for_request"))

    def get(self, url) -> Response:
        """Send a get request and return response."""
        self.driver.get(url)
        if self.driver.last_request:
            return self.driver.last_request.response

    def quit(self):
        """Quit the browser driver if it has been started."""
        if self.started:
            self.driver.quit()

    def find(self, by, query, *args, get_all=False, quiet=False, **kwargs):
        """Find element or elements.

        Args:
            by (str): how to search (from By)
            query (str): query string
            get_all (bool, default=False): return all matching elements (defaults to first)
            quiet (bool, default=False): suppress exception if not found and return None instead

            *args: args for find_element or find_elements
            *kwargs: kwargs for find_element or find_elements
        Return one element by default, or all elements if get_all is True."""

        if get_all:
            finder = self.driver.find_elements
        else:
            finder = self.driver.find_element

        try:
            return finder(by, query, *args, **kwargs)
        except NoSuchElementException as e:
            # only raise exception if quiet is False
            if not quiet:
                raise e

    find_class_name = partialmethod(find, By.CLASS_NAME)
    find_css_selector = partialmethod(find, By.CSS_SELECTOR)
    find_id = partialmethod(find, By.ID)
    find_link_text = partialmethod(find, By.LINK_TEXT)
    find_name = partialmethod(find, By.NAME)
    find_partial_link_text = partialmethod(find, By.PARTIAL_LINK_TEXT)
    find_tag_name = partialmethod(find, By.TAG_NAME)
    find_xpath = partialmethod(find, By.XPATH)


    def type_slowly(self, field, *keys):
        """Simulate human typing by sending text one character at a time followed by a delay."""
        for text in keys:
            for c in text:
                sleep(uniform(*self.DELAY_RANGE))
                field.send_keys(c)
