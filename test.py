import requests

# The URL of your running backend's login endpoint
url = "http://127.0.0.1:8000/login"

# The data your frontend sends, in the correct format.
# !!! IMPORTANT: Use the email and REAL password for a user you have
# already registered and verified in your database.
form_data = {
    "username": "saad@gmail.com",      # Your registered user's email
    "password": "YOUR_REAL_PASSWORD"   # <<< CHANGE THIS to the user's actual password
}

print("--- Sending request to backend... ---")

# Make the POST request with x-www-form-urlencoded data
response = requests.post(url, data=form_data)

print(f"--- Backend responded with Status Code: {response.status_code} ---")
print("--- Response JSON: ---")
try:
    # Try to print the JSON response
    print(response.json())
except requests.exceptions.JSONDecodeError:
    # If it's not JSON, print the raw text
    print("Response was not valid JSON.")
    print("Response Text:", response.text)