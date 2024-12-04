import requests


def make_request(url):
    """Make a web request and return the text content."""
    response = requests.get(url)
    return response.text
