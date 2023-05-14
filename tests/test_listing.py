from realestate_com_au.objects.listing import *
from tests.api_results import *
import pytest
from conf import skippable_properties

def test_listing() -> None:
    ret = get_listing(json_response)
    assert isinstance(ret, Listing) == True


def test_listers_in_listing() -> None:
    ret = get_listing(json_response)
    assert isinstance(ret.listers[0], Lister) == True


@pytest.mark.parametrize(
    "price_input,expected",
    [("$800,000", 800000), ("$800000", 800000), ("$800k", 800000)],
)
def test_parse_price(price_input, expected):
    assert parse_price_text(price_input) == expected


def test_listing_attr() -> None:
    """Ensure that get_listing returns a listing instance with correct attributes"""
    ret = get_listing(json_response)
    return_value = True
    for k, v in vars(ret).items():
        if k in skippable_properties:
            continue
        if getattr(json_response_listing, k) != v:
            return_value = False

    assert return_value == True
