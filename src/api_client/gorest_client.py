# gorest_api_tests/src/api_client/gorest_client.py
import requests
import time
from requests import Response

class GoRestClient:
    """
    A high-level wrapper for interacting with the GoRest API.
    Handles HTTP requests, authentication headers, and provides methods
    for common CRUD operations.
    """

    def __init__(self, base_url: str, token: str):
        """
        Initializes the GoRestClient.

        Args:
            base_url (str): The base URL of the GoRest API (e.g., "https://gorest.co.in/public/v2").
            token (str): The Bearer token for API authentication.
        """
        self.base_url = base_url
        self.token = token
        self.session = requests.Session() # Use a session for connection pooling and efficiency
        self.max_rate_limit_retries = 2

    def _get_headers(self, authenticated: bool = True) -> dict:
        """
        Constructs the HTTP headers for API requests.

        Args:
            authenticated (bool): If True, includes the Authorization header.

        Returns:
            dict: A dictionary of HTTP headers.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if authenticated:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, endpoint: str, payload: dict = None, authenticated: bool = True) -> Response:
        """
        Sends an HTTP request to the GoRest API.

        Args:
            method (str): The HTTP method (e.g., "GET", "POST", "PATCH", "DELETE").
            endpoint (str): The API endpoint path (e.g., "/users").
            payload (dict, optional): The request body for POST/PATCH requests. Defaults to None.
            authenticated (bool): If True, includes the Authorization header.

        Returns:
            requests.Response: The response object from the API.
        """
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(authenticated)

        for attempt in range(self.max_rate_limit_retries + 1):
            try:
                if payload:
                    response = self.session.request(method, url, json=payload, headers=headers)
                else:
                    response = self.session.request(method, url, headers=headers)

                if response.status_code == 429 and attempt < self.max_rate_limit_retries:
                    reset_seconds = int(response.headers.get("x-ratelimit-reset", "1"))
                    time.sleep(max(reset_seconds, 1))
                    continue

                response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            except requests.exceptions.HTTPError as e:
                # Catch HTTP errors and return the response for specific error assertions in tests
                return e.response
            except requests.exceptions.RequestException as e:
                # Catch other request exceptions (e.g., network issues)
                print(f"Request failed: {e}")
                raise
            return response

    def post(self, endpoint: str, payload: dict, authenticated: bool = True) -> Response:
        """
        Sends a POST request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint path.
            payload (dict): The request body.
            authenticated (bool): If True, includes the Authorization header.

        Returns:
            requests.Response: The response object.
        """
        return self._request("POST", endpoint, payload, authenticated)

    def get(self, endpoint: str, authenticated: bool = True) -> Response:
        """
        Sends a GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint path.
            authenticated (bool): If True, includes the Authorization header.

        Returns:
            requests.Response: The response object.
        """
        return self._request("GET", endpoint, authenticated=authenticated)

    def patch(self, endpoint: str, payload: dict, authenticated: bool = True) -> Response:
        """
        Sends a PATCH request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint path.
            payload (dict): The request body.
            authenticated (bool): If True, includes the Authorization header.

        Returns:
            requests.Response: The response object.
        """
        return self._request("PATCH", endpoint, payload, authenticated)

    def delete(self, endpoint: str, authenticated: bool = True) -> Response:
        """
        Sends a DELETE request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint path.
            authenticated (bool): If True, includes the Authorization header.

        Returns:
            requests.Response: The response object.
        """
        return self._request("DELETE", endpoint, authenticated=authenticated)
