"""CookieJar module."""

import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from requests import Session

bp = breakpoint


CookieDict = dict[str, str]
"""Dictionary of values for a single cookie."""

CookiesList = list[CookieDict]
"""List of cookies."""

CookiesMapping = dict[str, CookieDict]
"""Collection of cookies mapped by name -> cookie."""

CookiesCollection = Union[CookiesList, CookiesMapping]
"""A list or dict of cookies."""


class CookieJar():
    """CookieJar class."""

    _cookies: CookiesMapping = {}
    file: Path = None

    def __init__(self, cookies: Optional[CookiesCollection]=None, file: Path=None):
        """Construct a cookie jar."""
        self.cookies = cookies
        self.file = file

    def __repr__(self) -> str:
        """Return a string containing the cookie names."""
        names = ", ".join(map(lambda x: repr(x), self.cookies))
        if names:
            names = f" <{names}>"
        return f"CookieJar{names}"

    def get(self, name: str) -> CookieDict:
        """Get a cookie by name."""
        return self.cookies.get(name)

    @property
    def cookies(self) -> CookiesMapping:
        """Get cookies."""
        return self._cookies

    @cookies.setter
    def cookies(self, cookies: CookiesCollection) -> CookiesMapping:
        """Set cookies cast to a CookiesMapping."""
        if isinstance(cookies, list):
            cookies = {c["name"]: c for c in cookies}
        self._cookies = cookies
        return self._cookies

    def expired(self) -> bool:
        """Return True if any cookies are expired."""
        if not self.cookies:
            return False
        now = datetime.today().timestamp()
        expired = list(filter(
            lambda c: now >= c.get("expiry", now + 1),
            self.cookies.values())
        )
        return bool(expired)

    def has(self, *names) -> bool:
        """Return True if cookies for all names exist."""
        if not self.cookies:
            return False
        have = [name in self.cookies for name in names]
        return all(have)

    def for_session(self, session: Session) -> CookiesList:
        """Prepare cookies and add to session."""

        session_cookies = []
        for cookie in self.cookies.values():
            cookie.pop("sameSite", None)

            if "httpOnly" in cookie:
                cookie["rest"] = {"httpOnly": cookie.pop("httpOnly")}
            if "expiry" in cookie:
                cookie["expires"] = cookie.pop("expiry")

            session_cookies.append(cookie)
            session.cookies.set(**cookie)

        return session_cookies

    def load(self) -> CookiesMapping:
        """Load cookies from file."""
        # make sure the file is there
        if not self.file.is_file():
            return False

        # load the cookies from the file
        with open(self.file, "rb") as f:
            result = pickle.load(f)
            cookies = result

        self.cookies = cookies
        return cookies

    def save(self, session: Session=None) -> None:
        """Save cookies to pickled file and optionally add to session."""
        # create cookie directory if missing
        self.file.parent.mkdir(parents=True, exist_ok=True)

        # save the cookies file
        with open(self.file, "wb") as f:
            pickle.dump(self.cookies, f, pickle.HIGHEST_PROTOCOL)

        if session:
            self.for_session(session)

    def ok(self, *names) -> bool:
        """Return True if no cookies are expired and the required cookies are
        present."""
        return (not self.expired()) and (self.has(*names))
