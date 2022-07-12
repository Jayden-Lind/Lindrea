from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Listings
import json
import os

def in_dictlist(key, value, my_dictlist):
    for entry in my_dictlist:
        if entry.get(key) == value:
            return entry
    return {}

db_string = f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_SCHEMA')}"

engine = create_engine(db_string)

Session = sessionmaker(bind=engine)

session = Session()

results = session.query(Listings).order_by(Listings.listing_id).distinct(Listings.listing_id).all()


for listing in results:
    listing_id_results = session.query(Listings).order_by(Listings.insert_date).filter(Listings.listing_id == listing.listing_id).all()
    first_listing_occurence = listing_id_results[0]
    
    listing_history = {'url' : first_listing_occurence.url, 'history' : [], }
    indiviual_changes = []
    for listing_id in listing_id_results:
        
        for key,val in listing_id.__dict__.items():
            if key == 'id':
                continue
            if key == 'listing_company':
                continue
            if key == 'insert_date':
                continue
            if key == '_sa_instance_state':
                continue
            if val != getattr(first_listing_occurence, key):
                if indiviual_changes == []:
                    if listing_history.get(key) != val:
                        indiviual_changes.append({key : val, "date" : listing_id.insert_date.strftime("%-I%p %a %-d %b"), "original_val" : getattr(first_listing_occurence, key)})
                for change in indiviual_changes:
                    if change.get(key) == val:
                        continue
                    elif in_dictlist(key, val, indiviual_changes):
                        continue
                    else:
                        indiviual_changes.append({key : val, "date" : listing_id.insert_date.strftime("%-I%p %a %-d %b"), "original_val" : getattr(first_listing_occurence, key)})
    
    listing_history['history'] = indiviual_changes
    
    if listing_history['history'] != []:
        print("\n")
        print(json.dumps(listing_history, indent=4))
