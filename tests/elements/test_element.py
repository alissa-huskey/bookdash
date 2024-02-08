import lxml.html
import pytest

from bookdash.elements.element import Element

from .. import filecontents


@pytest.mark.parametrize("filecontents", [
    {'filename': "dice.html"}
], indirect=True)
def test_element_init_str(filecontents):
    doc = Element(filecontents)
    assert isinstance(doc.element, lxml.html.HtmlElement)


@pytest.mark.parametrize("filecontents", [
    {'filename': "dice.html"}
], indirect=True)
def test_element_init_elm(filecontents):
    doc = Element(filecontents)
    assert isinstance(doc.element, lxml.html.HtmlElement)


@pytest.mark.parametrize("filecontents", [
    {'filename': "dice.html"}
], indirect=True)
def test_element_xpath(filecontents):
    doc = Element(filecontents)
    assert doc.xpath("//h2/text()") == ["5"]


@pytest.mark.parametrize("filecontents", [
    {'filename': "dice.html"}
], indirect=True)
def test_element_first(filecontents):
    doc = Element(filecontents)
    assert doc.first("//h2/text()") == "5"


@pytest.mark.parametrize("filecontents", [
    {'filename': "dice.html"}
], indirect=True)
def test_element_attr(filecontents):
    doc = Element(filecontents)
    assert doc.attr("//h2", "id") == "result"
