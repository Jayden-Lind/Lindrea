"""
Provides linkedin api-related code
"""
import logging
from urllib.parse import urlencode
import json
from .graphql import searchBuy, searchRent, searchSold
from .objects.listing import get_listing
from .fajita import Fajita
from dataclasses import dataclass

logger = logging.getLogger(__name__)


def get_query(channel):
    if channel == "buy":
        return searchBuy.QUERY

    if channel == "sold":
        return searchSold.QUERY

    return searchRent.QUERY


@dataclass
class SearchVariables:
    locations: list[str]
    keywords: list[str]
    property_types: list[
        str
    ]  # "unit apartment", "townhouse", "villa", "land", "acreage", "retire", "unitblock",
    page: int = 1
    limit: int = -1
    channel: str = "buy"
    surrounding_suburbs: bool = True
    exclude_no_sale_price: bool = False
    furnished: bool = False
    pets_allowed: bool = False
    ex_under_contract: bool = False
    min_price: int = 0
    max_price: int = -1
    min_bedrooms: int = 0
    max_bedrooms: int = -1
    min_bathrooms: int = 0
    min_carspaces: int = 0
    min_land_size: int = 0
    construction_status: str = None  # NEW, ESTABLISHED
    sortType: str = "new-desc"

    _MAX_SEARCH_PAGE_SIZE = 100
    _DEFAULT_SEARCH_PAGE_SIZE = 25

    def get_query_variables(
        self,
    ) -> dict:
        query_variables = {
            "channel": self.channel,
            "page": self.page,
            "sortType": self.sortType,
            "pageSize": (
                min(self.limit, self._MAX_SEARCH_PAGE_SIZE)
                if self.limit
                else self._DEFAULT_SEARCH_PAGE_SIZE
            ),
            "localities": [{"searchLocation": location} for location in self.locations],
            "filters": {
                "surroundingSuburbs": self.surrounding_suburbs,
                "excludeNoSalePrice": self.exclude_no_sale_price,
                "ex-under-contract": self.ex_under_contract,
                "furnished": self.furnished,
                "petsAllowed": self.pets_allowed,
            },
        }
        if (self.max_price is not None and self.max_price > -1) or (
            self.max_price is not None and self.min_price > 0
        ):
            price_filter = {}
            if self.max_price > -1:
                price_filter["maximum"] = str(self.max_price)
            if self.min_price > 0:
                price_filter["minimum"] = str(self.min_price)
            query_variables["filters"]["priceRange"] = price_filter
        if (self.max_bedrooms is not None and self.max_bedrooms > -1) or (
            self.max_bedrooms is not None and self.min_bedrooms > 0
        ):
            beds_filter = {}
            if self.max_bedrooms > -1:
                beds_filter["maximum"] = str(self.max_bedrooms)
            if self.min_bedrooms > 0:
                beds_filter["minimum"] = str(self.min_bedrooms)
            query_variables["filters"]["bedroomsRange"] = beds_filter
        if self.property_types:
            query_variables["filters"]["propertyTypes"] = self.property_types
        if self.min_bathrooms is not None and self.min_bathrooms > 0:
            query_variables["filters"]["minimumBathroom"] = str(self.min_bathrooms)
        if self.min_carspaces is not None and self.min_carspaces > 0:
            query_variables["filters"]["minimumCars"] = str(self.min_carspaces)
        if self.min_land_size is not None and self.min_land_size > 0:
            query_variables["filters"]["landSize"] = {
                "minimum": str(self.min_land_size)
            }
        if self.construction_status:
            query_variables["filters"]["constructionStatus"] = self.construction_status
        if self.keywords:
            query_variables["filters"]["keywords"] = {"terms": self.keywords}
        if self.channel == "sold" and self.sortType:
            query_variables["sortType"] = self.sortType
        return query_variables

    def get_payload(self) -> dict:
        payload = {
            "operationName": "searchByQuery",
            "variables": {
                "query": json.dumps(self.get_query_variables()),
                "testListings": False,
                "nullifyOptionals": False,
            },
            "query": get_query(self.channel),
        }

        if self.channel == "rent":
            payload["variables"]["smartHide"] = False
            payload["variables"]["recentHides"] = []

        return payload


class RealestateComAu(Fajita):
    """
    Class for accessing realestate.com.au API.
    """

    API_BASE_URL = "https://lexa.realestate.com.au/graphql"
    REQUEST_HEADERS = {
        "content-type": "application/json",
        "origin": "https://www.realestate.com.au",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }

    def __init__(
        self,
        proxies={},
        debug=False,
    ):
        Fajita.__init__(
            self,
            base_url=self.API_BASE_URL,
            headers=self.REQUEST_HEADERS,
            proxies=proxies,
            debug=debug,
        )
        logging.basicConfig(level=logging.DEBUG if debug else logging.INFO)
        self.logger = logger

    def parse_items(self, res, channel):
        data = res.json()
        results = data.get("data", {}).get(f"{channel}Search", {}).get("results", {})

        exact_listings = (results.get("exact", {}) or {}).get("items", [])
        surrounding_listings = (results.get("surrounding", {}) or {}).get("items", [])

        listings = [
            get_listing(listing.get("listing", {}) or {})
            for listing in exact_listings + surrounding_listings
        ]

        return listings

    def next_page(self, search_object: SearchVariables, **kwargs):
        kwargs["json"] = search_object.get_payload()
        return kwargs

    def is_done(self, items: list, res, limit: int, channel: str, **kwargs):
        if not items:
            return True
        items_count = len(items)
        if limit > -1:
            if items_count >= limit:
                return True

        data = res.json()
        results = data.get("data", {}).get(f"{channel}Search", {}).get("results", {})
        total = results.get("totalResultsCount")

        if items_count >= total:
            return True

        pagination = results.get("pagination")

        # failsafe
        if not pagination.get("moreResultsAvailable"):
            return False

        return False

    def search(
        self,
        limit=-1,
        channel="buy",
        locations=[],
        surrounding_suburbs=True,
        exclude_no_sale_price=False,
        furnished=False,
        pets_allowed=False,
        ex_under_contract=False,
        min_price=0,
        max_price=-1,
        min_bedrooms=0,
        max_bedrooms=-1,
        property_types=[],  # "unit apartment", "townhouse", "villa", "land", "acreage", "retire", "unitblock",
        min_bathrooms=0,
        min_carspaces=0,
        min_land_size=0,
        construction_status=None,  # NEW, ESTABLISHED
        keywords=[],
        sortType="sold-price-desc",
    ):
        search = SearchVariables(
            limit=limit,
            channel=channel,
            locations=locations,
            surrounding_suburbs=surrounding_suburbs,
            exclude_no_sale_price=exclude_no_sale_price,
            furnished=furnished,
            pets_allowed=pets_allowed,
            ex_under_contract=ex_under_contract,
            min_price=min_price,
            max_price=max_price,
            min_bedrooms=min_bedrooms,
            max_bedrooms=max_bedrooms,
            property_types=property_types,
            min_bathrooms=min_bathrooms,
            min_carspaces=min_carspaces,
            min_land_size=min_land_size,
            construction_status=construction_status,
            keywords=keywords,
            sortType=sortType,
        )
        listings = self._scroll(
            "",
            "POST",
            parse_items=self.parse_items,
            next_page_fn=self.next_page,
            done_fn=self.is_done,
            json=search.get_payload(),
            search_object=search,
        )

        return listings
