"""
Provides linkedin api-related code
"""
import logging
from urllib.parse import urlencode
import json
from .graphql import searchBuy, searchRent, searchSold
from .objects.listing import get_listing
from .fajita import Fajita

logger = logging.getLogger(__name__)

def get_query(channel):
    if channel == "buy":
        return searchBuy.QUERY

    if channel == "sold":
        return searchSold.QUERY

    return searchRent.QUERY


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
    _MAX_SEARCH_PAGE_SIZE = 100
    _DEFAULT_SEARCH_PAGE_SIZE = 25

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

    def get_query_variables(
        self,
        limit,
        channel,
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
        page=1,
    ):
        query_variables = {
            "channel": channel,
            "page": page,
            "sortType": sortType,
            "pageSize": (
                min(limit, self._MAX_SEARCH_PAGE_SIZE)
                if limit
                else self._DEFAULT_SEARCH_PAGE_SIZE
            ),
            "localities": [{"searchLocation": location} for location in locations],
            "filters": {
                "surroundingSuburbs": surrounding_suburbs,
                "excludeNoSalePrice": exclude_no_sale_price,
                "ex-under-contract": ex_under_contract,
                "furnished": furnished,
                "petsAllowed": pets_allowed,
            },
        }
        if (max_price is not None and max_price > -1) or (
            max_price is not None and min_price > 0
        ):
            price_filter = {}
            if max_price > -1:
                price_filter["maximum"] = str(max_price)
            if min_price > 0:
                price_filter["minimum"] = str(min_price)
            query_variables["filters"]["priceRange"] = price_filter
        if (max_bedrooms is not None and max_bedrooms > -1) or (
            max_bedrooms is not None and min_bedrooms > 0
        ):
            beds_filter = {}
            if max_bedrooms > -1:
                beds_filter["maximum"] = str(max_bedrooms)
            if min_bedrooms > 0:
                beds_filter["minimum"] = str(min_bedrooms)
            query_variables["filters"]["bedroomsRange"] = beds_filter
        if property_types:
            query_variables["filters"]["propertyTypes"] = property_types
        if min_bathrooms is not None and min_bathrooms > 0:
            query_variables["filters"]["minimumBathroom"] = str(min_bathrooms)
        if min_carspaces is not None and min_carspaces > 0:
            query_variables["filters"]["minimumCars"] = str(min_carspaces)
        if min_land_size is not None and min_land_size > 0:
            query_variables["filters"]["landSize"] = {"minimum": str(min_land_size)}
        if construction_status:
            query_variables["filters"]["constructionStatus"] = construction_status
        if keywords:
            query_variables["filters"]["keywords"] = {"terms": keywords}
        if channel == "sold" and sortType:
            query_variables["sortType"] = sortType
        return query_variables

    def get_payload(self, query_variables, channel):
        payload = {
            "operationName": "searchByQuery",
            "variables": {
                "query": json.dumps(query_variables),
                "testListings": False,
                "nullifyOptionals": False,
            },
            "query": get_query(channel),
        }

        if channel == "rent":
            payload["variables"]["smartHide"] = False
            payload["variables"]["recentHides"] = []

        return payload

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

    def get_current_page(self, **kwargs):
        current_query_variables = json.loads(kwargs["json"]["variables"]["query"])
        return current_query_variables["page"]

    def next_page(self, 
                limit,
                channel,
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
                **kwargs):
        current_page = self.get_current_page(**kwargs)
        kwargs["json"] = self.get_payload(
            self.get_query_variables(
                limit,
                channel,
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
                page = current_page + 1,
                ),
            channel=channel
            )
        return kwargs

    def is_done(self, items, res, limit, channel, **kwargs):
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

        listings = self._scroll(
            "",
            "POST",
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
            parse_items = self.parse_items,
            next_page_fn = self.next_page,
            done_fn = self.is_done,
            json=self.get_payload(
                channel = channel,
                query_variables = self.get_query_variables(
                    limit,
                    channel,
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
                    page=1,
                )
            ),
            limit=limit,
            channel=channel,
        )

        return listings
