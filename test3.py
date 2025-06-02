import requests
import time
from geopy.geocoders import OpenCage

# List of all places to geocode
places = [
    # History - Congress Sessions
    "Calcutta, India", "Nagpur, India", "Madras, India",
    # Centres of National Movement
    "Champaran, Bihar, India", "Kheda, Gujarat, India", "Ahmedabad, Gujarat, India",
    "Amritsar, Punjab, India", "Dandi, Gujarat, India",
    # Dams
    "Salal, India", "Bhakra Nangal, India", "Tehri, India", "Rana Pratap Sagar, India",
    "Sardar Sarovar, India", "Hirakud, India", "Nagarjuna Sagar, India", "Tungabhadra, India",
    # Iron Ore Mines
    "Mayurbhanj, India", "Durg, India", "Bailadila, India", "Bellary, India", "Kudremukh, India",
    # Coal Mines
    "Raniganj, India", "Bokaro, India", "Talcher, India", "Neyveli, India",
    # Oil Fields
    "Digboi, India", "Naharkatia, India", "Mumbai High, India", "Bassien, India", "Kalol, India", "Ankleshwar, India",
    # Power Plants
    "Namrup, India", "Singrauli, India", "Ramagundam, India", "Narora, India", "Kakrapara, India", "Tarapur, India", "Kalpakkam, India",
    # Cotton Textile
    "Mumbai, India", "Indore, India", "Surat, India", "Kanpur, India", "Coimbatore, India",
    # Iron & Steel
    "Durgapur, India", "Jamshedpur, India", "Bhilai, India", "Vijayanagar, India", "Salem, India",
    # Software Tech Parks
    "Noida, India", "Gandhinagar, India", "Pune, India", "Hyderabad, India", "Bengaluru, India", "Chennai, India", "Thiruvananthapuram, India",
    # Sea Ports
    "Kandla, India", "Marmagao, India", "New Mangalore, India", "Kochi, India", "Tuticorin, India",
    "Vishakhapatnam, India", "Paradip, India", "Haldia, India",
    # Airports
    "Amritsar, India", "Delhi, India", "Kolkata, India"
]

def geocode_place(place, opencage_key=None):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "atlasace"
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return place, float(data["lat"]), float(data["lon"])
    except Exception:
        pass
    # Fallback to OpenCage
    if opencage_key:
        try:
            geolocator = OpenCage(api_key=opencage_key)
            location = geolocator.geocode(place)
            if location:
                return place, location.latitude, location.longitude
        except Exception:
            pass
    return place, None, None

OPENCAGE_KEY = "" 

for place in places:
    name, lat, lon = geocode_place(place, opencage_key=OPENCAGE_KEY)
    if lat is not None and lon is not None:
        print(f"{name}: {lat}, {lon}")
    else:
        print(f"{name}: NOT FOUND")
    time.sleep(1)
