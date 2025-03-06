import requests
import json
import pandas as pd
import time
import os

class apierrorhandler:
    def __init__(self, response):  
        """
        Initializes the APIErrorHandler class with the provided response.

        Args:
            response (requests.Response): The HTTP response object from the API request.
        """
        self.response = response

    def handle_error(self):
        """
        Handles various HTTP errors based on status codes and raises appropriate exceptions.

        Raises:
            Exception: Based on the HTTP status code, an appropriate error message is raised.
        """
        status_code = self.response.status_code

        if status_code == 200:
            print("200 OK: The API call was successful.")
        elif status_code == 201:
            print("201 Created: A new resource was successfully created via POST.")
        elif status_code == 202:
            print("202 Accepted: The request was accepted but processing is deferred.")
        elif status_code == 304:
            print("304 Not Modified: Resource not modified, no new data.")
        elif status_code == 400:
            raise Exception("400 Bad Request: The API client sent a malformed request.")  # Permanent error.
        elif status_code == 401:
            raise Exception("401 Unauthorized: Invalid credentials or token expired.")  # Permanent error.
        elif status_code == 403:
            raise Exception("403 Forbidden: No permission to perform this operation.")  # Permanent error.
        elif status_code == 404:
            raise Exception("404 Not Found: The requested resource wasn't found.")  # Semi-permanent error.
        elif status_code == 405:
            raise Exception("405 Method Not Allowed: Invalid HTTP method used.")  # Permanent error.
        elif status_code == 409:
            raise Exception("409 Conflict: The action cannot be performed due to a conflict.")  # Semi-permanent error.
        elif status_code == 413:
            raise Exception("413 Request Entity Too Large: Request exceeds the size limit.")  # Permanent error.
        elif status_code == 414:
            raise Exception("414 Request URI Too Long: The URI exceeds the 7KB limit.")  # Permanent error.
        elif status_code == 429:
            raise Exception("429 Too Many Requests: The client exceeded the request quota.")  # Retry possible.
        elif status_code == 451:
            raise Exception("451 Unavailable for Legal Reasons: API call is restricted by law.")  # Permanent error.
        elif status_code == 500:
            raise Exception("500 Internal Server Error: An unknown error occurred.")  # Retry possible.
        elif status_code == 502:
            raise Exception("502 Bad Gateway: The service is temporarily unavailable.")  # Retry possible.
        elif status_code == 503:
            raise Exception("503 Service Unavailable: The service is temporarily down.")  # Retry possible.
        else:
            self.response.raise_for_status()  # Raises an exception for unhandled HTTP status codes.


