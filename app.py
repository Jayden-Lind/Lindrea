import logging
from models import Listings
from realestate_com_au import realestate_com_au
from conf import Db, skippable_properties

api = realestate_com_au.RealestateComAu()

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True,
    )

def insert_into_db(listing, db_conn):
    """Instantiates a sqlalchemy model to be inserted into the db_conn supplied

    Args:
        listing (Listings): _description_
        db_conn (db): Active DB connection to insert listing into
    """
    kwargs = {}
    # transpose into dict to be created into Listing class
    for k, v in vars(listing).items():
        kwargs[k] = v
    kwargs['listing_id'] = kwargs['id']
    kwargs['id'] = None

    db_conn.session.add(Listings(**kwargs))
    db_conn.session.commit()


database = Db()

realestate_com_au_listings = api.search(
    locations=[
        "Chelsea Heights, 3196",
        "Aspendale Gardens, 3195",
        "Patterson Lakes, 3197"
    ],
    channel="buy",
    surrounding_suburbs=False,
    sortType="new-desc"
)

for graphql_property_listing in realestate_com_au_listings:
    ADD_TO_DB = False

    listing_db_query_results = database.session.query(Listings).order_by(
        Listings.insert_date).filter(Listings.listing_id == graphql_property_listing.id).all()

    if len(listing_db_query_results) == 0:
        ADD_TO_DB = True
        logging.info("Adding to DB: %s is a new property",
                     graphql_property_listing.url)

    if len(listing_db_query_results) > 0:

        latest_listing = listing_db_query_results[-1]

        for k, v in vars(latest_listing).items():
            if k in skippable_properties:
                continue
            if k == 'listing_id':
                k = 'id'
            if k == 'land_size' and isinstance(v, int):
                v = str(v)
            # If value is different, insert
            if v != getattr(graphql_property_listing, k):
                logging.info("Adding to DB: %s has a new addition",
                             graphql_property_listing.url)
                ADD_TO_DB = True

    if ADD_TO_DB:
        insert_into_db(graphql_property_listing, database)
