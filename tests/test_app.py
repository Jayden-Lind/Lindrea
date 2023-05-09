from tests.api_results import *
from unittest.mock import MagicMock
from models import Listings
from app import find_changes_listing, insert_into_db
from conf import skippable_properties
import pytest

class DbMock():
    session = MagicMock()

@pytest.fixture
def listing() -> Listing:
    return good_listing

@pytest.fixture
def listing_db_results() -> Listings:
    kwargs = {}
    # transpose into dict to be created into Listings class
    for k, v in vars(good_listing).items():
        kwargs[k] = v
    kwargs["listing_id"] = kwargs["id"]
    kwargs["id"] = None
    return Listings(**kwargs)


def test_find_no_changes(listing, listing_db_results) -> None:
    """Should find 0 changes in the listing"""
    assert (
        find_changes_listing(listing, [listing_db_results], skippable_properties)
        is False
    )


def test_find_changes(listing, listing_db_results) -> None:
    """Should find 1 change in the listing"""
    listing.suburb = "Chelsea Heights"
    assert (
        find_changes_listing(listing, [listing_db_results], skippable_properties)
        is True
    )

def test_insert_into_db(listing) -> None:
    tmp = insert_into_db(listing, DbMock)
