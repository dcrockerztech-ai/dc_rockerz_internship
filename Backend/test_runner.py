import requests, json

# Load test profiles
with open('Backend/test_profiles.json') as f:
    profiles = json.load(f)

# Call backend for each profile
for p in profiles:
    r = requests.post('http://127.0.0.1:5000/recommend', json=p)
    if r.status_code == 200:
        data = r.json()
        if data["results"]:
            top = data["results"][0]
            print("Profile:", p)
            print("  Top Match:", top['title'], "-", top['company'])
            print("  Location:", top['location'], " | Score:", top['score'])
            print("-"*50)
        else:
            print("Profile:", p, "=> No results")
    else:
        print("Error:", r.status_code, r.text)
