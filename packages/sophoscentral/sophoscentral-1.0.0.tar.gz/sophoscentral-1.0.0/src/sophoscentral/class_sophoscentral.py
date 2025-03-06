import requests
import base64
import json
import pandas as pd
import time

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

class SCentralConnection:
    
    BASE_URL = "https://api.central.sophos.com"
    AUTH_URL = "https://id.sophos.com"
    API_HOST = "https://api-eu02.central.sophos.com"

    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.access_token_expiry = None
        self.get_tokens()  # Changed from get_access_token to get_tokens for consistency
        self.partner_id = self.WhoAmI()
        self.page_size = 50
        print(f"Partner ID ingesteld: {self.partner_id}")

    def get_tokens(self):
        """
        Retrieves the access token and sets expiry time by authenticating with Sophos Central.
        """
        data = f"grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}&scope=token"
        url = f"{self.AUTH_URL}/api/v2/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        response = requests.post(url, headers=headers, data=data)

        if response.status_code == 200:
            print("Authentication successful.")
            data = response.json()
            self.access_token = data["access_token"]
            expiry_seconds = data.get("expires_in", 3600)
            self.access_token_expiry = int(time.time()) + expiry_seconds
            print(f"Token will expire in {expiry_seconds} seconds")
        else:
            error_handler = apierrorhandler(response)
            error_handler.handle_error()

    def is_token_expired(self):
        """
        Checks if the access token has expired or is near expiry.
        Returns True if the token is expired or near expiry (within 5 minutes), otherwise False.
        """
        if self.access_token_expiry is None:
            return True

        current_time = int(time.time())
        # Add 5-minute buffer before expiry
        return current_time >= self.access_token_expiry - 300


    def WhoAmI(self):
        """
        Haalt de huidige gebruiker op via een directe requests.get call, zonder gebruik te maken van self.get().
        """
        url = f"{self.BASE_URL}/whoami/v1"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return data["id"]  # Haal de partner_id op
        else:
            error_handler = APIErrorHandler(response)
            error_handler.handle_error()

    def get(self, endpoint, extra_params=None, extra_headers=None, debug=False):
        """
        Makes a GET request to the Sophos Central API and handles pagination.
        Automatically adds the X-Tenant-ID header if partner_id is available.
        """

        if self.is_token_expired():  # Check if the token has expired
            print("Access token expired, refreshing token...")
            self.get_tokens()  # Refresh the access token if expired
            
        responses = []
        pageFromKey = None  # For key-based pagination
        page = 1  # For number-based pagination (if needed)
        
        # Initialize the params dictionary
        params = extra_params if extra_params else {}

        # Add common params to the request
        params.update({"pageSize": 50, "pageTotal": True})
        print(params)
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }

        if extra_headers:
            headers.update(extra_headers)

        retries = 0
        backoff_times = [30, 300, 3650]  # List of backoff times in seconds (30s, 5m, 1h)

        while retries < 3:
            try:
                # Reset pagination per retry attempt
                pageFromKey = None  # Reset key pagination before retry

                while True:
                    # Handle pagination dynamically from response
                    if pageFromKey:
                        params["pageFromKey"] = pageFromKey
                    else:
                        params["page"] = page  # Add page number if applicable

                    # Make the GET request
                    response = requests.get(url=endpoint, headers=headers, params=params)

                    if debug:
                        print(f"Request URL: {response.url}")
                        print(f"Request Headers: {headers}")
                        print(f"Request Params: {params}")
                        print(f"Response Status Code: {response.status_code}")

                    # Check for valid response
                    if response.status_code == 200:
                        try:
                            data = response.json()  # Attempt to parse JSON response
                        except ValueError:
                            print("Error parsing JSON response")
                            break

                        if debug:
                            print(f"Response JSON: {data}")
                            print(f"Full Response Text: {response.text}")

                        if "items" in data:
                            # Add items to the responses list
                            responses.extend(data["items"])
                        else:
                            print("No 'items' in the response")

                        # Handle pagination logic dynamically based on the response
                        if "pages" in data:
                            pagingInfo = data["pages"]

                            # Check for key-based pagination
                            if "nextKey" in pagingInfo:
                                #print("Key-based pagination detected")
                                pageFromKey = pagingInfo.get("nextKey")
                                if not pageFromKey:
                                    break  # No next page, exit loop
                            elif "current" in pagingInfo and "total" in pagingInfo:
                                # Number-based pagination
                                pageTotal = pagingInfo.get("total")

                                if page >= pageTotal:
                                    break  # All pages processed, exit loop
                                time.sleep(2)
                                page += 1  # Increment page number for next request
                            else:
                                # No pagination detected (single response)
                                break
                        else:
                            # If no pagination info in response, exit loop
                            break
                    else:
                        print(f"Error response text: {response.text}")
                        raise Exception(f"Request failed with status code: {response.status_code}")

                # If we get here, the request was successful; break out of retry loop
                break

            except requests.RequestException as error:
                retries += 1
                print(f"Request failed (Attempt {retries}/3): {error}")

                # If we've retried 3 times, raise the exception
                if retries == 3:
                    print("Max retries reached, raising error.")
                    raise

                # Wait before retrying (based on the retry count)
                backoff_time = backoff_times[retries - 1]  # Get the appropriate backoff time
                print(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)

        return responses

    def handle_output(self, response_data, json_output=False):
        """
        Handles the output format for API responses.
        """

        if json_output:
            return json.dumps(response_data, indent=4)  # Return as a JSON string
        else:
            df = pd.json_normalize(response_data)  # Convert JSON data to a pandas DataFrame
            return df


    def get_partner_tenants(self, json_output=False):
        """
        Retrieves the partner tenants from the Sophos Central API.

        Args:
            json_output (bool, optional): If True, returns the output in JSON format. Defaults to False.

        Returns:
            Union[str, pd.DataFrame]: The tenants' data in JSON string format or as a pandas DataFrame.
        """
        endpoint = f"{self.BASE_URL}/partner/v1/tenants?pageTotal=true"

        headers = {
            "X-Partner-ID": f"{self.partner_id}"
        }

        response_data = self.get(endpoint, extra_headers=headers)

        # Transform the 'products' field to a comma-separated string if it exists
        for item in response_data:
            if 'products' in item and isinstance(item['products'], list):
                # Convert the list of dictionaries in 'products' to a comma-separated string of 'code' values
                item['products'] = ', '.join([product['code'] for product in item['products']])

        return self.handle_output(response_data, json_output)

    
    def get_tenant_endpoints(self, tenant_id=None, json_output=False):
        time.sleep(1)
        endpoint = f"{self.API_HOST}/endpoint/v1/endpoints"

        headers = {
            "X-Tenant-ID": f"{tenant_id}"
        }

        response_data = self.get(endpoint, extra_headers=headers)

        return self.handle_output(response_data, json_output)
    
    def post(self, endpoint, extra_headers, extra_params, debug=False):
        """
        Makes a POST request to the specified API endpoint.

        Args:
            endpoint (str): The API endpoint URL.
            extra_headers (dict): Additional headers for the request.
            extra_params (dict): The parameters for the POST request.
            debug (bool, optional): If True, prints debug information. Defaults to False.

        Returns:
            requests.Response: The response object from the POST request.
        """

        headers = {
            "Authorization": f"Bearer {self.access_token}",  # Authorization header with the access token.
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        if extra_headers:
            headers.update(extra_headers)  # Updates headers with additional headers if provided.

        if debug:
            print("Extra Headers:", extra_headers)
            print("Headers:", headers)
            print("Endpoint:", endpoint)
            print("Extra Params:", extra_params)

        response = requests.post(url=endpoint, headers=headers, json=extra_params)  # Sends POST request.

        if response.status_code == 201:
            print("Post successful")
        else:
            print(f"Error response text: {response.text}")
            raise Exception(f"Request failed with status code: {response.status_code}")
        
        if debug:
            print(response.json)

        return response  # Returns response from POST request.

    def put(self, endpoint, extra_headers, extra_params, debug=False):
        """
        Makes a PUT request to the specified API endpoint.

        Args:
            endpoint (str): The API endpoint URL.
            extra_headers (dict): Additional headers for the request.
            extra_params (dict): The parameters for the PUT request.
            debug (bool, optional): If True, prints debug information. Defaults to False.

        Returns:
            requests.Response: The response object from the PUT request.
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        if extra_headers:
            headers.update(extra_headers)

        if debug:
            print("Extra Headers:", extra_headers)
            print("Headers:", headers)
            print("Endpoint:", endpoint)
            print("Extra Params:", extra_params)

        response = requests.put(url=endpoint, headers=headers, json=extra_params)

        return response

    def create_email(self, customer_name):
        """
        Creates an email address based on the provided customer name, including the part before the underscore.

        Args:
            customer_name (str): The name of the customer.

        Returns:
            str: The generated email address.
        """
        split = customer_name.split('_')  # Splits the customer name by underscores.

        customer = split[0] + split[1]  # Combines the part before and after the underscore.
        customer = customer.replace("&", "").replace("/", "").replace("\"", "").replace("'", "").replace(".", "").replace(",", "").replace("(", "").replace(")", "")  # Removes unwanted characters.
        customer = customer.strip()  # Trims leading and trailing spaces.
        customer = customer[:15]  # Limits the customer name to 15 characters.
        created_email = f"{customer.lower()}@tosch.nl"  # Creates the email address.

        return created_email  # Returns the created email address.

    def new_partner_tenant(self, customer_name):
        """
        Creates a new partner tenant in the Sophos Central system.

        Args:
            customer_name (str): The name of the customer to create.

        Returns:
            requests.Response: The response data from the API request to create a new tenant.
        """
        endpoint = f"{self.BASE_URL}/partner/v1/tenants"  # API endpoint for creating a new tenant.

        headers = {
            "X-Partner-ID": f"{self.partner_id}"  # Adds partner ID to request headers.
        }

        create_email = self.create_email(customer_name=customer_name)  # Generates contact email using customer name.

        params = {
            "name": customer_name,
            "dataGeography": "DE",  # Specifies data geography as Germany (DE).
            "contact": {
                "firstName": "Ronny",
                "lastName": "Morren",
                "email": create_email,  # Adds generated email as contact email.
                "phone": "0342425200",
                "address": {
                    "address1": "Industrieweg 4",
                    "city": "Barneveld",
                    "countryCode": "NL",
                    "postalCode": "3771MD"
                }
            },
            "billingType": "trial"  # Sets billing type to "trial".
        }

        response_data = self.post(endpoint, extra_params=params, extra_headers=headers)  # Sends POST request to create tenant.

        return response_data
     
    def migrate_endpoint(self, hostnames, afasnr_sender, afasnr_receiver):
        """
        Migrates an endpoint from one tenant to another based on the hostname and AFAS numbers.

        Args:
            hostnames (str): A comma-separated string of hostnames to be migrated.
            afasnr_sender (str): The AFAS number of the sender tenant.
            afasnr_receiver (str): The AFAS number of the receiver tenant.

        Returns:
            None
        """
        # Fetch all tenants
        all_tenants = self.get_partner_tenants()  # Retrieve all tenant information.
        print("Tenants collected")

        # If handle_output returns a DataFrame, ensure it's in the correct format
        if isinstance(all_tenants, pd.DataFrame):
            tenants_df = all_tenants
        else:
            tenants_df = pd.json_normalize(all_tenants)

        # Split the comma-separated hostnames, strip whitespace, and create a list of hostnames
        endpoints_list = [hostname.strip() for hostname in hostnames.split(',')]
        print("Endpoints:", endpoints_list)

        # Select the tenant where the name contains afasnr_sender
        sender_tenant = tenants_df[tenants_df['name'].str.contains(afasnr_sender, case=False, na=False)]
        if sender_tenant.empty:
            raise Exception(f"No tenant found with name containing '{afasnr_sender}'.")
        sender_tenant_id = sender_tenant.iloc[0]['id']
        print("Sender found", sender_tenant_id)

        # Select the tenant where the name contains afasnr_receiver
        receiver_tenant = tenants_df[tenants_df['name'].str.contains(afasnr_receiver, case=False, na=False)]
        if receiver_tenant.empty:
            raise Exception(f"No tenant found with name containing '{afasnr_receiver}'.")
        receiver_tenant_id = receiver_tenant.iloc[0]['id']
        print("Receiver found", receiver_tenant_id)

        # Get the endpoints for the sender tenant
        print("Searching for endpoint:", endpoints_list)
        sender_endpoints = self.get_tenant_endpoints(tenant_id=sender_tenant_id)
        if isinstance(sender_endpoints, pd.DataFrame):
            endpoints_df = sender_endpoints
        else:
            endpoints_df = pd.json_normalize(sender_endpoints)

        # For each hostname, get the endpoint ID
        endpoint_ids = []
        for hostname in endpoints_list:
            matching_endpoint = endpoints_df[endpoints_df['hostname'].str.lower() == hostname.lower()]
            if not matching_endpoint.empty:
                endpoint_ids.append(matching_endpoint.iloc[0]['id'])
            else:
                raise Exception(f"Endpoint with hostname '{hostname}' not found in sender tenant.")

        print("All endpoints were found with IDs:", endpoint_ids)

        # Prepare receiving tenant for endpoint migration
        endpoint = f"{self.API_HOST}/endpoint/v1/migrations"
        print("Migration Endpoint:", endpoint_ids)

        receiver_headers = {
            "X-Tenant-ID": receiver_tenant_id
        }
        print("Sender params", receiver_headers)

        sender_params = {
            "fromTenant": sender_tenant_id,
            "endpoints": endpoint_ids
        }
        print("Sender params", sender_params)
        
        # Send a POST request to initialize the migration
        response_sender = self.post(endpoint=endpoint, extra_headers=receiver_headers, extra_params=sender_params)
        
        if response_sender.status_code in [200, 201]:
            response_data = response_sender.json()
            job_id = response_data.get("id")
            print("Job ID", job_id)
            job_token = response_data.get("token")
            print("Job Token", job_token)
        else:
            print(f"Failed to initiate migration: {response_sender.status_code} - {response_sender.text}")
            return

        # Prepare sending tenant for endpoint migration using the job ID and token
        endpoint = f"{self.API_HOST}/endpoint/v1/migrations/{job_id}"

        sender_headers = {
            "X-Tenant-ID": sender_tenant_id
        }
        print("Sender headers", sender_headers)
        receiver_params = {
            "token": job_token,
            "endpoints": endpoint_ids
        }
        print("reciever params", receiver_params)
        
        # Send a PUT request to finalize the migration
        response_receiver = self.put(endpoint=endpoint, extra_headers=sender_headers, extra_params=receiver_params)

        print(response_receiver.status_code)
        print("Migration successful")
        return response_receiver.json()
    

    def get_tenant_queries(self, tenant_id, json_output=False):
        
        endpoint = f"{self.API_HOST}/live-discover/v1/queries"

        headers = {
            "X-Tenant-ID": f"{tenant_id}"
        }

        response_data = self.get(endpoint, extra_headers=headers)

        return self.handle_output(response_data, json_output)

    
    def get_tenant_queries_runs(self, tenant_id, query_id, json_output=False):

        endpoint = f"{self.API_HOST}/live-discover/v1/queries/runs"

        headers = {
            "X-Tenant-ID": f"{tenant_id}"
        }

        extra_params = {
        "queryId": f"{query_id}",
        "sort": "createdAt"
        }

        response_data = self.get(endpoint, extra_headers=headers, extra_params=extra_params)

        return self.handle_output(response_data, json_output)
    
    def post_tenant_queries_runs(self, tenant_id, query_id, endpoints, json_output=False):

        endpoint = f"{self.API_HOST}/live-discover/v1/queries/runs"

        headers = {
            "X-Tenant-ID": tenant_id
        }

        extra_params = {
            "matchEndpoints": {
                "filters": [
                {
                    "ids": endpoints
                }
                ]
            },
            "savedQuery": {
                "queryId": query_id,
            }
        }

        response_data = self.post(endpoint, extra_headers=headers, extra_params=extra_params)

        return self.handle_output(response_data, json_output)


    def get_tenant_queries_run_results(self, tenant_id, run_query_id, json_output=False):

        endpoint = f"{self.API_HOST}/live-discover/v1/queries/runs/{run_query_id}/results"

        headers = {
            "X-Tenant-ID": f"{tenant_id}"
        }

        response_data = self.get(endpoint, extra_headers=headers)

        return self.handle_output(response_data, json_output)
    


        