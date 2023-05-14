from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, PickleType


Base = declarative_base()


class Listings(Base):
    __tablename__ = 'listings'
    id = Column(Integer, primary_key=True)
    listing_id = Column(String)
    url = Column(String)
    suburb = Column(String)
    state = Column(String)
    postcode = Column(String)
    short_address = Column(String)
    full_address = Column(String)
    property_type = Column(String)
    price = Column(Integer)
    price_text = Column(String)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    parking_spaces = Column(Integer)
    building_size = Column(String)
    building_size_unit = Column(String)
    land_size = Column(String)
    land_size_unit = Column(String)
    listing_company = Column(PickleType)
    auction_date = Column(String)
    sold_date = Column(String)
    description = Column(String)
    statement_of_information = Column(String)
    floorplan = Column(String)
    insert_date = Column(DateTime)

    def __init__(self, **kwargs):
        self.insert_date = datetime.now()
        self.__dict__.update(kwargs)
        self.listers = None
