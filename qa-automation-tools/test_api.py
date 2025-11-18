#!/usr/bin/env python
"""
API testing module for web applications.
"""
import os
import json
import time
import requests
import jsonschema
import pytest
import argparse

class APITest:
    """Base class for API testing."""
    
    def __init__(self, base_url="http://localhost:3000/api", headers=None):
        """
        Initialize the API test.
        
        Args:
            base_url: Base URL of the API to test
            headers: Headers to include in all requests
        """
        self.base_url = base_url
        self.headers = headers or {}
        self.results = {}
        self.session = requests.Session()
        
        # Create reports directory if it doesn't exist
        if not os.path.exists("reports"):
            os.makedirs("reports")
    
    def get(self, endpoint, params=None):
        """
        Send a GET request to the API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
        
        Returns:
            requests.Response: The response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = time.time()
        response = self.session.get(url, headers=self.headers, params=params)
        end_time = time.time()
        
        self._log_request("GET", url, None, params, response, end_time - start_time)
        return response
    
    def post(self, endpoint, data=None, json_data=None):
        """
        Send a POST request to the API.
        
        Args:
            endpoint: API endpoint to call
            data: Form data
            json_data: JSON data
        
        Returns:
            requests.Response: The response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = time.time()
        response = self.session.post(url, headers=self.headers, data=data, json=json_data)
        end_time = time.time()
        
        self._log_request("POST", url, json_data or data, None, response, end_time - start_time)
        return response
    
    def put(self, endpoint, data=None, json_data=None):
        """
        Send a PUT request to the API.
        
        Args:
            endpoint: API endpoint to call
            data: Form data
            json_data: JSON data
        
        Returns:
            requests.Response: The response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = time.time()
        response = self.session.put(url, headers=self.headers, data=data, json=json_data)
        end_time = time.time()
        
        self._log_request("PUT", url, json_data or data, None, response, end_time - start_time)
        return response
    
    def delete(self, endpoint, params=None):
        """
        Send a DELETE request to the API.
        
        Args:
            endpoint: API endpoint to call
            params: Query parameters
        
        Returns:
            requests.Response: The response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        start_time = time.time()
        response = self.session.delete(url, headers=self.headers, params=params)
        end_time = time.time()
        
        self._log_request("DELETE", url, None, params, response, end_time - start_time)
        return response
    
    def _log_request(self, method, url, data, params, response, duration):
        """Log the request and response."""
        request_id = len(self.results) + 1
        
        self.results[request_id] = {
            "request": {
                "method": method,
                "url": url,
                "data": data,
                "params": params,
                "headers": self.headers
            },
            "response": {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": self._get_response_body(response),
                "duration": duration
            }
        }
    
    def _get_response_body(self, response):
        """Get the response body as a dictionary or string."""
        try:
            return response.json()
        except ValueError:
            return response.text
    
    def validate_schema(self, response, schema):
        """
        Validate the response against a JSON schema.
        
        Args:
            response: Response object or JSON data
            schema: JSON schema to validate against
        
        Returns:
            bool: True if valid, False otherwise
        """
        if isinstance(response, requests.Response):
            try:
                data = response.json()
            except ValueError:
                return False
        else:
            data = response
        
        try:
            jsonschema.validate(instance=data, schema=schema)
            return True
        except jsonschema.exceptions.ValidationError:
            return False
    
    def assert_status_code(self, response, expected_status_code):
        """
        Assert that the response has the expected status code.
        
        Args:
            response: Response object
            expected_status_code: Expected status code
        """
        assert response.status_code == expected_status_code, \
            f"Expected status code {expected_status_code}, got {response.status_code}"
    
    def assert_json_value(self, response, path, expected_value):
        """
        Assert that the JSON response has the expected value at the given path.
        
        Args:
            response: Response object
            path: JSON path (e.g., "data.0.id")
            expected_value: Expected value
        """
        try:
            data = response.json()
        except ValueError:
            assert False, "Response is not valid JSON"
        
        # Navigate the path
        for key in path.split("."):
            if key.isdigit():
                key = int(key)
            try:
                data = data[key]
            except (KeyError, IndexError):
                assert False, f"Path {path} not found in response"
        
        assert data == expected_value, \
            f"Expected value {expected_value} at path {path}, got {data}"
    
    def save_results(self, filename="api_validation_report.json"):
        """
        Save the test results to a file.
        
        Args:
            filename: Name of the file to save the results to
        """
        filepath = os.path.join("reports", filename)
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
    
    def print_summary(self):
        """Print a summary of the API test results."""
        print("\n=== API Test Summary ===")
        
        total_requests = len(self.results)
        successful_requests = sum(1 for req in self.results.values() 
                                if 200 <= req["response"]["status_code"] < 300)
        failed_requests = total_requests - successful_requests
        
        print(f"Total requests: {total_requests}")
        print(f"Successful requests: {successful_requests}")
        print(f"Failed requests: {failed_requests}")
        
        if failed_requests > 0:
            print("\nFailed requests:")
            for req_id, req in self.results.items():
                if not (200 <= req["response"]["status_code"] < 300):
                    print(f"  - {req['request']['method']} {req['request']['url']}: {req['response']['status_code']}")


def test_homepage(base_url="http://localhost:3000"):
    """Test the GET / endpoint (homepage)."""
    api_test = APITest(base_url=base_url)
    response = api_test.get("")  # Test the root endpoint
    api_test.assert_status_code(response, 200)
    api_test.save_results()
    api_test.print_summary()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run API tests")
    parser.add_argument("--url", default="http://localhost:3000", help="Base URL to test")
    args = parser.parse_args()
    
    test_homepage(args.url)