from datetime import date, datetime
from realestate_com_au import realestate_com_au
api = realestate_com_au.RealestateComAu()
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from models import Listings
import os

db_string = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_SCHEMA')}"

engine = create_engine(db_string, echo=True)


Base = declarative_base()

Session = sessionmaker(bind=engine)

session = Session()

#create table
Base.metadata.create_all(engine)

realestate_com_au_listings = api.search(
    locations=["Chelsea Heights, 3196", "Aspendale Gardens, 3195", "Patterson Lakes, 3197"],
    channel="buy",
    surrounding_suburbs=False,
    sortType="new-desc"
)

for listing in realestate_com_au_listings:
    kwargs = {}
    for property, value in vars(listing).items():
        kwargs[property] = value
    kwargs['listing_id'] = kwargs['id']
    kwargs['id'] = None
    print(listing.id)
    session.add(Listings(**kwargs))
    session.commit()
