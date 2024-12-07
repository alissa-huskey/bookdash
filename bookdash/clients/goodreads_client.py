"""Goodreads client module."""

from datetime import datetime
from functools import partialmethod

import requests
from bs4 import BeautifulSoup
from more_itertools import first

from bookdash import abort, log
from bookdash.books import Book
from bookdash.browser import Browser
from bookdash.clients.base_client import BaseClient
from bookdash.config import Config
from bookdash.cookie_jar import CookieJar
from bookdash.elements.element import Element
from bookdash.elements.found_book_element import FoundBookElement

bp = breakpoint

__all__ = ["GoodreadsClient"]


class GoodreadsClient(BaseClient):
    """Goodreads client."""

    BASE_URL = "https://goodreads.com"
    COOKIES_FILE = Config().data_dir / "cookies" / "goodreads.pkl"
    BROWSER_DIR = Config().data_dir / "browser"

    cookie_jar = None

    def __init__(self, **kwargs):
        """Goodreads client.

        Params
        ------
        title (str): title to filter by
        author (str): author to filter by
        series (str): series to filter by
        query (str): submit query and return all results
        save (bool): save response content for debugging
        """
        self.save = kwargs.pop("save", False)

        search_fields = ("query", "title", "author", "series")
        self.query = {
            key: val for key,val in kwargs.items()
            if val and key in search_fields
        }
        for attr in search_fields:
            kwargs.pop(attr, None)

        self.search_by = "all"

        attrs = self.query.keys()
        if len(attrs) == 1 and first(attrs) in ["title", "author"]:
            self.search_by = first(attrs)

        super().__init__(**kwargs)

    def login(self, email, password):
        """Login to goodreads."""
        # if we have valid cookies cached, we're already logged in
        jar = self.cookie_jar = CookieJar(file=self.COOKIES_FILE)
        jar.load()
        if jar.ok("session-token"):
            return True

        browser = self.browser = Browser(user_data_dir=str(self.BROWSER_DIR))

        # go to the user-facing signin page
        browser.get(f"{self.BASE_URL}/user/sign_in")

        # check if the user is already signed in
        # (if they have a session-token cookie and are redirected to the home page)

        jar.cookies = browser.get_cookies()
        if jar.ok("session-token") and browser.current_url == f"{self.BASE_URL}/":
            jar.save(self.session)
            return True

        # click the "Sign in with email" button
        signin_btn = browser.find_xpath("//button[normalize-space(text())='Sign in with email']")
        signin_btn.click()

        #  fill in the form and submit it
        email_field = browser.find_xpath(".//input[@name='email']")
        browser.type_slowly(email_field, email)

        pwd_field = browser.find_xpath(".//input[@name='password']")
        browser.type_slowly(pwd_field, password)

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

        # save the cookies
        jar.cookies = browser.get_cookies()
        jar.save(self.session)

        current_url = browser.current_url
        browser.quit()
        return current_url

    def search(self) -> list:
        """Submit a query to goodreads and return a list of Book objects.

        Examples
        --------
        >>> api = GoodreadsClient(title="ender's game", author="orson scott card")
        >>> api.search()
        [Book('Ender’s Game')]
        """
        query = " ".join(self.query.values())
        response = self.get(
            "https://www.goodreads.com/search",
            params={'q': query, 'search[field]': self.search_by}
        )

        # log(path_url=response.request.path_url)
        log(url=response.url)
        log(
            prefix="Client.search() query:", query=query,
            search_by=self.search_by
        )

        doc = Element(response.text)
        if self.save:
            with open("goodreads-search.html", "w") as fp:
                fp.write(response.text)

        books = []
        for elm in doc.xpath('//tr[@itemtype="http://schema.org/Book"]'):
            found_book = FoundBookElement(elm)
            book = Book(elm, id=found_book.id)
            book.match(self.query)
            books.append(book)

        books = sorted(books, key=lambda b: b.score, reverse=True)
        threshold = 1
        matches = None
        while not matches:
            matches = [b for b in books if b.score >= threshold]
            if threshold <= 0:
                break
            threshold -= 0.15

        books = matches
        return books

    def show(self):
        """Submit a request to show a book by ID and return the details for
        that book."""
