import requests
import base64
import json
import pandas as pd
import time

class CoveBackupConnection:
    """
    A class to handle connections and interactions with the Cove Backup JSON RPC.

    Required libraries: requests, json, pandas
    """

    # List of jsonrpc methods
    endpoints = {
        "authentication": "Login",  # Method for authentication
        "get_customers": "EnumeratePartners",  # Method for fetching customers
        "create_customer": "AddPartner",  # Method for creating a customer
        "delete_customer": "RemovePartner",  # Method for deleting a customer
        "device_info": "EnumerateAccountStatistics"  # Method for fetching device statistics
    }

    # List of query codes with their human-readable names
    query_name_map = {
        "I1": "Device name",  # Device name
        "I2": "Device name alias",  # Alias for the device name
        "I3": "Password",  # Password
        "I4": "Creation date",  # Creation date
        "I5": "Expiration date",  # Expiration date
        "I8": "Customer",  # Customer name
        "I9": "Product ID",  # Product ID
        "I10": "Product",  # Product name
        "I14": "Used storage",  # Used storage
        "I19": "Internal IPs",  # Internal IP addresses
        "I21": "MAC address",  # MAC address
        "I31": "Used Virtual Storage",  # Virtual storage usage
        "I39": "Retention units",  # Retention units
        "I54": "Profile ID",  # Profile ID
        "I38": "Archived size",  # Archived size
        "I80": "Recovery Testing",  # Recovery testing status
        "F14": "Retention",  # Retention setting
        "F03": "Selected Size",  # Selected size
        "F20": "Total Mailboxes",  # Total mailboxes for Microsoft 365
    }

    # List of active data source codes with their human-readable names
    active_data_sources_map = {
        "D1": "Files and Folders",  # Files and folders backup
        "D2": "System State",  # System state backup
        "D3": "MsSql",  # Microsoft SQL backup
        "D4": "VssExchange",  # Volume Shadow Copy Service for Exchange
        "D5": "Microsoft 365 SharePoint",  # Microsoft 365 SharePoint
        "D6": "NetworkShares",  # Network shares
        "D7": "VssSystemState",  # Volume Shadow Copy System State
        "D8": "VMware Virtual Machines",  # VMware VMs backup
        "D9": "Total",  # Total backup sources
        "D10": "VssMsSql",  # VSS SQL backups
        "D11": "VssSharePoint",  # VSS SharePoint backups
        "D12": "Oracle",  # Oracle database backups
        "D14": "Hyper-V",  # Hyper-V backups
        "D15": "MySql",  # MySQL backups
        "D16": "Virtual Disaster Recovery",  # Virtual disaster recovery
        "D17": "Bare Metal Restore",  # Bare metal restore
        "D19": "Microsoft 365 Exchange",  # Microsoft 365 Exchange backups
        "D20": "Microsoft 365 OneDrive",  # Microsoft 365 OneDrive backups
        "D23": "Microsoft 365 Teams",  # Microsoft 365 Teams backups
    }

    def __init__(self, username: str = None, password: str = None, partner: str = None):
        """
        Initialize the connection with the backup.management.

        Args:
            username (str): The username for API access.
            password (str): The password for the user.
            partner (str): The full partner name to retrieve partner ID.
        """

        self.username = username  # Store the username
        self.password = password  # Store the password
        self.partner = partner  # Store the partner name
        self.baseurl = "https://api.backup.management/jsonapi"  # Base URL for the API
        self.partner_id = self.get_visa_token()  # Get visa token and partner ID during initialization

    def handle_output(self, response_data, json_output: bool = False):
        """
        Handle the output format for API responses.

        Args:
            response_data (dict or list): The data returned from an API response.
            json_output (bool, optional): If True, returns the output in JSON format. 
                                          If False, returns the deepest 'result' part as a pandas DataFrame.
                                          Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: The formatted output based on the json_output flag.
        """
        if json_output:  # Check if JSON format is requested
            return json.dumps(response_data, indent=4)  # Return the response data as a formatted JSON string

        # Traverse to the deepest 'result' field in the response
        if 'result' in response_data:
            nested_result = response_data['result']  # Start at the first level of 'result'
            while 'result' in nested_result:  # Continue going deeper until there are no more 'result' fields
                nested_result = nested_result['result']  # Update nested_result to the deeper 'result'
            df = pd.json_normalize(nested_result)  # Convert the deepest result to a pandas DataFrame
            return df  # Return the DataFrame
        else:
            df = pd.json_normalize(response_data)  # Convert the response data to a DataFrame
            return df  # Return the DataFrame

    def post(self, extra_params={}, debug=False):
        """
        Helper function to handle POST requests to the API.
        
        Args:
            extra_params (dict): Additional parameters to send with the request.
            debug (bool): If True, prints request and response data for debugging purposes.

        Returns:
            dict: The response data if the request is successful, or None in case of an error.
        """
        params = {
            "jsonrpc": "2.0",  # Standard JSON-RPC version
        }

        if extra_params:  # If additional parameters are provided
            params.update(extra_params)  # Merge them with the base parameters

        try:
            response = requests.post(self.baseurl, json=params)  # Make a POST request to the API

            if debug:  # If debug mode is enabled
                print("Request parameters: ", params)  # Print the request parameters
                print("Response status code: ", response.status_code)  # Print the status code of the response
                print("Response content: ", response.text)  # Print the response content

            if response.status_code == 200:  # Check if the response status is OK
                return response.json()  # Return the response data as a JSON object
            else:
                print(f"Error: Received status code {response.status_code}")  # Print error if status is not OK
                return None  # Return None in case of an error
        except Exception as e:
            print(f"An error occurred during the POST request: {str(e)}")  # Print any exception that occurs
            return None  # Return None in case of an exception

    def get_visa_token(self, json_output: bool = False):
        """
        Fetch the visa token and Partner ID by authenticating with the API.

        Args:
            json_output (bool, optional): If True, returns the output in JSON format. Defaults to False.

        Returns:
            dict: A dictionary containing the visa token and Partner ID.
        """
        params = {
            "method": self.endpoints['authentication'],  # Use the authentication method
            "params": {
                "partner": self.partner,  # Partner name for authentication
                "username": self.username,  # Username for authentication
                "password": self.password  # Password for authentication
            },
            "id": "1"  # JSON-RPC ID
        }
        response_data = self.post(extra_params=params)  # Send the POST request to authenticate

        if response_data is None:  # Check if the response is None
            print("No response data received from the API.")  # Print an error message
            return None  # Return None if no response

        try:
            visa_token = response_data['visa']  # Extract the visa token from the response
            partner_id = response_data['result']['result']['PartnerId']  # Extract the Partner ID
            print("Connection successful")  # Print success message
            return {'visa': visa_token, 'partner_id': partner_id}  # Return the visa token and Partner ID as a dict
        except KeyError as e:
            print(f"Visa token: {visa_token}")  # Print the visa token
            print(f"Partner ID: {partner_id}")  # Print the Partner ID
            print(f"Error: Missing expected key in the response: {e}")  # Print the KeyError
            return None  # Return None in case of a missing key

    def map_query_id_to_name(self, settings):
        """
        Converts query IDs to human-readable query names using the mapping.
        
        Args:
            settings (list): A list of settings where each item is a dict with a single key-value pair.
        
        Returns:
            dict: A dictionary with human-readable query names as keys and their values from the input.
        """
        mapped_settings = {}  # Initialize an empty dictionary to store the mapped settings
        for setting in settings:  # Loop through each setting in the list
            for key, value in setting.items():  # Extract the key and value from each setting
                query_name = self.query_name_map.get(key, key)  # Get the human-readable name or fallback to key
                mapped_settings[query_name] = value  # Add the mapped name and value to the dictionary
        return mapped_settings  # Return the dictionary with mapped names

    def map_active_data_sources(self, active_data_sources):
        """
        Converts Active Data Sources product IDs to their corresponding product names.
        
        Args:
            active_data_sources (list): A list of product IDs as strings (e.g., ["D1", "D2"]).
        
        Returns:
            list: A list of product names corresponding to the product IDs.
        """
        mapped_sources = [self.active_data_sources_map.get(source, source) for source in active_data_sources]  # Map each product ID to its name
        return mapped_sources  # Return the list of mapped product names
    
    def get_customer(self, json_output: bool = False):
        """
        Fetch customer information using the partner ID.

        Args:
            json_output (bool, optional): If True, returns the output in JSON format. Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: The customer information in the requested format.
        """
        params = {
            "id": "jsonrpc",  # JSON-RPC ID
            "visa": self.partner_id['visa'],  # Use the visa token for authentication
            "method": "EnumeratePartners",  # Use the EnumeratePartners method to get customers
            "params": {
                "parentPartnerId": self.partner_id['partner_id'],  # The partner ID to fetch customers for
                "fields": [0, 1, 3, 5, 8, 20],  # Fields to fetch
                "fetchRecursively": True  # Fetch customers recursively
            }
        }

        response_data = self.post(extra_params=params)  # Send the POST request to get customers
        return self.handle_output(response_data, json_output)  # Return the response data in the requested format

    def get_customer_devices(self, json_output: bool = False):
        """
        Fetches customer devices and maps query IDs to readable query names.

        Args:
            json_output (bool): If True, returns the full JSON output. If False, returns a DataFrame.

        Returns:
            dict or pd.DataFrame: Customer device information with readable settings.
        """
        params = {
            "id": "jsonrpc",  # JSON-RPC ID
            "visa": self.partner_id['visa'],  # Use the visa token for authentication
            "method": "EnumerateAccountStatistics",  # Use the method to get device info
            "params": {
                "query" : {
                    "PartnerId" : self.partner_id['partner_id'],  # Use the partner ID
                    "StartRecordNumber" : 0,  # Start at record 0
                    "RecordsCount" : 999,  # Fetch up to 999 records
                    "Columns" : ["GM", "I1", "I2", "I3", "I4", "I5", "I8", "I9", "I10", "I39", "I54", "I19", "I21", "I14", "I131", "F14", "I38", "I80", "TM"]  # Columns to fetch
                }
            }
        }

        response_data = self.post(extra_params=params)  # Send the POST request to get device info

        # Check if the 'result' field is in the response data
        if 'result' in response_data and 'result' in response_data['result']:
            devices = response_data['result']['result']  # Extract the list of devices
            for device in devices:  # Loop through each device
                if 'Settings' in device:  # Check if the device has settings
                    # Map query IDs to readable names and update the device
                    device.update(self.map_query_id_to_name(device['Settings']))  
                    del device['Settings']  # Remove the original 'Settings' column
                    
                    # Optionally handle active data sources if I78 is part of the settings
                    if 'I78' in device:
                        active_data_sources = device['I78'].split(",")  # Split active data sources by comma
                        device['Active Data Sources'] = self.map_active_data_sources(active_data_sources)  # Map product IDs to names
                        del device['I78']  # Remove the original 'I78' after processing

        # Convert response data to DataFrame if json_output is False
        if not json_output:
            df = pd.json_normalize(devices)  # Normalize the devices data into a pandas DataFrame
            
            # Remove 'MappedSettings.' prefix from column names if present
            df.columns = df.columns.str.replace('MappedSettings.', '', regex=False)

            return df  # Return the DataFrame

        return self.handle_output(response_data, json_output)  # Return the raw or formatted response based on json_output flag


    def create_customer(self, customer_name: str = None):
        """
        Create a new customer under the current partner ID.

        Args:
            customer_name (str): The name of the new customer to create.

        Returns:
            Union[str, pd.DataFrame]: The response from the API after customer creation.
        """
        params = {
            "id": "jsonrpc",  # JSON-RPC ID
            "visa": self.partner_id['visa'],  # Use the visa token for authentication
            "method": "AddPartner",  # Use the AddPartner method to create a customer
            "params": {
                "partnerInfo": {
                    "ParentId": self.partner_id['partner_id'],  # Use the parent partner ID
                    "Name": customer_name,  # The name of the new customer
                    "Level": "EndCustomer",  # Customer level
                    "ServiceType": "AllInclusive",  # Service type
                    "ChildServiceTypes": [
                        "AllInclusive"  # Sub-services
                    ],
                    "Country": "Netherlands"  # Country of the customer
                }
            }
        }

        response_data = self.post(extra_params=params)  # Send the POST request to create the customer
        return self.handle_output(response_data, json_output=True)  # Return the response in JSON format
    
    def delete_customer(self, partner_id: int = None, json_output: bool = False):
        """
        Deletes a customer based on the partner ID.

        Args:
            partner_id (int): The ID of the partner to delete.

        Returns:
            Union[str, pd.DataFrame]: The response from the API after deleting the customer.
        """
        params = {
            "id": "jsonrpc",  # JSON-RPC ID
            "visa": self.partner_id['visa'],  # Use the visa token for authentication
            "method": "RemovePartner",  # Use the RemovePartner method to delete a customer
            "params": {
                "partnerId": partner_id  # The partner ID of the customer to delete
            }
        }

        response_data = self.post(extra_params=params)  # Send the POST request to delete the customer
        return self.handle_output(response_data, json_output=True)  # Return the response in JSON format
