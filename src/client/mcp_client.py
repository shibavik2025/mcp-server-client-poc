import requests
 
# BASE_URL = "http://0.0.0.0:8000/api/v1/mcp-server-retail-temp/stream"
BASE_URL="http://127.0.0.1:8000/mcp/"
 
def call_load_inventory():
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "x-session-id": "test-session"
    }
    payload = {
        "jsonrpc": "2.0",
        "method": "load_inventory",
        "params": {},
        "id": 1
    }
    response = requests.post(BASE_URL, headers=headers, json=payload)
    if response.status_code == 200:
        print("Load Inventory Response:", response.json())
    else:
        print("Error:", response.status_code, response.text)

def call_forecasted_demand():
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "x-session-id": "test-session"
    }
    payload = {
        "jsonrpc": "2.0",
        "method": "forecasted_demand",
        "params": {},
        "id": 2
    }
    response = requests.post(BASE_URL, headers=headers, json=payload)
    if response.status_code == 200:
        print("Forecasted Demand Response:", response.json())
    else:
        print("Error:", response.status_code, response.text)

if __name__ == "__main__":
    call_load_inventory()
    call_forecasted_demand()