import pytest
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from seleniumwire.request import Response

from bookdash.browser import Browser

from . import Stub

bp = breakpoint


@pytest.fixture
def browser():
    browser = Browser()
    yield browser
    browser.quit()

def test_browser(browser):
    assert browser

def test_browser_options(browser):
    """
    GIVEN: A browser object.
    WHEN: .options is accessed
    THEN: a webdriver.ChromeOptions object should be returned
    """
    assert isinstance(browser.options, webdriver.ChromeOptions)


def test_browser_driver(browser):
    """
    GIVEN: A browser object.
    WHEN: .driver is accessed
    THEN: a Chrome webdriver should be returned
    """
    assert isinstance(browser.driver, WebDriver)


def test_browser_get(browser, httpserver):
    """
    GIVEN: A browser object.
    WHEN: .request() is called.
    THEN: A response should be returned.
    """
    httpserver.serve_content("success")
    response = browser.get(httpserver.url)

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.body == b"success"


@pytest.mark.parametrize("filecontents", [
    {"filename": "dice.html"},
], indirect=True)
def test_browser_find(browser, httpserver, filecontents):
    """
    GIVEN: A browser object.
    AND: A request has been made that serves HTML content.
    WHEN: .find() is called with a By value, a query string, and a bool value for get_all.
    THEN: Matching element or elements should be returned.
    """
    httpserver.serve_content(filecontents)

    browser.get(httpserver.url)
    elm = browser.find(By.TAG_NAME, "h1")

    assert isinstance(elm, WebElement)
    assert elm.text == "Your dice roll result:"


@pytest.mark.parametrize("filecontents", [
    {"filename": "dice.html"},
], indirect=True)
@pytest.mark.parametrize("params", [
    Stub(by="class_name", query="timestamp", result="January 28, 2021 06:14:10AM"),
    Stub(by="class_name", query="timestamp", result="January 28, 2021 06:14:10AM", get_all=True),
    Stub(by="id", query="no-such-id", result=None, quiet=True),
    Stub(by="css_selector", query="#result", result="5"),
    Stub(by="id", query="result", result="5"),
    Stub(by="link_text", query="Roll it again", result="Roll it again"),
    Stub(by="name", query="roll-link", result="Roll it again"),
    Stub(by="partial_link_text", query="Roll", result="Roll it again"),
    Stub(by="tag_name", query="h2", result="5"),
    Stub(by="xpath", query=".//h2", result="5"),
])
def test_browser_find_methods(params, browser, httpserver, filecontents):
    """
    GIVEN: A browser object.
    AND: A request has been made that serves HTML content.
    WHEN: .find_xpath() is called with a valid xpath.
    THEN: Matching elements should be returned.
    """
    httpserver.serve_content(filecontents)

    browser.get(httpserver.url)

    # get the find method we want to test
    find_method = getattr(browser, f"find_{params.by}")

    # call the method
    results = find_method(params.query, get_all=params.get_all, quiet=params.quiet)

    # if get_all is true, it should return a list of elements
    if params.get_all:
        res_type = list
        elm = results[0]

    # otherwise it should return one element
    else:
        res_type = WebElement
        elm = results

    # if there there are no matching elements and quiet is set to True
    # then None should be returned
    if params.result is None and params.quiet is True:
        assert results is None
        return

    assert isinstance(results, res_type)
    assert isinstance(elm, WebElement)
    assert elm.text == params.result


@pytest.mark.parametrize("filecontents", [
    {"filename": "goodreads-search.html"},
], indirect=True)
def test_browser_type_slowly(browser, httpserver, filecontents, mocker):
    """
    GIVEN: ...
    WHEN: ...
    THEN: ...
    """
    # set delay to zero so that tests aren't (as) slow
    browser.DELAY_RANGE = (0, 0)

    # serve the HTML file
    httpserver.serve_content(filecontents)

    # request the HTML file
    browser.get(httpserver.url)

    # get an input element
    elm = browser.find_class_name("searchBox__input")

    # get a mock spy object for the elm.send_keys() method
    send_keys = mocker.spy(elm, "send_keys")

    # call type_slowly()
    browser.type_slowly(elm, "hello")

    # elm.send_keys() should be called as many times as the keys sent
    assert send_keys.call_count == len("hello")


def test_browser_(browser):
    """
    GIVEN: ...
    WHEN: ...
    THEN: ...
    """
    assert browser
