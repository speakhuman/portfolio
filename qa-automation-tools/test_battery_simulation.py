#!/usr/bin/env python
"""
Battery simulation testing module for web applications.
"""
import os
import json
import time
import warnings
import threading
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Try to import optional dependencies with fallbacks
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    warnings.warn("psutil not available. Resource monitoring will be limited.")

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    warnings.warn("numpy not available. Using standard library alternatives.")
    # Provide basic alternatives for numpy functions we use
    import random
    class NumpyAlternative:
        @staticmethod
        def random_choice(items):
            return random.choice(items)
        @staticmethod
        def random_uniform(low, high):
            return random.uniform(low, high)
    np = NumpyAlternative()

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    warnings.warn("matplotlib not available. Chart generation will be skipped.")


class BatterySimulationTest:
    """Base class for battery simulation testing."""
    
    def __init__(self, url="http://localhost:3000", browser="chrome", headless=True):
        """
        Initialize the battery simulation test.
        
        Args:
            url: URL of the application to test
            browser: Browser to use (chrome or firefox)
            headless: Whether to run in headless mode
        """
        self.url = url
        self.browser = browser
        self.headless = headless
        self.driver = None
        self.results = {
            "summary": {},
            "measurements": []
        }
        self.monitoring = False
        self.monitor_thread = None
        
        # Create reports directory if it doesn't exist
        if not os.path.exists("reports"):
            os.makedirs("reports")
    
    def setup(self):
        """Set up the WebDriver."""
        if self.browser.lower() == "chrome":
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            try:
                self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
            except Exception as e:
                print(f"Error using ChromeDriverManager: {e}")
                print("Trying to use default Chrome driver...")
                self.driver = webdriver.Chrome(options=options)
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")
        
        self.driver.maximize_window()
    
    def teardown(self):
        """Tear down the WebDriver."""
        if self.driver:
            self.driver.quit()
    
    def start_monitoring(self, interval=1.0):
        """
        Start monitoring system resources.
        
        Args:
            interval: Interval between measurements in seconds
        """
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring system resources."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
    
    def _monitor_resources(self, interval):
        """
        Monitor system resources.
        
        Args:
            interval: Interval between measurements in seconds
        """
        start_time = time.time()
        
        while self.monitoring:
            # Initialize measurement with timestamp and elapsed time
            measurement = {
                "timestamp": datetime.now().isoformat(),
                "elapsed_time": time.time() - start_time
            }
            
            # Get CPU and memory usage if psutil is available
            if HAS_PSUTIL:
                try:
                    cpu_percent = psutil.cpu_percent(interval=None)
                    memory = psutil.virtual_memory()
                    
                    measurement.update({
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_used": memory.used,
                        "memory_available": memory.available
                    })
                    
                    # Get battery info if available
                    try:
                        battery = psutil.sensors_battery()
                        if battery:
                            measurement.update({
                                "battery_percent": battery.percent,
                                "battery_power_plugged": battery.power_plugged,
                                "battery_secsleft": battery.secsleft
                            })
                    except (AttributeError, NotImplementedError):
                        pass
                except Exception as e:
                    print(f"Error monitoring resources: {e}")
            else:
                # If psutil is not available, just record basic info
                print("psutil not available. Limited resource monitoring.")
            
            self.results["measurements"].append(measurement)
            
            # Sleep for the specified interval
            time.sleep(interval)
    
    def simulate_user_browsing(self, duration=60, actions=None):
        """
        Simulate user browsing.
        
        Args:
            duration: Duration of the simulation in seconds
            actions: List of actions to perform (if None, default actions will be used)
        """
        if not self.driver:
            self.setup()
        
        print(f"Starting battery simulation test for {duration} seconds...")
        
        # Start monitoring
        self.start_monitoring()
        
        # Navigate to the application
        self.driver.get(self.url)
        print(f"Navigated to {self.url}")
        
        start_time = time.time()
        end_time = start_time + duration
        
        # Default actions if none provided
        if not actions:
            actions = [
                self._scroll_down,
                self._scroll_up,
                self._refresh_page,
                self._click_random_element
            ]
        
        # Perform actions until duration is reached
        action_count = 0
        while time.time() < end_time:
            # Select a random action
            if HAS_NUMPY:
                action = np.random.choice(actions)
            else:
                action = np.random_choice(actions)  # Using our alternative implementation
            
            try:
                # Perform the action
                action()
                action_count += 1
            except Exception as e:
                print(f"Error performing action: {e}")
            
            # Sleep for a random time between 1 and 3 seconds
            if HAS_NUMPY:
                sleep_time = np.random.uniform(1, 3)
            else:
                sleep_time = np.random_uniform(1, 3)  # Using our alternative implementation
                
            time.sleep(sleep_time)
        
        # Stop monitoring
        self.stop_monitoring()
        
        # Calculate metrics
        self._calculate_metrics(action_count)
        
        print(f"Battery simulation test completed. Performed {action_count} actions.")
    
    def _scroll_down(self):
        """Scroll down the page."""
        self.driver.execute_script("window.scrollBy(0, 500);")
        print("Scrolled down")
    
    def _scroll_up(self):
        """Scroll up the page."""
        self.driver.execute_script("window.scrollBy(0, -500);")
        print("Scrolled up")
    
    def _refresh_page(self):
        """Refresh the page."""
        self.driver.refresh()
        print("Refreshed page")
    
    def _click_random_element(self, max_retries=3):
        """
        Click a random clickable element.
        
        Args:
            max_retries: Maximum number of retries for stale element references
        """
        for attempt in range(max_retries):
            try:
                # Find all clickable elements that are visible and enabled
                # Use the newer find_elements method if available
                try:
                    all_elements = self.driver.find_elements(by="css selector",
                        value="a:not([disabled]), button:not([disabled]), input[type='submit']:not([disabled]), input[type='button']:not([disabled])")
                except AttributeError:
                    # Fall back to deprecated method for older selenium versions
                    all_elements = self.driver.find_elements_by_css_selector(
                        "a:not([disabled]), button:not([disabled]), input[type='submit']:not([disabled]), input[type='button']:not([disabled])")
                
                # Filter for visible elements
                visible_elements = []
                for element in all_elements:
                    try:
                        if element.is_displayed():
                            visible_elements.append(element)
                    except:
                        # Skip elements that cause errors when checking visibility
                        continue
                
                if not visible_elements:
                    print("No visible clickable elements found")
                    return
                
                # Select a random element from visible elements
                if HAS_NUMPY:
                    element = np.random.choice(visible_elements)
                else:
                    element = np.random_choice(visible_elements)  # Using our alternative implementation
                
                # Get element info before scrolling (for better error reporting)
                try:
                    tag_name = element.tag_name
                    element_text = element.text[:20] + "..." if len(element.text) > 20 else element.text
                except:
                    tag_name = "unknown"
                    element_text = ""
                
                # Scroll the element into view with some margin
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", element)
                
                # Wait a moment for the scroll to complete
                time.sleep(0.5)
                
                # Try to click using JavaScript first (more reliable for intercepted elements)
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    print(f"Clicked {tag_name} element with JavaScript: {element_text}")
                    return  # Success, exit the method
                except Exception as js_error:
                    # Fall back to regular click if JavaScript click fails
                    try:
                        element.click()
                        print(f"Clicked {tag_name} element: {element_text}")
                        return  # Success, exit the method
                    except Exception as click_error:
                        if attempt < max_retries - 1:
                            print(f"Click attempt {attempt+1} failed, retrying...")
                            time.sleep(0.5)  # Wait before retry
                            continue
                        else:
                            # Last attempt failed, raise the exception
                            raise click_error
            
            except Exception as e:
                if "stale element reference" in str(e) and attempt < max_retries - 1:
                    print(f"Stale element reference on attempt {attempt+1}, retrying...")
                    time.sleep(0.5)  # Wait before retry
                else:
                    print(f"Error clicking random element: {e}")
                    break  # Exit the retry loop on non-stale errors or last attempt
    
    def _calculate_metrics(self, action_count):
        """
        Calculate metrics from the measurements.
        
        Args:
            action_count: Number of actions performed
        """
        measurements = self.results["measurements"]
        
        if not measurements:
            print("No measurements recorded.")
            return
        
        # Initialize metrics with basic information
        metrics = {
            "duration": measurements[-1]["elapsed_time"],
            "action_count": action_count
        }
        
        # Add CPU and memory metrics if psutil was available
        if HAS_PSUTIL and "cpu_percent" in measurements[0]:
            # Extract CPU and memory usage
            cpu_usage = [m.get("cpu_percent", 0) for m in measurements]
            memory_usage = [m.get("memory_percent", 0) for m in measurements]
            
            # Add CPU and memory metrics
            metrics.update({
                "cpu_min": min(cpu_usage),
                "cpu_max": max(cpu_usage),
                "cpu_avg": sum(cpu_usage) / len(cpu_usage),
                "memory_min": min(memory_usage),
                "memory_max": max(memory_usage),
                "memory_avg": sum(memory_usage) / len(memory_usage)
            })
        
        # Add battery metrics if available
        if measurements and "battery_percent" in measurements[0]:
            battery_start = measurements[0]["battery_percent"]
            battery_end = measurements[-1]["battery_percent"]
            battery_drain = battery_start - battery_end
            
            metrics.update({
                "battery_start": battery_start,
                "battery_end": battery_end,
                "battery_drain": battery_drain,
                "battery_drain_per_hour": battery_drain * (3600 / metrics["duration"])
            })
        
        self.results["summary"] = metrics
    
    def save_results(self, filename="battery_test_report.json"):
        """
        Save the test results to a file.
        
        Args:
            filename: Name of the file to save the results to
        """
        filepath = os.path.join("reports", filename)
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2)
    
    def generate_charts(self, filename_prefix="battery_test"):
        """
        Generate charts from the measurements.
        
        Args:
            filename_prefix: Prefix for the chart filenames
        """
        if not HAS_MATPLOTLIB:
            print("Matplotlib not available. Skipping chart generation.")
            self._generate_csv_reports(filename_prefix)
            return
            
        measurements = self.results["measurements"]
        
        if not measurements:
            print("No measurements to generate charts from.")
            return
        
        # Extract data
        timestamps = [m["elapsed_time"] for m in measurements]
        
        # Create CPU usage chart if psutil is available
        if HAS_PSUTIL:
            cpu_usage = [m.get("cpu_percent", 0) for m in measurements]
            memory_usage = [m.get("memory_percent", 0) for m in measurements]
            
            # Create CPU usage chart
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, cpu_usage)
            plt.title("CPU Usage Over Time")
            plt.xlabel("Time (seconds)")
            plt.ylabel("CPU Usage (%)")
            plt.grid(True)
            plt.savefig(os.path.join("reports", f"{filename_prefix}_cpu.png"))
            
            # Create memory usage chart
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, memory_usage)
            plt.title("Memory Usage Over Time")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Memory Usage (%)")
            plt.grid(True)
            plt.savefig(os.path.join("reports", f"{filename_prefix}_memory.png"))
        
        # Create battery usage chart if available
        if measurements and "battery_percent" in measurements[0]:
            battery_usage = [m.get("battery_percent", 0) for m in measurements]
            
            plt.figure(figsize=(10, 6))
            plt.plot(timestamps, battery_usage)
            plt.title("Battery Level Over Time")
            plt.xlabel("Time (seconds)")
            plt.ylabel("Battery Level (%)")
            plt.grid(True)
            plt.savefig(os.path.join("reports", f"{filename_prefix}_battery.png"))
    
    def _generate_csv_reports(self, filename_prefix="battery_test"):
        """
        Generate CSV reports as an alternative to charts.
        
        Args:
            filename_prefix: Prefix for the CSV filenames
        """
        measurements = self.results["measurements"]
        
        if not measurements:
            print("No measurements to generate reports from.")
            return
            
        # Create CSV file
        csv_path = os.path.join("reports", f"{filename_prefix}_data.csv")
        
        with open(csv_path, "w") as f:
            # Write header
            headers = ["timestamp", "elapsed_time"]
            
            if HAS_PSUTIL:
                headers.extend(["cpu_percent", "memory_percent", "memory_used", "memory_available"])
                
            if "battery_percent" in measurements[0]:
                headers.extend(["battery_percent", "battery_power_plugged"])
                
            f.write(",".join(headers) + "\n")
            
            # Write data
            for m in measurements:
                row = [
                    m.get("timestamp", ""),
                    str(m.get("elapsed_time", 0))
                ]
                
                if HAS_PSUTIL:
                    row.extend([
                        str(m.get("cpu_percent", 0)),
                        str(m.get("memory_percent", 0)),
                        str(m.get("memory_used", 0)),
                        str(m.get("memory_available", 0))
                    ])
                    
                if "battery_percent" in m:
                    row.extend([
                        str(m.get("battery_percent", 0)),
                        str(m.get("battery_power_plugged", False))
                    ])
                    
                f.write(",".join(row) + "\n")
                
        print(f"CSV report generated: {csv_path}")
    
    def print_summary(self):
        """Print a summary of the battery simulation test results."""
        metrics = self.results["summary"]
        
        print("\n=== Battery Simulation Test Summary ===")
        print(f"Duration: {metrics.get('duration', 0):.2f} seconds")
        print(f"Actions performed: {metrics.get('action_count', 0)}")
        
        # Print CPU and memory metrics if available
        if "cpu_avg" in metrics:
            print(f"CPU usage: {metrics.get('cpu_avg', 0):.2f}% (min: {metrics.get('cpu_min', 0):.2f}%, max: {metrics.get('cpu_max', 0):.2f}%)")
        
        if "memory_avg" in metrics:
            print(f"Memory usage: {metrics.get('memory_avg', 0):.2f}% (min: {metrics.get('memory_min', 0):.2f}%, max: {metrics.get('memory_max', 0):.2f}%)")
        
        # Print battery metrics if available
        if "battery_drain" in metrics:
            print(f"Battery drain: {metrics.get('battery_drain', 0):.2f}% ({metrics.get('battery_drain_per_hour', 0):.2f}% per hour)")
        
        # Print a message if no resource metrics were collected
        if "cpu_avg" not in metrics and "memory_avg" not in metrics and "battery_drain" not in metrics:
            print("No resource metrics were collected. Install psutil for resource monitoring.")


def test_battery_simulation():
    """Run a battery simulation test."""
    test = BatterySimulationTest()
    try:
        test.simulate_user_browsing(duration=30)  # Short duration for demonstration
        test.save_results()
        test.generate_charts()
        test.print_summary()
    finally:
        test.teardown()


if __name__ == "__main__":
    test_battery_simulation()