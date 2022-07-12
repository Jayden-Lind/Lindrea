
import random
import logging
import requests
from time import sleep

logger = logging.getLogger(__name__)


def default_evade():
    """
    A catch-all method to try and evade suspension.
    Currenly, just delays the request by a random (bounded) time
    """
    sleep(random.randint(0, 1))  # sleep a random duration to try and evade suspention


logger = logging.getLogger(__name__)

class Client(object):
    def __init__(
        self,
        *,
        debug=False,
        headers={},
        proxies={},
        authenticate_fn=None
    ):
        self.session = requests.session()
        self.logger = logger
        self._authenticate = authenticate_fn
        self.session.proxies.update(proxies)
        self.session.headers.update(headers)

        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)


class Fajita(object):
    """
    Extend this to build your wrapper
    """

    def __init__(
        self,
        base_url=None,
        headers={},
        proxies={},
        debug=False
    ):
        self._client = Client(
            headers=headers,
            debug=debug,
            proxies=proxies
        )
        self._logger = logger
        self._base_url = base_url
        self._fresh = True  # False if the instance has been used

        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)

    def _get(self, uri, base_url=None, evade=default_evade, **kwargs):
        """
        GET request to Linkedin API
        """
        if not self._fresh:
            evade()
        self._fresh = False

        url = f"{base_url or self._base_url}{uri}"
        return self._client.session.get(url, **kwargs)

    def _post(self, uri, base_url=None, evade=default_evade, **kwargs):
        """
        POST request to Linkedin API
        """
        if not self._fresh:
            evade()
        self._fresh = False

        url = f"{base_url or self._base_url}{uri}"
        return self._client.session.post(url, **kwargs)

    def _scroll(
        self, uri, method, parse_items, next_page_fn, done_fn, items=[], **kwargs
    ):
        res = None
        if method == "GET":
            res = self._get(uri, **kwargs)
        elif method == "POST":
            res = self._post(uri, **kwargs)
        items = items + parse_items(res)

        if done_fn(items, res, **kwargs):
            return items

        new_kwargs = next_page_fn(**kwargs)
        return self._scroll(
            uri, method, parse_items, next_page_fn, done_fn, items=items, **new_kwargs
        )

