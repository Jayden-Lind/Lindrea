import logging
import os
from models import Listings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from realestate_com_au import realestate_com_au

api = realestate_com_au.RealestateComAu()

logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True,
    )


class Db():
    """Connects to DB creates a session, then creates
    the required table.
    """

    def __init__(self) -> None:
        db_string = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_SCHEMA')}"
        engine = create_engine(db_string)
        db_session = sessionmaker(bind=engine)
        self.session = db_session()
        # create table
        if Listings.metadata.create_all(engine):
            logging.info("Database has been created")
        else:
            logging.info("Using current db")


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
        "Caulfield East, VIC 3145",
        "Caulfield South, VIC 3162",
        "Caulfield, VIC 3162",
        "Caulfield North, VIC 3161",
        "Ormond, VIC 3204",
        "Moorabbin, VIC 3189",
        "Carnegie, VIC 3163",
        "Murrumbeena, VIC 3163",
        "Hampton East, VIC 3188",
        "Hampton, VIC 3188",
        "Brighton East, VIC 3187",
        "Brighton, VIC 3186",
        "Bentleigh, VIC 3204",
        "Bentleigh East, VIC 3165",
        "Hughesdale, VIC 3166",
        "Highett, VIC 3190",
        "Sandringham, VIC 3191",
        "Mckinnon, VIC 3204",
        "Cheltenham, VIC 3192"
    ],
    channel="buy",
    surrounding_suburbs=False,
    sortType="new-desc",
    property_types=["townhouse", "house", "unit apartment"],
    max_price=1200000,
    min_price=800000,
)


# Values we don't care about if they change
skippable_properties = [
    'id',
    'listing_company',
    'insert_date',
    '_sa_instance_state'
]

for graphql_property_listing in realestate_com_au_listings:
    add_to_db = False

    listing_db_query_results = database.session.query(Listings).order_by(
        Listings.insert_date).filter(Listings.listing_id == graphql_property_listing.id).all()

    if len(listing_db_query_results) == 0:
        add_to_db = True
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
                add_to_db = True

    if add_to_db:
        insert_into_db(graphql_property_listing, database)
