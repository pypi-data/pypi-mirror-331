import requests
import json
import pandas as pd

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


class PrintixConnection:
    
    endpoints = {
        "get_tenants": "/partners/4aa9e6ce-132c-4747-b180-b4a3d0b14554/tenants",
        "create_tenant": "/partners/4aa9e6ce-132c-4747-b180-b4a3d0b14554/tenants",
        "get_tenant_details": "/partners/4aa9e6ce-132c-4747-b180-b4a3d0b14554/tenants/{tenant_id}",
        "get_tenant_billing": "/partners/4aa9e6ce-132c-4747-b180-b4a3d0b14554/tenants/{tenant_id}/billing-info"
    }

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.BASE_URL = "https://api.printix.net/public"
        self.AUTH_URL = "https://auth.printix.net/oauth/token"
        self.access_token = self.get_access_token()  # Automatically set token

    def get_access_token(self):
        """
        Fetches and returns an access token for authentication.
        """
        endpoint = self.AUTH_URL
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(endpoint, headers=headers, data=params)
        data = response.json()
        #print(data)
        #print(data['access_token'] )

        if 'access_token' not in data:
            raise Exception(f"Failed to obtain access token: {data.get('error_description', 'Unknown error')}")
        access_token = data['access_token'] 
        return access_token

    def post(self, endpoint: str, extra_params=None, debug: bool = False, json_output: bool = False):
        """
        Makes a POST request with the access token for authentication.
        """
        url = f"{self.BASE_URL}{endpoint}"  
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        response = requests.post(url, headers=headers, json=extra_params)

        if debug:
            print(response.json())

        if response.status_code in [200, 201]:
            return self.handle_output(response.json(), json_output=json_output)
        else:
            error_handler = apierrorhandler(response)
            error_handler.handle_error()

    def get(self, endpoint: str, debug: bool = False, json_output: bool = False):
        """
        Makes a GET request with optional parameters.
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        if debug:
            print(url)
            print(headers)

        # Adding extra_params as query parameters if provided
        response = requests.get(url, headers=headers)

        if debug:
            print(response.json())


        if response.status_code in [200, 201]:
            return self.handle_output(response.json(), json_output=json_output)
        else:
            error_handler = apierrorhandler(response)
            error_handler.handle_error()

    def handle_output(self, response_data, json_output: bool = False):
        """
        Handles the output format for API responses, automatically unpacking nested 'data'keys,
        and also unpacks nested structures within columns such as 'subaccounts' when present.

        Args:
            response_data (dict or list): The data returned from an API response.
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                        If False, returns the output as a pandas DataFrame.
                                        Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: The formatted output based on the json_output flag.
        """

        if isinstance(response_data, dict) and "tenants" in response_data:
            # Extract the list of tenants
            tenants = response_data["tenants"]
            
            # Create a DataFrame from the tenants list
            df = pd.json_normalize(tenants)
            
            # Optionally, include any additional processing here if needed

            return df
            
        # Fallback to original handling for other responses
        if isinstance(response_data, dict) and "data" in response_data:
            response_data = response_data["data"]

        if json_output:
            return json.dumps(response_data, indent=4)
        else:
            return pd.json_normalize(response_data)

        
    def generate_tenant_domain(self, customer_name):
        """
        Generates a tenant_domain from the customer_name according to the rules:
        - If an underscore is present, removes everything before it
        - All letters are lowercase
        - Only alphanumeric characters and hyphens are allowed
        - Maximum of 15 characters

        Args:
            customer_name (str): The name of the customer

        Returns:
            str: The tenant_domain name (maximum 15 characters)
        """
        # Remove everything before the underscore if it exists
        if '_' in customer_name:
            customer_name = customer_name.split('_', 1)[1]
        
        # Convert all letters to lowercase
        customer_name = customer_name.lower()
        
        # Keep only alphanumeric characters, replace spaces and special characters with hyphens
        tenant_domain = ''.join(char if char.isalnum() else '-' for char in customer_name)

        # Remove duplicate hyphens that might result from consecutive special characters
        tenant_domain = tenant_domain.strip('-')
        while '--' in tenant_domain:
            tenant_domain = tenant_domain.replace('--', '-')
        
        # Limit to a maximum of 15 characters
        tenant_domain = tenant_domain[:15]

        return tenant_domain


    def get_tenants(self, json_output: bool = False):
        """
        Makes a get request to  Pritnix to get all sub-domain accounts.

        Returns:
            dict: The response data from Pritnix.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """

        endpoint = self.endpoints['get_tenants']

        response = self.get(endpoint, json_output=json_output)
        return response  

    def get_tenant_details(self, tenant_id, json_output: bool = False):
        """
        Makes a get request to  Pritnix to get all sub-domain accounts.

        Returns:
            dict: The response data from Pritnix.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """


        endpoint = f"{self.endpoints['get_tenant_details']}".replace("{tenant_id}", str(tenant_id))

        response = self.get(endpoint, json_output=json_output)
        return response

    def get_tenant_billing(self, tenant_id, json_output: bool = False):
        """
        Makes a get request to  Pritnix to get all sub-domain accounts.

        Returns:
            dict: The response data from Pritnix.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """


        endpoint = f"{self.endpoints['get_tenant_billing']}".replace("{tenant_id}", str(tenant_id))

        response = self.get(endpoint, json_output=json_output)
        return response
    
    def create_tenant(self, customer_name, json_output: bool = False):
        """
        Makes a get request to  Pritnix to get all sub-domain accounts.

        Returns:
            dict: The response data from Pritnix.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """

        generate_name = self.generate_tenant_domain(customer_name)
        customer_domain = generate_name + ".printix.net"

        params = {
            'tenant_name' : customer_name,
            'tenant_domain' : customer_domain
        }

        endpoint = self.endpoints['create_tenant']

        response = self.post(endpoint, extra_params=params, json_output=json_output)
        return response
        


