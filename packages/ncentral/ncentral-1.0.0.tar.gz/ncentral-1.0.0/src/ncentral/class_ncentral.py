import requests  # Imports the 'requests' library to handle HTTP requests.
import json  # Imports the 'json' library for working with JSON data.
import time  # Imports the 'time' library for sleep functionality to avoid rate limits.
import pandas as pd  # Imports 'pandas' for data manipulation, especially working with DataFrames.


class NCentralConnection:
    """
    A class to handle connections and interactions with the N-central API.
    """

    # List of API endpoints
    endpoints = {   
        "authenticate": "/api/auth/authenticate",
        "refresh": "/api/auth/refresh",  
        "service_orgs": "/api/service-orgs",  
        "organisation_default_properties": "/api/org-units/50/custom-properties?sortOrder=ASC",  
        "organisation_properties": "/api/org-units/{customerid}/custom-properties?sortOrder=ASC",  
        "customers": "/api/org-units?sortBy=orgUnitName&sortOrder=asc",  
        "customer_sites": "/api/customers/{customerid}",  
        "customer_devices": "/api/org-units/{customerid}/devices?sortOrder=ASC",  
        "device_custom_properties": "/api/devices/{deviceid}/custom-properties",  
        "device_assets": "/api/devices/{deviceid}/assets",  
        "new_customer": "/api/service-orgs/50/customers",  
        "update_customer_property": "/api/org-units/{customerid}/custom-properties/{property_id}",  
        "update_customer_contract": "/api/org-units/{customerid}/custom-properties/1077441815",  
        "update_customer_sla": "/api/org-units/{customerid}/custom-properties/1993836718",  
        "device_filters": "/api/device-filters",  
        "device_by_filter": "/api/devices",  
        "registration_token": "/api/customers/{customerid}/registration-token" 
    }

    def __init__(self, ncentral_host: str = None, api_token: str = None):
        """
        Initialize the connection with the N-central server.

        Args:
            ncentral_host (str): The address of the N-central server.
            api_token (str): The API token required for authentication.
        """
        self.ncentral_host = ncentral_host  
        self.api_token = api_token  
        self.access_token = None  
        self.refresh_token = None
        self.access_token_expiry = None  
        self.get_tokens()  

    def get_tokens(self):
        """
        Retrieves the access token and refresh token by authenticating with the N-central server.

        Updates:
            self.access_token (str): The access token for making API calls.
            self.refresh_token (str): The refresh token used to renew access tokens.
            self.access_token_expiry (int): The expiry time (in seconds) for the access token.
        """
        url = f"https://{self.ncentral_host}{self.endpoints['authenticate']}"
        headers = {
            "Authorization": f"Bearer {self.api_token}", 
            "Content-Type": "text/plain" 
        }
        response = requests.post(url, headers=headers)  

        if response.status_code == 200:
            data = response.json()  
            self.access_token = data["tokens"]["access"]["token"]
            self.refresh_token = data["tokens"]["refresh"]["token"]
            self.access_token_expiry = int(time.time()) + data["tokens"]["access"]["expirySeconds"]  # Set expiry time for access token
        else:
            raise Exception(f"Authentication failed: {response.text}")  

    def refresh_access_token(self):
        """
        Refreshes the access token using the refresh token if the access token is expired or near expiry.
        """
        if self.refresh_token is None:
            raise Exception("No refresh token available.")

        url = f"https://{self.ncentral_host}{self.endpoints['refresh']}"
        headers = {
            "Authorization": f"Bearer {self.api_token}", 
            "Content-Type": "text/plain" 
        }

        data = self.refresh_token

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            data = response.json()
            self.access_token = data["tokens"]["access"]["token"]
            self.access_token_expiry = int(time.time()) + data["tokens"]["access"]["expirySeconds"]  # Update the expiry time
            print("Saved Access Token and Expiry token")
        else:
            raise Exception(f"Failed to refresh access token: {response.text}")

    def is_token_expired(self):
        """
        Checks if the access token has expired or is near expiry.
        Returns True if the token is expired or near expiry (e.g., within 5 minutes), otherwise False.
        """
        if self.access_token_expiry is None:
            return True

        current_time = int(time.time())
        return current_time >= self.access_token_expiry - 300  # 5 minutes buffer before expiry

    def get(self, endpoint: str, extra_params={}, debug: bool = False):
        """
        Makes a GET request to the N-central server and handles pagination, including token refresh if necessary.
        """
        if self.is_token_expired():  # Check if the token has expired
            print("Access token expired, refreshing token...")
            self.refresh_access_token()  # Refresh the access token if expired

        responses = []  
        failed_requests = []  
        max_retries = 3  
        retry_delays = [30, 300, 1800]  

        for attempt in range(max_retries):
            try:
                page = 1
                page_total = 1

                while page <= page_total:
                    params = {"pageNumber": page, "pageSize": 50}

                    if extra_params:
                        params.update(extra_params)

                    url = f"https://{self.ncentral_host}{endpoint}"
                    headers = {
                        "Authorization": f"Bearer {self.access_token}",  
                        "Content-Type": "application/json"  
                    }

                    response = requests.get(url=url, headers=headers, params=params)

                    if debug:
                        print(response.json())

                    time.sleep(1)

                    if response.status_code == 200:
                        data = response.json()

                        if "data" in data and isinstance(data["data"], (list, dict)):
                            items = data["data"]

                            total_items = data.get("totalItems", 0)
                            if total_items <= 50:
                                return items

                            responses.extend(items)
                            page_total = data.get("totalPages", 1)
                            links = data.get("_links")
                            if links and links.get("nextPage") is None:
                                break

                            page += 1
                        else:
                            return data

                    else:
                        raise requests.exceptions.HTTPError(f"Request failed with status code: {response.status_code}")

                return responses

            except requests.exceptions.HTTPError as e:
                print(f"HTTP Error on attempt {attempt + 1} for {endpoint}: {e}")
                failed_requests.append({
                    "endpoint": endpoint,
                    "params": extra_params,
                    "error": str(e)
                })
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("Max retries reached. Continuing with next items.")
                    break

            except requests.RequestException as e:
                print(f"Request exception on attempt {attempt + 1} for {endpoint}: {e}")
                failed_requests.append({
                    "endpoint": endpoint,
                    "params": extra_params,
                    "error": str(e)
                })
                if attempt < max_retries - 1:
                    delay = retry_delays[attempt]
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("Max retries reached. Continuing with next items.")
                    break

        if failed_requests:
            print(f"Failed to process {len(failed_requests)} requests.")
            for failure in failed_requests:
                print(f"Failed request: {failure}")

        return responses


    

    def post(self, endpoint: str, extra_params, debug: bool = False):
        """
        Makes a POST request to the N-central server to create or update resources.

        Args:
            endpoint (str): The API endpoint to make the request to.
            extra_params (dict): The parameters to include in the POST request body.
            debug (bool, optional): If True, prints the JSON response for debugging purposes. Defaults to False.

        Returns:
            dict: The response data from the server.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        url = f"https://{self.ncentral_host}{endpoint}"  # Construct the full URL for the POST request

        headers = {
            "Authorization": f"Bearer {self.access_token}",  # Include access token in headers
            "Content-Type": "application/json"  # Set content type to JSON
        }

        response = requests.post(url, headers=headers, json=extra_params)  # Perform the POST request

        if debug:
            print(response.json())  # Print the response if in debug mode

        if response.status_code == 200 or response.status_code == 201:
            return response.json()  # Return the entire response data
        else:
            print(response.text)  # Print response text for errors
            raise Exception(f"POST request failed with status code: {response.status_code}")  # Raise exception

    def put(self, endpoint: str, extra_params=None, json_output: bool = False):
        """
        Makes a PUT request to the N-central server to update resources.

        Args:
            endpoint (str): The API endpoint to make the request to.
            extra_params (dict, optional): The parameters to include in the PUT request body. Defaults to None.
            json_output (bool, optional): If True, returns the response in JSON string format. Defaults to False.

        Returns:
            Union[str, dict]: The response data from the server or a string message for no content.

        Raises: 
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        url = f"https://{self.ncentral_host}{endpoint}"  # Construct the full URL for the PUT request

        headers = {
            "Authorization": f"Bearer {self.access_token}",  # Include access token in headers
            "Content-Type": "application/json"  # Set content type to JSON
        }

        try:
            response = requests.put(url, headers=headers, json=extra_params)  # Perform the PUT request

            if response.status_code in [200, 204]:
                if response.status_code == 204:
                    return "No content to return (204 No Content)"  # Return message if no content
                
                return self.handle_output(response.json(), json_output)  # Handle response output

            else:
                print(response.text)  # Print response text for errors
                raise Exception(f"PUT request failed with status code: {response.status_code}")  # Raise exception

        except requests.RequestException as error:
            print(f"Request failed: {error}")  # Print error message
            raise  # Rethrow the exception

    def clean_entry(self, input_string: str):
        """
        Removes special characters such as '&', '/', and '\"' from the given input string, 
        and strips any leading or trailing whitespace.

        Args:
            input_string (str): The string that needs to be cleaned. 

        Returns:
            str: A cleaned version of the input string, with special characters removed and extra whitespace stripped.
        """
        cleaned_string = input_string.replace("&", "").replace("/", "").replace("\"", "")  # Remove special characters
        cleaned_string = cleaned_string.strip()  # Remove leading and trailing whitespace
        cleaned_entry = cleaned_string  # Set cleaned_entry to cleaned_string

        return cleaned_entry  # Return cleaned entry

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
        if json_output:
            return json.dumps(response_data, indent=4)  # Return as a JSON string
        else:
            df = pd.json_normalize(response_data)  # Convert JSON data to a pandas DataFrame
            return df  # Return DataFrame

    def get_organisation(self, json_output: bool = False):
        """
        Retrieves the service organization from the N-central server.

        Args:
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas Series. 
                                          Defaults to False.

        Returns:
            Union[str, pd.Series]: A pandas Series with the service organization information. 
                                   If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        response_data = self.get(self.endpoints['service_orgs'])  # Retrieve service organization data
        return self.handle_output(response_data, json_output)  # Handle output format

    def organisation_default_properties(self, json_output: bool = False):
        """
        Retrieves the default custom properties for the service organization from the N-central server.

        Args:
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas Series. 
                                          Defaults to False.

        Returns:
            Union[str, pd.Series]: A pandas Series with the organization properties. 
                                   If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        endpoint = self.endpoints['organisation_default_properties']  # Retrieve the endpoint for organization properties
        response_data = self.get(endpoint)  # Make the GET request for organization properties
        return self.handle_output(response_data, json_output)  # Handle output format
    
    def get_organisation_properties(self, customerid, json_output: bool = False):
        """
        Retrieves the default custom properties for the service organization from the N-central server.

        Args:
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas Series. 
                                          Defaults to False.

        Returns:
            Union[str, pd.Series]: A pandas Series with the organization properties. 
                                   If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """

        endpoint = f"{self.endpoints['organisation_properties']}".replace("{customerid}", str(customerid))  # Retrieve the endpoint for organization properties
        response_data = self.get(endpoint)  # Make the GET request for organization properties
        return self.handle_output(response_data, json_output)  # Handle output format

    def get_customers(self, json_output: bool = False):
        """
        Retrieves all customers and sub-customers from the N-central server.

        Args:
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas DataFrame. 
                                          Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: A DataFrame containing information about all customers and sub-customers. 
                                      If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        endpoint = self.endpoints['customers']  # Retrieve the endpoint for customers
        response_data = self.get(endpoint)  # Make the GET request for customers
        return self.handle_output(response_data, json_output)  # Handle output format

    def get_customer_sites(self, customerid, json_output: bool = False):
        """
        Retrieves all sites for a specific customer from the N-central server.

        Args:
            customerid (int): The unique identifier of the customer for which to retrieve the sites.
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas DataFrame. 
                                          Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: A DataFrame containing information about the sites associated with the specified customer. 
                                      If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        endpoint = f"{self.endpoints['customer_sites']}".replace("{customerid}", str(customerid))  # Format the endpoint with customer ID
        response_data = self.get(endpoint)  # Make the GET request for customer sites
        return self.handle_output(response_data, json_output)  # Handle output format

    def get_customer_devices(self, customerid, json_output: bool = False):
        """
        Retrieves all devices associated with a specific customer from the N-central server.
        To get all devices, use customerid 50

        Args:
            customerid (int): The unique identifier of the customer for which to retrieve the devices.
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas DataFrame. 
                                          Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: A DataFrame containing information about the devices associated with the specified customer. 
                                      If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        endpoint = f"{self.endpoints['customer_devices']}".replace("{customerid}", str(customerid))  # Format the endpoint with customer ID
        response_data = self.get(endpoint)  # Make the GET request for customer devices
        return self.handle_output(response_data, json_output)  # Handle output format

    def get_device_custom_properties(self, deviceid, json_output: bool = False):
        """
        Retrieves the custom properties of a specific device from the N-central server.

        Args:
            deviceid (int): The unique identifier of the device for which to retrieve the custom properties.
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas Series. 
                                          Defaults to False.

        Returns:
            Union[str, pd.Series]: A pandas Series with the custom properties of the specified device. 
                                   If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        endpoint = f"{self.endpoints['device_custom_properties']}".replace("{deviceid}", str(deviceid))  # Format the endpoint with device ID
        response_data = self.get(endpoint)  # Make the GET request for device custom properties
        return self.handle_output(response_data, json_output)  # Handle output format

    def get_device_assets(self, deviceid, include_os: bool = True, include_application: bool = False, include_computersystem: bool = True, include_networkadapter: bool = False, include_device: bool = True, include_processor: bool = True, include_extra: bool = True, json_output: bool = False):
        """
        Retrieves the asset information of a specific device from the N-central server.

        Args:
            deviceid (int): The unique identifier of the device for which to retrieve asset information.
            include_os (bool, optional): If True, includes the OS information in the output. Defaults to False.
            include_application (bool, optional): If True, includes the application information in the output. Defaults to False.
            include_computersystem (bool, optional): If True, includes the computer system information in the output. Defaults to False.
            include_networkadapter (bool, optional): If True, includes the network adapter information in the output. Defaults to False.
            include_device (bool, optional): If True, includes the device information in the output. Defaults to False.
            include_processor (bool, optional): If True, includes the processor information in the output. Defaults to False.
            include_extra (bool, optional): If True, includes the extra information in the output. Defaults to False.
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas DataFrame. Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: A DataFrame or JSON string containing the specified asset information for the device.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        endpoint = f"{self.endpoints['device_assets']}".replace("{deviceid}", str(int(deviceid)))  # Convert to string after casting to int
        response_data = self.get(endpoint)  # Make the GET request for device assets

        selected_data = {}  # Dictionary to hold the selected asset information

        if include_os and "os" in response_data:
            selected_data["os"] = response_data["os"]  # Include OS information
        if include_application and "application" in response_data:
            selected_data["application"] = response_data["application"]  # Include application information
        if include_computersystem and "computersystem" in response_data:
            selected_data["computersystem"] = response_data["computersystem"]  # Include computer system information
        if include_networkadapter and "networkadapter" in response_data:
            selected_data["networkadapter"] = response_data["networkadapter"]  # Include network adapter information
        if include_device and "device" in response_data:
            selected_data["device"] = response_data["device"]  # Include device information
        if include_processor and "processor" in response_data:
            selected_data["processor"] = response_data["processor"]  # Include processor information
        if include_extra and "_extra" in response_data:
            selected_data["_extra"] = response_data["_extra"]  # Include extra information

        return self.handle_output(selected_data, json_output)  # Handle output format

    def new_customer(self, customername, externalid, json_output=False):
        """
        Creates a new customer in the N-central server.

        Args:
            customername (str): The name of the customer to be created.
            externalid (str): An external ID for the customer.
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas DataFrame. 
                                          Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: A DataFrame containing the details of the newly created customer. 
                                      If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        endpoint = self.endpoints['new_customer']  # Retrieve the endpoint for creating a new customer

        clean_name = self.clean_entry(input_string=customername)  # Clean the customer name

        params = {
            "customerName": clean_name,  # Set the customer name
            "contactFirstName": "null",  # Set the contact first name to null
            "contactLastName": "null",  # Set the contact last name to null
            "licenseType": "Professional",  # Set the license type to Professional
            "externalId": externalid,  # Set the external ID
            "phone": "",  # Set the phone to empty
            "contactTitle": "",  # Set the contact title to empty
            "contactEmail": "",  # Set the contact email to empty
            "contactPhone": "",  # Set the contact phone to empty
            "contactPhoneExt": "null",  # Set the contact phone extension to null
            "contactDepartment": "",  # Set the contact department to empty
            "street1": "",  # Set street1 to empty
            "street2": "",  # Set street2 to empty
            "city": "",  # Set city to empty
            "stateProv": "",  # Set state or province to empty
            "country": "",  # Set country to empty
            "postalCode": ""  # Set postal code to empty
        }    

        response_data = self.post(endpoint, params)  # Make the POST request to create a new customer
        return self.handle_output(response_data, json_output)  # Handle output format

    def update_customer_propertie(self, property_id, customerid, property_value: str, json_output: bool = False):
        """
        Updates a specific custom property for a customer in the N-central server. 
        First you need to poll get_organisation_properties to check for property id.

        Args:
            property_id (int): The ID of the custom property to update.
            customerid (int): The unique identifier of the customer whose property is to be updated.
            property_value (str): The new value to set for the custom property.
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas DataFrame. 
                                          Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: A DataFrame containing the updated property details. 
                                      If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        endpoint = f"{self.endpoints['update_customer_property']}".replace("{customerid}", str(customerid)).replace("{property_id}", str(property_id))  # Format the endpoint with customer and property ID

        params = {
            "value": property_value  # Set the new value for the custom property
        }

        response_data = self.put(endpoint, params)  # Call the 'put' method to update the custom property
        return self.handle_output(response_data, json_output)  # Handle output format
        
    def update_customer_contract(self, customerid, property_value: str, json_output: bool = False):
        """
        Updates the contract property for a customer in the N-central server.

        Args:
            customerid (int): The unique identifier of the customer whose contract property is to be updated.
            property_value (str): The new value to set for the contract property.
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas DataFrame. 
                                          Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: A DataFrame containing the updated contract details. 
                                      If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        endpoint = f"{self.endpoints['update_customer_contract']}".replace("{customerid}", str(customerid))  # Format the endpoint with customer ID

        params = {
            "value": property_value  # Set the new value for the contract property
        }

        response_data = self.put(endpoint, params)  # Call the 'put' method to update the contract property
        return self.handle_output(response_data, json_output)  # Handle output format
        
    def update_customer_sla(self, customerid, property_value: str, json_output: bool = False):
        """
        Updates the SLA property for a customer in the N-central server.

        Args:
            customerid (int): The unique identifier of the customer whose SLA property is to be updated.
            property_value (str): The new value to set for the SLA property.
            json_output (bool, optional): If True, returns the output in JSON format as a string. 
                                          If False, returns the output as a pandas DataFrame. 
                                          Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: A DataFrame containing the updated SLA details. 
                                      If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        """
        endpoint = f"{self.endpoints['update_customer_sla']}".replace("{customerid}", str(customerid))  # Format the endpoint with customer ID

        params = {
            "value": property_value  # Set the new value for the SLA property
        }

        response_data = self.put(endpoint, params)  # Call the 'put' method to update the SLA property
        return self.handle_output(response_data, json_output)  # Handle output format
    
    def get_device_filters(self, json_output: bool = False):

        """
        Gives all devices filter in N-central

        Returns:
            Union[str, pd.DataFrame]: A DataFrame containing the updated SLA details. 
                                      If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        
        """
        endpoint = f"{self.endpoints['device_filters']}"  # Set endpoint to device filters

        response_data = self.get(endpoint)  # Make GET request to get device filters
        return self.handle_output(response_data, json_output)  # Handle output format
    
    def get_device_by_filter(self, filter_id, json_output: bool = False):
        
        """
        Args:
            filter_id (int): The unique identifier of the filter to get all devices within the filter.


        Returns:
            Union[str, pd.DataFrame]: A DataFrame containing the updated SLA details. 
                                      If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        
        """
        endpoint = f"{self.endpoints['device_by_filter']}"  # Set endpoint to device by filter

        params = {
            "filterId": filter_id  # Set filter ID as a parameter
        }

        response_data = self.get(endpoint, params)  # Make GET request to get devices by filter
        return self.handle_output(response_data, json_output)  # Handle output format
    

    def get_customer_registration_token(self, customerid: int, json_output: bool = False):

        """
        Args:
            customerid (int): The unique identifier of the filter to get all devices within the filter.


        Returns:
            Union[str, pd.DataFrame]: A DataFrame containing the updated SLA details. 
                                      If `json_output` is True, returns the data in JSON string format instead.

        Raises:
            Exception: If the request fails, an exception with a descriptive error message is raised.
        
        """

        endpoint = f"{self.endpoints['registration_token']}".replace("{customerid}", str(customerid)) # Set endpoint to device by filter

        response_data = self.get(endpoint)  # Make GET request to get devices by filter
        return self.handle_output(response_data, json_output)  # Handle output format
