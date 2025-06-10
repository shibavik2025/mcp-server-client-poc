import requests
 
BASE_URL = "http://0.0.0.0:8000/api/v1/coreai-mcp-server-temp/stream"
 
def call_load_inventory():
    url = f"{BASE_URL}/load_inventory"
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "x-session-id": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Il9GcnhmUVZTbFBVbHZHWjVIdmRrTlN1Z1FzeXJkbjB1cWxXSkdJTVlfWXcifQ.eyJ0eXBlIjoicnQiLCJjbGllbnRJZCI6IjEyNmJjNDU0LTJjZDYtNDlmZS05Y2RmLTJjZjdlZjNhOWNlNyIsImlkcCI6Im1zZnQiLCJpc3MiOiJodHRwczovL2Rldi5saW9uaXMuYWkiLCJyb2xlcyI6WyJzdXBlcl91c2VyIl0sImp0aSI6IkNQQVYyMUlhdXUiLCJVc2VySW5mbyI6eyJpZCI6IjkxZTVmOTIzLWIzODctNGU1Yi04Y2VkLTgzODk1ZjUzMjRiOSIsImVtYWlsIjoic2hpYmF2aWtAcHVibGljaXNncm91cGUubmV0IiwiZGlzcGxheU5hbWUiOiJTaGl0YWwgQmF2aWthciJ9LCJhcHBLZXkiOiJza19kMjE0ODAwMmM2OGNjIiwiYXBwSWQiOiIyM2I2MWU3NS0yNGNhLTRjZDAtOTk5OS0wMTY1NmY1YTZhNzEiLCJzZXJ2aWNlcyI6WyJ0YXhvbm9teSIsInByb2plY3RzIiwibGxtIiwiYXNzZXQiLCJub3RpZmljYXRpb24iLCJhdWRpZW5jZSIsImRhdGEiLCJhc3NldC1hbmFseXplciIsImJvZGhpIiwiaW52ZW50b3J5Iiwic3RhdGUiXSwiYXBwTmFtZSI6IkFQSS1BR0VOVC1XT1JLQkVOQ0giLCJpbmR1c3RyeSI6IjM2ODgzOTkzLTNkNmEtNDhjNC05YzVjLWVmMTg2ZDQ5ZmFhOCIsImlhdCI6MTc0OTU1NzMxOCwiZXhwIjoxNzQ5NzMwMTE4fQ.cXMCXo8xj2Yfotv4TOUEwkLa-n6yTT3uHwyMz8AdH4KdvZkWzriVE5F7pn_i9zx0ZF7pPj9lVi7_0LUMffAsBcXWJnMX0gs92lv6STWz61uqLs5myO2Ngm7bml2lgtqPlqc94Wg9AeG_LE6KhCa8qj52_LsKii3cuOUAz1pDXYYJUEmmssjh8NdDjFoJ0tBX103q1cUiSBJN5MWvQ1AfD81oDXsHV7Tt5RQWGMM9bMhwL6ZFuIcxRGn-iHxTHsYACnpY6ym87CohqdFSY3U1ldpV-O3zotrJVmGz9dUDbcimJf79Bsspe33ZkWeIUBJKmAAyClROzcY6BVxMwgtc8Q"  # Ensure this header is included
    }
    # JSON-RPC request payload
    payload = {
        "jsonrpc": "2.0",
        "method": "load_inventory",
        "params": {},
        "id": 1
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Load Inventory Response:", response.json())
    else:
        print("Error:", response.status_code, response.text)
 
def call_forecasted_demand():
    url = f"{BASE_URL}/forecasted_demand"
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
        "x-session-id": "test-session"  # Ensure this header is included
    }
    # JSON-RPC request payload
    payload = {
        "jsonrpc": "2.0",
        "method": "forecasted_demand",
        "params": {},
        "id": 2
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Forecasted Demand Response:", response.json())
    else:
        print("Error:", response.status_code, response.text)
 
if __name__ == "__main__":
    call_load_inventory()
    call_forecasted_demand()