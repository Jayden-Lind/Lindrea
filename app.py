import logging
from models import Listings
from realestate_com_au.realestate_com_au import RealestateComAu
from realestate_com_au.objects.listing import Listing
from conf import Db, skippable_properties

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)

def insert_into_db(listing: Listings, db_conn: Db):
    """Instantiates a sqlalchemy model to be inserted into the db_conn supplied

    Args:
        listing (Listings): _description_
        db_conn (db): Active DB connection to insert listing into
    """
    kwargs = {}
    # transpose into dict to be created into Listings class
    for k, v in vars(listing).items():
        kwargs[k] = v
    kwargs["listing_id"] = kwargs["id"]
    kwargs["id"] = None

    db_conn.session.add(Listings(**kwargs))
    db_conn.session.commit()

def find_changes_listing(graphql_property: Listing, property_db_results: list, skippable_properties: list):
    """_summary_

    Args:
        property (Listing): _description_
        property_db_results (list): _description_

    Returns:
        _type_: _description_
    """

    add_to_db = False

    if len(property_db_results) == 0:
        add_to_db = True
        logging.info("Adding to DB: %s is a new property", graphql_property.url)

    if len(property_db_results) > 0:

        latest_listing = property_db_results[-1]

        for k, v in vars(latest_listing).items():
            if k in skippable_properties:
                continue
            if k == "listing_id":
                k = "id"
            if k == "land_size" and isinstance(v, int):
                v = str(v)
            # If value is different, insert
            if v != getattr(graphql_property, k):
                logging.info(
                    "Adding to DB: %s has a new addition", graphql_property.url
                )
                add_to_db = True

    return add_to_db

def main():
    database = Db()

    api = RealestateComAu()

    realestate_com_au_listings = api.search(
    locations=[
        "Chelsea Heights, 3196",
        "Aspendale Gardens, 3195",
        "Patterson Lakes, 3197",
    ],
    channel="buy",
    surrounding_suburbs=False,
    sortType="new-desc",
    )

    for graphql_property_listing in realestate_com_au_listings:
        listing_db_query_results = (
            database.session.query(Listings)
            .order_by(Listings.insert_date)
            .filter(Listings.listing_id == graphql_property_listing.id)
            .all()
        )

        if find_changes_listing(graphql_property_listing, listing_db_query_results, skippable_properties):
            insert_into_db(graphql_property_listing, database)

if __name__ == "__main__":
    main()