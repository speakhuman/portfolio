#!/usr/bin/env python
"""
Performance testing module for web applications.
"""
import os
import json
import time
import statistics
import requests
import warnings
from datetime import datetime

# Try to import gevent for concurrent testing, but provide fallback
try:
    import gevent
    HAS_GEVENT = True
except ImportError:
    HAS_GEVENT = False
    warnings.warn("gevent not available. Concurrent testing will be limited.")


class PerformanceTest:
    """Base class for performance testing."""
    
    def __init__(self, base_url="http://localhost:3000", headers=None):
        """
        Initialize the performance test.
        
        Args:
            base_url: Base URL of the application to test
            headers: Headers to include in all requests
        """
        self.base_url = base_url
        self.headers = headers or {}
        self.results = {
            "summary": {},
            "requests": []
        }
        self.session = requests.Session()
        
        # Create reports directory if it doesn't exist
        if not os.path.exists("reports"):
            os.makedirs("reports")
    
    def measure_page_load(self, path="", num_requests=10, delay=1):
        """
        Measure the page load time.
        
        Args:
            path: Path to the page to test
            num_requests: Number of requests to make
            delay: Delay between requests in seconds
        
        Returns:
            dict: Performance metrics
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        load_times = []
        
        print(f"Testing page load performance for {url}")
        print(f"Making {num_requests} requests with {delay}s delay between requests...")
        
        for i in range(num_requests):
            start_time = time.time()
            response = self.session.get(url, headers=self.headers)
            end_time = time.time()
            
            load_time = end_time - start_time
            load_times.append(load_time)
            
            self.results["requests"].append({
                "url": url,
                "status_code": response.status_code,
                "load_time": load_time,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"Request {i+1}/{num_requests}: {load_time:.4f}s")
            
            if i < num_requests - 1:
                time.sleep(delay)
        
        # Calculate metrics
        metrics = {
            "url": url,
            "num_requests": num_requests,
            "min_time": min(load_times),
            "max_time": max(load_times),
            "avg_time": statistics.mean(load_times),
            "median_time": statistics.median(load_times),
            "p90_time": self._percentile(load_times, 90),
            "p95_time": self._percentile(load_times, 95),
            "p99_time": self._percentile(load_times, 99),
            "std_dev": statistics.stdev(load_times) if len(load_times) > 1 else 0
        }
        
        self.results["summary"] = metrics
        return metrics
    
    def _percentile(self, data, percentile):
        """Calculate the percentile value."""
        sorted_data = sorted(data)
        index = (len(sorted_data) - 1) * percentile / 100
        floor = int(index)
        ceil = min(floor + 1, len(sorted_data) - 1)
        if floor == ceil:
            return sorted_data[floor]
        return sorted_data[floor] * (ceil - index) + sorted_data[ceil] * (index - floor)
    
    def measure_api_performance(self, endpoint, method="GET", data=None, num_requests=10, delay=1):
        """
        Measure the API performance.
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method to use
            data: Data to send with the request
            num_requests: Number of requests to make
            delay: Delay between requests in seconds
        
        Returns:
            dict: Performance metrics
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response_times = []
        
        print(f"Testing API performance for {method} {url}")
        print(f"Making {num_requests} requests with {delay}s delay between requests...")
        
        for i in range(num_requests):
            start_time = time.time()
            
            if method.upper() == "GET":
                response = self.session.get(url, headers=self.headers)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            end_time = time.time()
            
            response_time = end_time - start_time
            response_times.append(response_time)
            
            self.results["requests"].append({
                "url": url,
                "method": method,
                "status_code": response.status_code,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"Request {i+1}/{num_requests}: {response_time:.4f}s")
            
            if i < num_requests - 1:
                time.sleep(delay)
        
        # Calculate metrics
        metrics = {
            "url": url,
            "method": method,
            "num_requests": num_requests,
            "min_time": min(response_times),
            "max_time": max(response_times),
            "avg_time": statistics.mean(response_times),
            "median_time": statistics.median(response_times),
            "p90_time": self._percentile(response_times, 90),
            "p95_time": self._percentile(response_times, 95),
            "p99_time": self._percentile(response_times, 99),
            "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0
        }
        
        self.results["summary"] = metrics
        return metrics
    
    def save_results(self, filename="performance_report.json"):
        """
        Save the test results to a file.
        
        Args:
            filename: Name of the file to save the results to
        """
        filepath = os.path.join("reports", filename)
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
    
    def print_summary(self):
        """Print a summary of the performance test results."""
        metrics = self.results["summary"]
        
        print("\n=== Performance Test Summary ===")
        print(f"URL: {metrics.get('url', 'N/A')}")
        print(f"Method: {metrics.get('method', 'GET')}")
        print(f"Number of requests: {metrics.get('num_requests', 0)}")
        print(f"Minimum response time: {metrics.get('min_time', 0):.4f}s")
        print(f"Maximum response time: {metrics.get('max_time', 0):.4f}s")
        print(f"Average response time: {metrics.get('avg_time', 0):.4f}s")
        print(f"Median response time: {metrics.get('median_time', 0):.4f}s")
        print(f"90th percentile: {metrics.get('p90_time', 0):.4f}s")
        print(f"95th percentile: {metrics.get('p95_time', 0):.4f}s")
        print(f"99th percentile: {metrics.get('p99_time', 0):.4f}s")
        print(f"Standard deviation: {metrics.get('std_dev', 0):.4f}s")


def test_homepage_performance():
    """Test the performance of the homepage."""
    perf_test = PerformanceTest()
    perf_test.measure_page_load(path="/", num_requests=5, delay=1)
    perf_test.save_results()
    perf_test.print_summary()


if __name__ == "__main__":
    test_homepage_performance()