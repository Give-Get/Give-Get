"""
handles all database interaction
"""

from pymongo import MongoClient
from math import radians, sin, cos, sqrt, atan2
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
geolocator = Nominatim(user_agent="my-geocoder")


MONGO_URI = "mongodb+srv://praj:praj@give-and-get-data.undmkkl.mongodb.net/?appName=Give-and-Get-Data"

client = MongoClient(MONGO_URI)
db = client['HackPSU-User-Data']
users = db.users
orgs = db.organizations
app_stats = db.app_statistics 


'''---------------- DATABASE UTILITY FUNCTIONS ---------------'''

def update_database(id:str, new_json:dict, type:str):
    """
    id: id of user or org you want to change in users or orgs database
    type: is equal to either "users" or "organizations"
    """
    collection = db.users if type == "users" else db.organizations

    # Ensure the new JSON includes the same _id
    if "_id" not in new_json:
        new_json["_id"] = id

    result = collection.replace_one({"_id": id}, new_json, upsert=True)
    return f"Updated {result.modified_count} document(s)."


def update_user(id:str, new_json:dict):
    """
    id: id of user you want to change in users database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    update_database(id, new_json, "users") 
    return

def update_organization(id:str, new_json:dict):
    """
    id: id of org you want to change in orgs database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    update_database(id, new_json, "organizations")
    user_json =  {
        "_id": f"{id}",
        "name": new_json["name"], 
        "charity": new_json["type"]["charity"],
        "shelter": new_json["type"]["shelter"],
        "donor": False,
        "phone_number": new_json["contact"]["phone"],
        "email": new_json["contact"]["email"]
    }
    update_database(id, user_json, "users")
    return

def create_user(new_json, id=None):
    """
    new_json: the json for the new user
    id: will be a num if called by create_org()
    """
    if not id:
        id = generate_id()

    new_json["_id"] = str(id)
    
    update_user(id, new_json)
    return

def create_organization(new_json: dict):
    """
    Create a new organization and linked user entry.
    Geocodes the address — raises ValueError if address cannot be found.
    """
    id = generate_id()


    address = new_json.get("address", "").strip()

    # Try to geocode the provided address
    try:
        location = geolocator.geocode(address, timeout=10)
        if not location:
            raise ValueError(f"Unable to geocode address: '{address}'. Please provide a valid address.")
        new_json["location"] = {"lat": location.latitude, "lng": location.longitude}
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        raise ValueError(f"Geocoding service unavailable or timed out: {str(e)}")

    new_json["_id"] = str(id)
    update_organization(id, new_json)
    return id

def generate_id():
    collection = db.app_statistics
    result = collection.find_one_and_update(
        {"_id": "68fdc40a6d0189be52ed220f"},
        {"$inc": {"next_id": 1}},
        return_document=False
    )
    return str(result["next_id"])

def collect_user(id:str):
    """
    id: id of user you want to in users database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    collection = db.users
    user = collection.find_one({"_id": id})
    if user:
        return user
    else:
        raise ValueError(f"User with id {id} not found")

def collect_organization(id:str):
    """
    id: id of org you want to change in orgs database
    things_changed: dictionary with changes you wish to make in ket,value format
    """
    collection = db.organizations
    organization = collection.find_one({"_id": id})
    if organization:
        return organization
    else:
        raise ValueError(f"User with id {id} not found")

def get_orgs_within_radius(location, radius, org_type = None):
    """
    Retrieve organizations within a specified radius from a location.
    
    Args:
        location: {"lat": float, "lng": float} - Location to search from
        radius: int - Search radius in miles
        org_type: dict (optional) - Organization type filter
            Example: {"shelter": True, "charity": False} or {"shelter": True, "charity": True}
    
    Returns:
        list[tuple]: List of (distance_miles, organization_dict) tuples
            Example: [(2.5, {...org_data...}), (5.1, {...org_data...}), ...]
    """
    lat, lon = location['lat'], location['lng'] 
    all_orgs_dict = db.organizations.find()

    orgs_within_radius = []
    for org in all_orgs_dict:
        org_lat, org_lon = get_org_coords(org)
        dist = calculate_distance(lat, lon, org_lat, org_lon)
        if dist < radius:
            orgs_within_radius.append((dist, org))

    org_types = []
    if org_type["shelter"]:
        org_types += ["shelter"]
    if org_type["charity"]:
        org_types += ["charity"]

    if not org_type:
        return [(d, o) for d, o in orgs_within_radius]
    else: 
        return [(d, o) for d, o in orgs_within_radius if (len(org_types) == 2 and (o['type'][org_types[0]] or o['type'][org_types[1]] )) or (len(org_types) == 1 and (o['type'][org_types[0]]))]


def get_org_coords(org_dict):
    if not isinstance(org_dict,dict):
        return None
    
    lat = org_dict['location']['lat']
    lon = org_dict['location']['lng']
    return lat, lon


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def get_account_id(email: str, password: str):
    """
    Retrieves the user's account _id based on email and password.
    Returns the _id if a matching user is found, otherwise raises an error.

    Args:
        email (str): User's email address
        password (str): Plaintext password (or hashed if stored that way)

    Returns:
        str: The user's _id as a string
    """
    collection = db.users
    user = collection.find_one({"email": email, "password": password})
    
    if user:
        return user["_id"]
    else:
        raise ValueError("Invalid email or password.")
