#!/usr/bin/env python
"""
Accessibility testing module for web applications.
"""
import os
import json
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from axe_selenium_python import Axe


class AccessibilityTest:
    """Base class for accessibility testing."""
    
    def __init__(self, url="http://localhost:3000", browser="chrome", headless=True):
        """
        Initialize the accessibility test.
        
        Args:
            url: Base URL of the application to test
            browser: Browser to use (chrome or firefox)
            headless: Whether to run in headless mode
        """
        self.url = url
        self.browser = browser
        self.headless = headless
        self.driver = None
        self.results = {}
    
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
        elif self.browser.lower() == "firefox":
            options = webdriver.FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            try:
                self.driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
            except Exception as e:
                print(f"Error using GeckoDriverManager: {e}")
                print("Trying to use default Firefox driver...")
                self.driver = webdriver.Firefox(options=options)
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")
        
        self.driver.maximize_window()
    
    def teardown(self):
        """Tear down the WebDriver."""
        if self.driver:
            self.driver.quit()
    
    def navigate_to(self, path=""):
        """Navigate to a specific path on the site."""
        url = f"{self.url}/{path.lstrip('/')}"
        self.driver.get(url)
        return self
    
    def run_axe(self, name=None):
        """
        Run axe accessibility tests on the current page.
        
        Args:
            name: Name for the report file (defaults to timestamp)
        
        Returns:
            dict: The axe results object
        """
        # Create the output directory if it doesn't exist
        output_dir = "reports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Initialize axe
        axe = Axe(self.driver)
        
        # Inject axe-core javascript into the page
        axe.inject()
        
        # Run axe analysis
        results = axe.run()
        
        # Save the results
        if name is None:
            name = "accessibility_report"
        
        # Save JSON report
        json_filename = f"{output_dir}/{name}.json"
        with open(json_filename, "w") as f:
            f.write(json.dumps(results, indent=2))
        
        # Save HTML report
        html_filename = f"{output_dir}/{name}.html"
        self._generate_html_report(results, html_filename)
        
        self.results = results
        return results
    
    def _generate_html_report(self, results, filename):
        """Generate an HTML report from the axe results."""
        violations = results.get("violations", [])
        passes = results.get("passes", [])
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Accessibility Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .summary {{ display: flex; margin-bottom: 20px; }}
                .summary-box {{ padding: 15px; margin-right: 15px; border-radius: 5px; color: white; }}
                .violations {{ background-color: #d9534f; }}
                .passes {{ background-color: #5cb85c; }}
                .violation {{ background-color: #f9f9f9; padding: 15px; margin-bottom: 15px; border-left: 5px solid #d9534f; }}
                .critical {{ border-left-color: #d9534f; }}
                .serious {{ border-left-color: #f0ad4e; }}
                .moderate {{ border-left-color: #5bc0de; }}
                .minor {{ border-left-color: #5cb85c; }}
                .affected-elements {{ margin-top: 10px; }}
                .element {{ font-family: monospace; background-color: #eee; padding: 5px; margin-bottom: 5px; }}
                pre {{ background-color: #f5f5f5; padding: 10px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <h1>Accessibility Test Report</h1>
            <p>URL: {self.driver.current_url}</p>
            <p>Date: {results.get("timestamp", "N/A")}</p>
            
            <div class="summary">
                <div class="summary-box violations">
                    <h2>Violations: {len(violations)}</h2>
                </div>
                <div class="summary-box passes">
                    <h2>Passes: {len(passes)}</h2>
                </div>
            </div>
            
            <h2>Violations</h2>
        """
        
        if not violations:
            html += "<p>No accessibility violations found!</p>"
        else:
            for violation in violations:
                impact = violation.get("impact", "unknown")
                html += f"""
                <div class="violation {impact}">
                    <h3>{violation.get("help", "Unknown issue")} ({impact})</h3>
                    <p><strong>Description:</strong> {violation.get("description", "No description")}</p>
                    <p><strong>Help URL:</strong> <a href="{violation.get("helpUrl", "#")}" target="_blank">{violation.get("helpUrl", "#")}</a></p>
                    <p><strong>Tags:</strong> {", ".join(violation.get("tags", []))}</p>
                    <div class="affected-elements">
                        <p><strong>Affected Elements ({len(violation.get("nodes", []))}):</strong></p>
                """
                
                for node in violation.get("nodes", [])[:5]:  # Show first 5 elements
                    html += f"""
                    <div class="element">
                        <p>{node.get("html", "Unknown element")}</p>
                        <p><strong>Failure Summary:</strong> {node.get("failureSummary", "No summary")}</p>
                    </div>
                    """
                
                if len(violation.get("nodes", [])) > 5:
                    html += f"<p>...and {len(violation.get('nodes', [])) - 5} more elements</p>"
                
                html += "</div></div>"
        
        html += """
            <h2>Test Details</h2>
            <pre id="test-details">{}</pre>
            <script>
                document.getElementById("test-details").textContent = JSON.stringify(
                    {
                        "url": window.location.href,
                        "timestamp": new Date().toISOString(),
                        "violations": """ + str(len(violations)) + """,
                        "passes": """ + str(len(passes)) + """
                    }, 
                    null, 2
                );
            </script>
        </body>
        </html>
        """
        
        with open(filename, "w") as f:
            f.write(html)
    
    def check_accessibility_compliance(self, level="aa"):
        """
        Check if the page complies with WCAG at the specified level.
        
        Args:
            level: WCAG compliance level to check ("a", "aa", or "aaa")
        
        Returns:
            bool: True if compliant, False otherwise
        """
        violations = self.results.get("violations", [])
        
        # Filter violations by WCAG level
        if level.lower() == "a":
            relevant_tags = ["wcag2a", "wcag21a", "best-practice"]
        elif level.lower() == "aa":
            relevant_tags = ["wcag2a", "wcag21a", "wcag2aa", "wcag21aa", "best-practice"]
        elif level.lower() == "aaa":
            relevant_tags = ["wcag2a", "wcag21a", "wcag2aa", "wcag21aa", "wcag2aaa", "wcag21aaa", "best-practice"]
        else:
            raise ValueError(f"Invalid WCAG level: {level}. Must be 'a', 'aa', or 'aaa'.")
        
        # Check if any violations match the relevant tags
        for violation in violations:
            tags = violation.get("tags", [])
            for tag in tags:
                if tag in relevant_tags:
                    return False
        
        return True
    
    def print_summary(self):
        """Print a summary of the accessibility test results."""
        violations = self.results.get("violations", [])
        passes = self.results.get("passes", [])
        
        print("\n=== Accessibility Test Summary ===")
        print(f"URL: {self.driver.current_url}")
        print(f"Violations: {len(violations)}")
        print(f"Passes: {len(passes)}")
        
        if not violations:
            print("\nNo accessibility violations found!")
            return
        
        print("\nTop violations:")
        for i, violation in enumerate(violations[:5], 1):
            impact = violation.get("impact", "unknown")
            description = violation.get("description", "No description")
            nodes = violation.get("nodes", [])
            print(f"\n{i}. {description} ({impact})")
            print(f"   Affected elements: {len(nodes)}")
    
    def test_page(self, path="", name=None, level="aa"):
        """
        Test the accessibility of a page.
        
        Args:
            path: Path to the page to test
            name: Name for the report file
            level: WCAG compliance level to check
        
        Returns:
            bool: True if compliant, False otherwise
        """
        try:
            self.setup()
            self.navigate_to(path)
            self.run_axe(name)
            self.print_summary()
            is_compliant = self.check_accessibility_compliance(level)
            
            if is_compliant:
                print(f"\nSUCCESS: Page complies with WCAG {level.upper()} standards")
            else:
                print(f"\nWARNING: Page does not comply with WCAG {level.upper()} standards")
            
            return is_compliant
        finally:
            self.teardown()


def test_homepage():
    """Test the accessibility of the homepage."""
    tester = AccessibilityTest()
    tester.test_page(path="/", name="accessibility_report")


if __name__ == "__main__":
    test_homepage()