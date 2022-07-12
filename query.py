import json
import os
import datetime
import sys
from conf import Db, skippable_properties
from models import Listings

database = Db()

def in_dictlist(key: str, value: str, my_dictlist: dict):
    """Searches through dict if it has matching key value

    Args:
        key (str): key to match
        value (str): value to match
        my_dictlist (dict): dict to be passed through

    Returns:
        dict: Returns empty dict if not found otherwise returns value
    """
    for entry in my_dictlist:
        if entry.get(key) == value:
            return entry
    return {}



def main(days: int = 1):
    """Prints out the changes between now - 'days'
    to stdout.

    EG:

    "url": "https://www.realestate.com.au/property-house-vic-patterson+lakes-xxxxxxxxx",
    "history": [
        {
            "price_text": "$2,100,000 - $2,250,000",
            "date": "11PM Sat 21 Jan",
            "original_val": "$2,150,000-$2,350,000"
        },
    ]

    Args:
        days (int, optional): How many days of changes to query. Defaults to 1.
    """

    results = database.session.query(Listings).order_by(
        Listings.listing_id).distinct(Listings.listing_id).all()

    for listing in results:
        
        indiviual_changes = []

        listing_id_results = database.session.query(Listings).order_by(
            Listings.insert_date).filter(Listings.listing_id == listing.listing_id).all()

        first_listing_occurence = listing_id_results[0]

        listing_history = {
            'url': first_listing_occurence.url,
            'history': [],
        }

        for listing_id in listing_id_results:

            for key, val in listing_id.__dict__.items():

                if key in skippable_properties:
                    continue

                if val != getattr(first_listing_occurence, key):
                    if not indiviual_changes:
                        if listing_history.get(key, "") != val:
                            time_delta = datetime.datetime.today() - listing_id.insert_date
                            indiviual_changes.append({
                                key: val,
                                "date": listing_id.insert_date,
                                "original_val": getattr(first_listing_occurence, key)
                            })

                    for change in indiviual_changes:
                        if change.get(key) == val:
                            continue
                        elif in_dictlist(key, val, indiviual_changes):
                            continue
                        else:
                            time_delta = datetime.datetime.today() - listing_id.insert_date
                            indiviual_changes.append({
                                key: val,
                                "date": listing_id.insert_date,
                                "original_val": getattr(first_listing_occurence, key)
                            })

        listing_history['history'] = indiviual_changes

        if listing_history['history']:
            tmp_dict = listing_history['history'].copy()
            for listing in listing_history['history']:
                time_delta = datetime.datetime.today() - listing['date']

                if time_delta.days <= days and time_delta.days >= 0:
                    listing['date'] = listing['date'].strftime("%-I%p %a %-d %b")
                else:
                    tmp_dict.remove(listing)

            listing_history['history'] = tmp_dict

            if listing_history['history']:
                print("\n")
                print(json.dumps(listing_history, indent=4))


if len(sys.argv) > 1:
    days = int(sys.argv[1])
    main(days=days)
else:
    main()