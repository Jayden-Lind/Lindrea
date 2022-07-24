from datetime import date, datetime
from realestate_com_au import realestate_com_au
api = realestate_com_au.RealestateComAu()
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from models import Listings
import os

class db():
    def __init__(self) -> None:
        db_string = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_SCHEMA')}"
        engine = create_engine(db_string)
        Base = declarative_base()
        Session = sessionmaker(bind=engine)
        self.session = Session()
        #create table
        Base.metadata.create_all(engine)

database = db()

realestate_com_au_listings = api.search(
    locations=["Chelsea Heights, 3196", "Aspendale Gardens, 3195", "Patterson Lakes, 3197"],
    channel="buy",
    surrounding_suburbs=False,
    sortType="new-desc"
)

for listing in realestate_com_au_listings:
    add_to_db = False
    #Check if listing has changed before inserting
    listing_id_results = database.session.query(Listings).order_by(Listings.insert_date).filter(Listings.listing_id == listing.id).all()
    if len(listing_id_results) == 0:
        add_to_db  = True
        print(f"${listing.url} is a new property!!!" )
    else:
        skippable_properties = [
            'id',
            'listing_company',
            'insert_date',
            '_sa_instance_state'
        ]
        latest_listing = listing_id_results[-1]
        for property, value in vars(latest_listing).items():
            if property in skippable_properties:
                continue
            if property == 'listing_id':
                property = 'id'
            if property == 'land_size' and type(value) == int:
                value = str(value)
            if value != getattr(listing, property):
                add_to_db = True
    if add_to_db:
        kwargs = {}
        for property, value in vars(listing).items():
            kwargs[property] = value
        kwargs['listing_id'] = kwargs['id']
        kwargs['id'] = None
        print(f"{listing.id} is being added!!!")
        database.session.add(Listings(**kwargs))
        database.session.commit()
