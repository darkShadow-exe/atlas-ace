import requests
import time
import re

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

def geocode_place(place):
    try:
        # 1. Search Wikipedia for the page
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(place)}&format=json"
        resp = requests.get(search_url, headers={"User-Agent": "atlasace"}, timeout=10)
        if resp.status_code == 200:
            search_results = resp.json()
            if search_results['query']['search']:
                page_title = search_results['query']['search'][0]['title']
                # 2. Get the page content and look for coordinates
                page_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                html = requests.get(page_url, headers={"User-Agent": "atlasace"}, timeout=10).text
                # Try to find coordinates in the HTML
                # Try decimal coordinates first
                match = re.search(r'class="geo-dec"[^>]*>([\d.\-]+)[^,]*,\s*([\d.\-]+)', html)
                if match:
                    lat, lon = float(match.group(1)), float(match.group(2))
                    return place, lat, lon, f"Wikipedia ({page_title})"
                # Try DMS coordinates
                match2 = re.search(r'class="latitude"[^>]*>([\d.\-NSEW°′″\s]+)</span>.*?class="longitude"[^>]*>([\d.\-NSEW°′″\s]+)</span>', html, re.DOTALL)
                if match2:
                    from geopy.point import Point
                    try:
                        point = Point(match2.group(1).replace("\u2212", "-"), match2.group(2).replace("\u2212", "-"))
                        return place, point.latitude, point.longitude, f"Wikipedia ({page_title})"
                    except Exception:
                        pass
    except Exception:
        pass
    return place, None, None, None

for place in places:
    name, lat, lon, source = geocode_place(place)
    if lat is not None and lon is not None:
        print(f"{name}: {lat}, {lon} (via Wikipedia)")
    else:
        print(f"{name}: NOT FOUND")
    time.sleep(1)
