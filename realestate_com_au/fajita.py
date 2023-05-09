
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
    sleep(random.randint(0, 1)) 


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
        self, uri, method, parse_items, next_page_fn, done_fn, limit, channel,
        locations,
        surrounding_suburbs,
        exclude_no_sale_price,
        furnished,
        pets_allowed,
        ex_under_contract,
        min_price,
        max_price,
        min_bedrooms,
        max_bedrooms,
        property_types,
        min_bathrooms,
        min_carspaces,
        min_land_size,
        construction_status,
        keywords,
        sortType,
        items=[],
        **kwargs
    ):
        res = None
        if method == "GET":
            res = self._get(uri, **kwargs)
        elif method == "POST":
            res = self._post(uri, **kwargs)
        items = items + parse_items(res, channel)

        if done_fn(items, res, limit, channel, **kwargs):
            return items

        new_kwargs = next_page_fn(limit,
        channel=channel,
        locations = locations,
        surrounding_suburbs = surrounding_suburbs,
        exclude_no_sale_price = exclude_no_sale_price,
        furnished = furnished,
        pets_allowed = pets_allowed,
        ex_under_contract = ex_under_contract,
        min_price = min_price,
        max_price = max_price,
        min_bedrooms = min_bedrooms,
        max_bedrooms = max_bedrooms,
        property_types = property_types,
        min_bathrooms = min_bathrooms,
        min_carspaces = min_carspaces,
        min_land_size = min_land_size,
        construction_status = construction_status,
        keywords = keywords,
        sortType = sortType,
        **kwargs
        )
        return self._scroll(
            uri, method, parse_items, next_page_fn, done_fn, limit, channel,
            locations = locations,
            surrounding_suburbs = surrounding_suburbs,
            exclude_no_sale_price = exclude_no_sale_price,
            furnished = furnished,
            pets_allowed = pets_allowed,
            ex_under_contract = ex_under_contract,
            min_price = min_price,
            max_price = max_price,
            min_bedrooms = min_bedrooms,
            max_bedrooms = max_bedrooms,
            property_types = property_types,
            min_bathrooms = min_bathrooms,
            min_carspaces = min_carspaces,
            min_land_size = min_land_size,
            construction_status = construction_status,
            keywords = keywords,
            sortType = sortType,
            items=items,
            **new_kwargs
        )

