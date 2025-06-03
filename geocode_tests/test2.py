import requests
import time

replacements = {
    "Bhakra Nangal, India": "Bhakra Dam, Himachal Pradesh, India",
    "Bailadila, India": "Bailadila Range, Chhattisgarh, India",
    "Bassien, India": "Vasai, Maharashtra, India",
    "Kakrapara, India": "Kakrapar Atomic Power Station, Gujarat, India",
    "Vishakhapatnam, India": "Visakhapatnam, Andhra Pradesh, India"
}

places = list(replacements.values())

def geocode_place(place):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": "atlasace"  
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200 and response.json():
        return True
    else:
        return False

for place in places:
    has_coord = geocode_place(place)
    print(f"{place}: {'FOUND' if has_coord else 'NOT FOUND'}")
    time.sleep(1)
