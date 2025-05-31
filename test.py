import requests
import json

# Prompt
prompt = """
You are an educational AI assistant helping to create a map-based learning dataset for CBSE Class 10. Use the following syllabus to generate 10 question-answer pairs.

---
📚 SYLLABUS:
• History – Chapter 2: Nationalism in India (1918–1930)
  - Indian National Congress Sessions:
    - Calcutta (Sept 1920), Nagpur (Dec 1920), Madras (1927)
  - Centres of the Indian National Movement:
    - Champaran (Bihar), Kheda (Gujarat), Ahmedabad (Gujarat), Amritsar (Punjab), Dandi (Gujarat)

• Geography – Chapter 3: Water Resources
  - Dams: Salal, Bhakra Nangal, Tehri, Rana Pratap Sagar, Sardar Sarovar, Hirakud, Nagarjuna Sagar, Tungabhadra

• Geography – Chapter 5: Minerals and Energy Resources
  - Iron Ore Mines: Mayurbhanj, Durg, Bailadila, Bellary, Kudremukh
  - Coal Mines: Raniganj, Bokaro, Talcher, Neyveli
  - Oil Fields: Digboi, Naharkatia, Mumbai High, Bassien, Kalol, Ankleshwar
  - Power Plants:
    - Thermal: Namrup, Singrauli, Ramagundam
    - Nuclear: Narora, Kakrapara, Tarapur, Kalpakkam

• Geography – Chapter 6: Manufacturing Industries
  - Cotton Textile: Mumbai, Indore, Surat, Kanpur, Coimbatore
  - Iron & Steel: Durgapur, Bokaro, Jamshedpur, Bhilai, Vijayanagar, Salem
  - Software Tech Parks: Noida, Gandhinagar, Mumbai, Pune, Hyderabad, Bengaluru, Chennai, Thiruvananthapuram

• Geography – Chapter 7: Lifelines of National Economy
  - Major Sea Ports: Kandla, Mumbai, Marmagao, New Mangalore, Kochi, Tuticorin, Chennai, Vishakhapatnam, Paradip, Haldia
  - International Airports: Amritsar, Delhi, Mumbai, Chennai, Kolkata, Hyderabad
---

🧾 OUTPUT FORMAT:
Return the data as a JSON array. Each object should follow this format:

{
  "question": "Where is the Bhakra Nangal Dam located?",
  "answer": "Bhakra Nangal",
  "place": "Bhakra Nangal, India",
  "category": "Geography",
  "chapter": "Water Resources",
  "topic": "Dams"
}

Make sure the 'place' field is suitable for geocoding using the Nominatim API (city/town + state or country). Do not explain anything. Just return the JSON.
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

try:
    json_start = full_output.find("[")
    json_end = full_output.rfind("]") + 1
    parsed_data = json.loads(full_output[json_start:json_end])
except Exception as e:
    print("Error parsing JSON:", str(e))
    print("Raw Output:", full_output)
    exit()

print(json.dumps(parsed_data, indent=2))
