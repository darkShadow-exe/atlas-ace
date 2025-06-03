import requests
import json
from geopy.geocoders import Nominatim

# User Customization
custom_instructions = {
    "num_questions": 10,  # Total questions
    "type_ratio": [0.5, 0.5],  # [find_ratio, name_ratio] must sum to 1
    "filter_topics": [],  # Example: ["Dams", "Thermal"], empty = no filter
    "include_history": True  # Set False to exclude History questions
}

# Prompt
prompt = f"""
You are an educational AI assistant creating a map-based learning dataset for CBSE Class 10. Use the syllabus below to generate question-answer pairs.

Follow these custom instructions:
- Total questions: {custom_instructions['num_questions']}
- Ratio of 'find' (map click) to 'name' (user types name): {custom_instructions['type_ratio'][0]} : {custom_instructions['type_ratio'][1]}
- Topics to include: {"All" if not custom_instructions['filter_topics'] else ", ".join(custom_instructions['filter_topics'])}
- Include history-related questions: {"Yes" if custom_instructions['include_history'] else "No"}

---

SYLLABUS  
{"History – Chapter 2: Nationalism in India (1918–1930)" if custom_instructions['include_history'] else ""}
{"- Indian National Congress Sessions: Calcutta (Sept 1920), Nagpur (Dec 1920), Madras (1927)" if custom_instructions['include_history'] else ""}
{"- Centres of the Indian National Movement: Champaran (Bihar), Kheda (Gujarat), Ahmedabad (Gujarat), Amritsar (Punjab), Dandi (Gujarat)" if custom_instructions['include_history'] else ""}

Geography – Chapter 3: Water Resources  
- Dams: Salal, Bhakra Nangal, Tehri, Rana Pratap Sagar, Sardar Sarovar, Hirakud, Nagarjuna Sagar, Tungabhadra

Geography – Chapter 5: Minerals and Energy Resources  
- Iron Ore Mines: Mayurbhanj, Durg, Bailadila, Bellary, Kudremukh  
- Coal Mines: Raniganj, Bokaro, Talcher, Neyveli  
- Oil Fields: Digboi, Naharkatia, Mumbai High, Bassien, Kalol, Ankleshwar  
- Power Plants:  
  - Thermal: Namrup, Singrauli, Ramagundam  
  - Nuclear: Narora, Kakrapara, Tarapur, Kalpakkam

Geography – Chapter 6: Manufacturing Industries  
- Cotton Textile: Mumbai, Indore, Surat, Kanpur, Coimbatore  
- Iron & Steel: Durgapur, Bokaro, Jamshedpur, Bhilai, Vijayanagar, Salem  
- Software Tech Parks: Noida, Gandhinagar, Mumbai, Pune, Hyderabad, Bengaluru, Chennai, Thiruvananthapuram

Geography – Chapter 7: Lifelines of National Economy  
- Major Sea Ports: Kandla, Mumbai, Marmagao, New Mangalore, Kochi, Tuticorin, Chennai, Vishakhapatnam, Paradip, Haldia  
- International Airports: Amritsar, Delhi, Mumbai, Chennai, Kolkata, Hyderabad

---

OUTPUT FORMAT  
Return a JSON array with each object in this format:

{{
  "question": "Where is the Bhakra Nangal Dam located?",
  "answer": "Bhakra Nangal",
  "place": "Bhakra Nangal, India",
  "category": "Geography",
  "chapter": "Water Resources",
  "topic": "Dams",
  "type": "name"
}}

Point Type Explanation:  
- "name" → User sees a location on the map and must type the name.  
- "find" → User sees the name and must click the location on the map.

Maintain the specified ratio between 'find' and 'name' question types.  
Use only city/town + state or country in the place field for compatibility with Nominatim.  
If filter_topics is set, only include questions from those topics.  
Return only the JSON array.
"""

# Send Request
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3",
        "prompt": prompt,
        "stream": True
    }
)

# Read and Collect Streamed Response
full_output = ""
if response.ok:
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            if "response" in data:
                full_output += data["response"]
else:
    print("Error:", response.status_code, response.text)
    exit()

# Parse and Print JSON Output
try:
    json_start = full_output.find("[")
    json_end = full_output.rfind("]") + 1
    parsed_data = json.loads(full_output[json_start:json_end])
except Exception as e:
    print("Error parsing JSON:", str(e))
    print("Raw Output:", full_output)
    exit()

# Geocode each 'place' and add coordinates
geolocator = Nominatim(user_agent="atlas-ace-geocoder")
for obj in parsed_data:
    place = obj.get("place")
    if place:
        try:
            location = geolocator.geocode(place)
            if location:
                obj["coordinates"] = {"lat": location.latitude, "lon": location.longitude}
            else:
                obj["coordinates"] = None
        except Exception:
            obj["coordinates"] = None

print(json.dumps(parsed_data, indent=2))
