from unittest.mock import MagicMock
import pytest
from pytest import MonkeyPatch
from realestate_com_au.realestate_com_au import RealestateComAu, get_query
from realestate_com_au.graphql import searchBuy, searchRent, searchSold
from tests.api_results import *

api = RealestateComAu()


def test_search_api() -> None:
    api.search(
        locations=[
            "Chelsea Heights, 3196",
        ],
        channel="buy",
        surrounding_suburbs=False,
        sortType="new-desc",
    )


def test_get_query_buy() -> None:
    assert get_query("buy") == searchBuy.QUERY


def test_get_query_sold() -> None:
    assert get_query("sold") == searchSold.QUERY


def test_get_query_rent() -> None:
    assert get_query("rent") == searchRent.QUERY


def test_get_payload_buy() -> None:
    json_payload = api.get_payload(
        api.get_query_variables(
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
        ),
        channel="buy",
    )
    assert json_payload == good_json_payload
