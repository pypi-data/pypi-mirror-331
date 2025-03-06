import requests
import base64
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

class SMTP2GOConnection:
    
    endpoints = {
        "create_subdomain": "subaccount/add",  # Method for authentication
        "create_customer_account": "users/smtp/add",  # Method for fetching customers
        "get_all_subdomains": "subaccounts/search"
    }

    def __init__(self, api_key):
        self.api_key = api_key  # Authentication API key
        self.BASE_URL = "https://api.smtp2go.com/v3/"  # Default BASE URL

    def post(self, endpoint: str, extra_params, debug: bool = False, json_output: bool = False):
        """
        Makes a POST request to the SMTP2GO to create or update resources.

        Args:
            endpoint (str): The API endpoint to make the request to.
            extra_params (dict): The parameters to include in the POST request body.
            debug (bool, optional): If True, prints the JSON response for debugging purposes. Defaults to False.
            json_output (bool, optional): If True, returns the output in JSON format. Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: The response data from the server in JSON or DataFrame format.
        """
        url = f"{self.BASE_URL}{endpoint}"  # Construct the full URL for the POST request

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "X-Smtp2go-Api-Key": self.api_key
        }

        response = requests.post(url, headers=headers, json=extra_params)  # Perform the POST request

        if debug:
            print(response.json())  # Print the response if in debug mode

        if response.status_code == 200 or response.status_code == 201:
            return self.handle_output(response.json(), json_output=json_output)  # Use handle_output function
        else:
            error_handler = apierrorhandler(response)  # Initialize error handler
            error_handler.handle_error()  # Handle errors appropriately

    def handle_output(self, response_data, json_output: bool = False):
        """
        Handles the output format for API responses, automatically unpacking nested 'data' or 'results' keys,
        and also unpacks nested structures within columns such as 'subaccounts' when present.

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

        # If response_data is still a dictionary with a 'results' key, unpack it
        if isinstance(response_data, dict) and "results" in response_data:
            response_data = response_data["results"]

        # Convert to JSON string if json_output is True
        if json_output:
            return json.dumps(response_data, indent=4)
        else:
            # Convert to DataFrame using pandas
            df = pd.json_normalize(response_data)
            
            # Check for nested structures (like 'subaccounts') and unpack them if they are lists of dictionaries
            for column in df.columns:
                if isinstance(df[column].iloc[0], list) and isinstance(df[column].iloc[0][0], dict):
                    # If the column contains a list of dictionaries, normalize it into separate rows
                    df = df.explode(column).reset_index(drop=True)
                    sub_df = pd.json_normalize(df[column])
                    # Merge the exploded column with the main DataFrame
                    df = df.drop(columns=[column]).join(sub_df)

            return df


    def get_all_customers(self, json_output: bool = False):
        """
        Makes a get request to  SMTP2GO to get all sub-domain accounts.

        Returns:
            dict: The response data from SMTP2GO.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """

        endpoint = self.endpoints['get_all_subdomains']

        params = {
        "fuzzy_search": True,
        "page_size": 500
        }

        response = self.post(endpoint, extra_params=params, json_output=json_output)
        return response
        

    def create_customer_name(self, afas_id: str, pakket: str, customer_name: str):
        """
        Makes a POST request to the SMTP2GO to create or update resources, default with Pakket S.

        Args:
            endpoint (str): The API endpoint to make the request to.
            extra_params (dict): The parameters to include in the POST request body.
            debug (bool, optional): If True, prints the JSON response for debugging purposes. Defaults to False.

        Returns:
            dict: The response data from the server.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        # Strip special characters from the start and end of the customer name
        customer_name = customer_name.strip('!@#$%^&*()_+-=[]{},.<>?/|\\:;"\'`~')

        # Remove non-alphanumeric characters from the rest of the customer name
        klantnaam_schoon = ''.join(teken for teken in customer_name if teken.isalnum())

        # Create the email address in the correct format
        name = f"{afas_id}_{pakket}_{klantnaam_schoon}"
        print(name)
        return name
    
    def generate_random_password(self, length=16):
        # Define the set of characters to use for the password manually
        letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        digits = '0123456789'
        punctuation = '!@#$%^&*()-_=+[]{};:,.<>?'
        
        characters = letters + digits + punctuation

        # Generate a random password of the specified length
        password = ''
        for _ in range(length):
            index = int((len(characters) * int.from_bytes(os.urandom(1), 'big')) / 256)
            password += characters[index]

        return password

    def create_customer(self, customer_name: str, afas_id: str, pakket: str, json_output: bool = False):
        """
        Makes a POST request to the SMTP2GO to create a customer.

        Args:
            customer_name (str): The customer name.
            afas_id (str): Afas ID like 10000.
            pakket (str): Choose sending package Small (S), Medium (M), or Large (L).
            json_output (bool, optional): If True, returns the output in JSON format. Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: The response data from the server in JSON or DataFrame format.
        """
        endpoint = self.endpoints['create_subdomain']

        customer_name = self.create_customer_name(afas_id=afas_id, customer_name=customer_name, pakket=pakket)

        params = {
            "fullname": customer_name,
            "limit": 20000,
            "dedicated_ip": False
        }

        response = self.post(endpoint, extra_params=params, json_output=json_output)
        return response
    
    def create_customer_user(self, customer_id: str, username: str, json_output: bool = False):
        """
        Makes a POST request to the SMTP2GO to create a customer.

        Args:
            customer_id (str): The ID of the created customer subdomain.
            username (str): The username for the customer.
            json_output (bool, optional): If True, returns the output in JSON format. Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: The response data from the server in JSON or DataFrame format.
        """
        endpoint = self.endpoints['create_customer_account']

        password = self.generate_random_password()

        params = {
            "status": "allowed",
            "feedback_domain": "default",
            "username": username,
            "email_password": password,
            "subaccount_id": customer_id
        }

        response = self.post(endpoint, extra_params=params, json_output=json_output)
        print(f"Generated password for user: {password}")
        return response
