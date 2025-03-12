import requests
import json

# Enter your API key here
FIGMA_ACCESS_TOKEN = "figd_PhQxqbPQgD2tE4BKrtyE2-8ho7Pn9MsQlxhWqca2"  
FIGMA_API_URL = "https://api.figma.com/v1/files/"

def fetch_figma_json(file_key):
    headers = {"X-Figma-Token": FIGMA_ACCESS_TOKEN}
    try:
        response = requests.get(f"{FIGMA_API_URL}{file_key}", headers=headers, timeout=30)
        
        if response.status_code == 403:
            raise Exception("Access denied! Check Figma API key & file permissions.")
        elif response.status_code != 200:
            raise Exception(f"Figma API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network Error: {str(e)}")

def main():
    file_key = input("Enter Figma File Key: ").strip()
    
    if not file_key:
        print("⚠️ Please enter a Figma File Key")
        return
    
    try:
        print("Fetching Figma JSON data...")
        figma_data = fetch_figma_json(file_key)
        
        filename = f"figma_{file_key}.json"
        with open(filename, 'w') as f:
            json.dump(figma_data, f, indent=2)
        
        print(f"✅ Successfully saved Figma JSON to {filename}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()