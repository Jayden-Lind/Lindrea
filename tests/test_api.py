
from realestate_com_au.realestate_com_au import RealestateComAu, get_query, SearchVariables
from realestate_com_au.graphql import searchBuy, searchRent, searchSold
from tests.api_results import *
import pytest

api = RealestateComAu()

class response_object():
    def json(self):
        ret = {
        "data" : {
            "buySearch" : {
                "results" : {
                    "totalResultsCount" : 1
                    }
                }
            }
        }
        return ret

def test_search_api() -> None:
    results = api.search(
        locations=[
            "Chelsea Heights, 3196",
            "Aspendale Gardens, 3195",
            "Patterson Lakes, 3197",
        ],
        channel="buy",
        surrounding_suburbs=False,
        sortType="new-desc",
    )
    assert len(results) > 0


def test_get_query_buy() -> None:
    assert get_query("buy") == searchBuy.QUERY


def test_get_query_sold() -> None:
    assert get_query("sold") == searchSold.QUERY


def test_get_query_rent() -> None:
    assert get_query("rent") == searchRent.QUERY


def test_get_payload_buy() -> None:
    search = SearchVariables(
        locations=[
            "Chelsea Heights, 3196",
            "Aspendale Gardens, 3195",
            "Patterson Lakes, 3197",
        ],
        surrounding_suburbs=False,
        exclude_no_sale_price=False,
        furnished=False,
        pets_allowed=False,
        ex_under_contract=False,
        min_price=0,
        max_price=-1,
        min_bedrooms=0,
        max_bedrooms=-1,
        property_types=[],
        min_bathrooms=0,
        min_carspaces=0,
        min_land_size=0,
        construction_status=None,
        keywords=[],
        sortType="new-desc",
        channel="buy",
        limit=-1,
    )
    json_payload = search.get_payload()
    assert json_payload == good_json_payload


def test_is_done() -> None:
    res = response_object()
    assert api.is_done([good_listing], res, -1, "buy") == True