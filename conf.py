import logging
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Listings

class Db():
    """Connects to DB creates a session, then creates
    the required table.
    """

    def __init__(self) -> None:
        db_string = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}"
        self.engine = create_engine(db_string)
        db_session = sessionmaker(bind=self.engine)
        self.session = db_session()
        self._create_db()

    def _create_db(self):
        # create table
        if Listings.metadata.create_all(self.engine):
            logging.info("Database has been created")
        else:
            logging.info("Using current db")


# Values we don't care about if they change
skippable_properties = [
    'id',
    'listing_company',
    'insert_date',
    '_sa_instance_state',
    'floorplan'
]