class UnifiControllerConnection:
    # Define Unifi endpoints
    endpoints = {
        'login': '/api/login',                      # Endpoint for authentication.
        'logout': '/logout',                        # Endpoint for logging out.
        'sites': '/api/self/sites',                 # Endpoint to retrieve sites.
        'devices': '/api/s/{site}/stat/device',     # Endpoint for device information (replace {site} with the site name).
        'site_settings': '/api/s/{site}/rest/setting', # Endpoint for site setting information (replace {site} with the site name).
        'set_site_settings': '/api/s/{site}/rest/setting/{key}/{_id}',
        'create_site': '/api/s/{site}/cmd/sitemgr'
    }

    def __init__(self, username: str = None, password: str = None, base_url: str = None, verify_ssl: bool = True):
        self.BASE_URL = base_url or "https://unifi.toschsecurity.nl:8443"  # Default BASE URL
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.headers = {
            "Content-Type": "application/json"
        }
        self.session = requests.Session()  # Use a session to persist cookies and headers

    def handle_output(self, response_data, json_output: bool = False):
        """
        Handles the output format for API responses.

        Args:
            response_data (dict or list): The data returned from an API response.
            json_output (bool, optional): If True, returns the output in JSON format as a string.
                                          If False, returns the output as a pandas DataFrame.
                                          Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: The formatted output based on the json_output flag.
        """
        # Check if response_data is a dictionary with a 'data' key
        if isinstance(response_data, dict) and "data" in response_data:
            # Extract the 'data' key's value
            response_data = response_data["data"]

        if json_output:
            return json.dumps(response_data, indent=4)  # Return as a JSON string
        else:
            df = pd.json_normalize(response_data)  # Convert JSON data to a pandas DataFrame
            return df  # Return DataFrame

    def generate_random_name(self, length=8):
        # Define the set of characters to use for the password manually
        letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        
        characters = letters + digits

        # Generate a random password of the specified length
        name = ''
        for _ in range(length):
            index = int((len(characters) * int.from_bytes(os.urandom(1), 'big')) / 256)
            name += characters[index]

        return name

    def post(self, endpoint: str, data=None, debug: bool = False):
        """
        Makes a POST request to the Unifi controller.

        Args:
            endpoint (str): The API endpoint to make the request to.
            data (dict): The data to include in the POST request body.
            debug (bool, optional): If True, prints the JSON response for debugging purposes. Defaults to False.

        Returns:
            dict: The JSON response data from the server.
        """
        url = f"{self.BASE_URL}{endpoint}"  # Construct the full URL for the POST request

        response = self.session.post(
            url,
            headers=self.headers,
            data=json.dumps(data),
            verify=self.verify_ssl
        )  # Perform the POST request

        if debug:
            print("POST Request to:", url)
            print("Headers:", self.headers)
            print("Data:", data)
            print("Response Status Code:", response.status_code)
            print("Response JSON:", response.json())

        if response.status_code in (200, 201):
            return response.json()
        else:
            error_handler = apierrorhandler(response)  # Initialize error handler
            error_handler.handle_error()  # Handle errors appropriately
            return None

    def get(self, endpoint: str, params: dict = None, data=None, debug: bool = False, json_output: bool = False):
        """
        Performs an authenticated GET request to the Unifi API.

        Args:
            endpoint (str): The API endpoint to request.
            params (dict): Optional query parameters for the GET request.
            data (str or dict): Optional data to include in the GET request body.
            debug (bool, optional): If True, prints debug information. Defaults to False.

        Returns:
            dict: The JSON response data from the server.
        """
        url = f"{self.BASE_URL}{endpoint}"

        response = self.session.get(
            url,
            headers=self.headers,
            params=params,
            data=data,
            verify=self.verify_ssl
        )

        if debug:
            print("GET Request to:", url)
            print("Headers:", self.headers)
            print("Params:", params)
            print("Data:", data)
            print("Response Status Code:", response.status_code)
            try:
                print("Response JSON:", response.json())
            except json.JSONDecodeError:
                print("Response Content:", response.content)

        if response.status_code == 200:
            return self.handle_output(response.json(), json_output=json_output)  # Use handle_output function
        else:
            error_handler = apierrorhandler(response)  # Initialize error handler
            error_handler.handle_error()  # Handle errors appropriately
            return None
        

    def put(self, endpoint: str, params: dict = None, data=None, debug: bool = False, json_output: bool = False):
        """
        Performs an authenticated GET request to the Unifi API.

        Args:
            endpoint (str): The API endpoint to request.
            params (dict): Optional query parameters for the GET request.
            data (str or dict): Optional data to include in the GET request body.
            debug (bool, optional): If True, prints debug information. Defaults to False.

        Returns:
            dict: The JSON response data from the server.
        """
        url = f"{self.BASE_URL}{endpoint}"

        response = self.session.put(
            url,
            headers=self.headers,
            json=params,
            data=data,
            verify=self.verify_ssl
        )

        if debug:
            print("PUT Request to:", url)
            print("Headers:", self.headers)
            print("Params:", params)
            print("Data:", data)
            print("Response Status Code:", response.status_code)
            try:
                print("Response JSON:", response.json())
            except json.JSONDecodeError:
                print("Response Content:", response.content)

        if response.status_code == 200 or response.status_code == 201:
            return self.handle_output(response.json(), json_output=json_output)  # Use handle_output function
        else:
            error_handler = apierrorhandler(response)  # Initialize error handler
            error_handler.handle_error()  # Handle errors appropriately
            return None    

    def login(self):
        """
        Logs in to the Unifi controller.
        """
        endpoint = self.endpoints['login']
        login_data = {
            'username': self.username,
            'password': self.password
        }

        response = self.post(endpoint, data=login_data)

        if response is None:
            raise Exception("Failed to log in to API with provided credentials")
        else:
            print("Logged in successfully.")

    def logout(self):
        """
        Logs out from the Unifi controller.
        """
        endpoint = self.endpoints['logout']
        url = f"{self.BASE_URL}{endpoint}"
        self.session.get(url, verify=self.verify_ssl)
        self.session.close()
        print("Logged out and session closed.")

    def get_sites(self, json_output: bool = False):
        """
        Retrieves the available sites from the Unifi controller.

        Args:
            json_output (bool): If True, returns JSON output.

        Returns:
            DataFrame or JSON string with site information.
        """
        endpoint = self.endpoints['sites']
        response = self.get(endpoint, json_output=json_output)
        return response

    def get_device_info(self, site: str, json_output: bool = False):
        """
        Retrieves device information from a specific site.

        Args:
            site (str): The site name.
            json_output (bool): If True, returns JSON output.

        Returns:
            DataFrame or JSON string with device information.
        """
        endpoint = f"{self.endpoints['devices']}".replace("{site}", str(site))  # Retrieve the endpoint for organization properties
        response = self.get(endpoint, json_output=json_output)
        return response
    
    def get_site_settings(self, site: str, json_output: bool = False):
        """
        Retrieves settings information from a specific site.

        Args:
            site (str): The site name.
            json_output (bool): If True, returns JSON output.

        Returns:
            DataFrame or JSON string with device information.
        """
        endpoint = f"{self.endpoints['site_settings']}".replace("{site}", str(site))  # Retrieve the endpoint for organization properties
        response = self.get(endpoint, json_output=json_output)
        return response
    
    def set_site_settings(self, site: str, key: str, id: str, params: dict = None, json_output: bool = False):
        """
        Retrieves settings information from a specific site.

        Args:
            site (str): The site name.
            json_output (bool): If True, returns JSON output.

        Returns:
            DataFrame or JSON string with device information.
        """

        endpoint = f"{self.endpoints['set_site_settings']}".replace("{site}", str(site)).replace("{key}", str(key)).replace("{key}", str(id))  # Format the site, setting key and setting ID
        response = self.put(endpoint, params=params, json_output=json_output)
        return response
    
    def set_ssh_site(self, site: str, id: str, json_output: bool = False):
        """
        Sets SSH settings for a specific site.

        Args:
            site (str): The site name.
            id (str): ID of mgmt site key
            json_output (bool): If True, returns JSON output.

        Returns:
            DataFrame or JSON string with device information.
        """

        # Generate random password
        random_name = self.generate_random_name(length=20)

        params = {
            'x_ssh_username': 'admin_unifi',
            'x_ssh_password':  random_name,
            'x_ssh_enabled':  True
        }
        
        # SSH rest api key
        key = "mgmt"

        respone = self.set_site_settings(site=site, id=id, key=key, params=params, json_output=json_output)
        return respone

    
    def create_site(self, customer_name: str, site: str = 'default', json_output: bool = False):
        """
        Creates a new site on the Unifi controller.

        Args:
            customer_name (str): Short name for the new site <AFAS ID>119_<AFAS Name>.
            base_site (str): The base site to use in the URL (defaults to 'default').
            json_output (bool, optional): If True, returns the output in JSON format as a string.
                                        If False, returns the output as a pandas DataFrame.
                                        Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: The formatted output based on the json_output flag.
        """
        # Construct the endpoint URL by replacing {site} with the base site (usually 'default')
        endpoint = self.endpoints['create_site'].replace("{site}", site)

        # Create random name for site url
        random_name = self.generate_random_name()

        # Prepare the data payload for the POST request
        data = {
            "cmd": "add-site",
            "desc": customer_name,
            "name": random_name
        }

        # Send the POST request to create the new site
        response = self.post(endpoint, data=data)

        # Handle and return the response
        if response is not None:
            return self.handle_output(response, json_output=json_output)
        else:
            return None