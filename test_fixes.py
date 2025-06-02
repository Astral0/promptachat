#!/usr/bin/env python3
import requests
import json
import time
import sys
from pprint import pprint
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path('/app/frontend/.env'))

# Configuration
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')
BASE_URL = f"{BACKEND_URL}/api"
AUTH_CREDENTIALS = {
    "uid": "admin",
    "password": "admin"
}

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")

def print_subheader(text):
    print(f"\n{Colors.OKBLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}{'-' * 50}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ️ {text}{Colors.ENDC}")

def login():
    """Login and get authentication token."""
    response = requests.post(f"{BASE_URL}/auth/login", json=AUTH_CREDENTIALS)
    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    else:
        print_error(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_admin_llm_servers(token):
    """Test Admin LLM Servers API endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_subheader("Testing Admin LLM Servers API")
    
    # Test GET /api/admin/llm-servers
    print_info("Testing GET /api/admin/llm-servers")
    response = requests.get(f"{BASE_URL}/admin/llm-servers", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        servers = response.json()
        print_success(f"Found {len(servers)} system LLM servers")
        initial_server_count = len(servers)
        if len(servers) > 0:
            print_info("Sample servers:")
            for server in servers[:2]:  # Show first 2 servers
                print(f"  - {server.get('name')} ({server.get('type')}): {server.get('url')}")
    else:
        print_error(f"Error: {response.text}")
        return False
    
    # Create a test server
    print_info("\nCreating a test system LLM server with POST /api/admin/llm-servers")
    test_server_data = {
        "name": "Test Admin Server",
        "type": "ollama",
        "url": "http://localhost:11434",
        "default_model": "llama3"
    }
    
    response = requests.post(f"{BASE_URL}/admin/llm-servers", json=test_server_data, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        server = response.json()
        server_id = server.get("id")
        print_success(f"Created server with ID: {server_id}")
        
        # Test GET for the created server
        print_info(f"\nGetting the server with GET /api/admin/llm-servers/{server_id}")
        response = requests.get(f"{BASE_URL}/admin/llm-servers/{server_id}", headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            retrieved_server = response.json()
            if retrieved_server.get("name") == "Test Admin Server" and retrieved_server.get("type") == "ollama":
                print_success("Server retrieved successfully")
            else:
                print_error("Server data doesn't match what was created")
                return False
        else:
            print_error(f"Error: {response.text}")
            return False
        
        # Clean up - delete the test server
        print_info(f"\nDeleting test server with DELETE /api/admin/llm-servers/{server_id}")
        response = requests.delete(f"{BASE_URL}/admin/llm-servers/{server_id}", headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print_success("Server deleted successfully")
        else:
            print_error(f"Error: {response.text}")
            return False
    else:
        print_error(f"Error creating server: {response.text}")
        return False
    
    return True

def test_prompt_execution(token):
    """Test Prompt Execution API endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_subheader("Testing Prompt Execution")
    
    # First, get a prompt to test with
    print_info("Getting available prompts with GET /api/prompts")
    response = requests.get(f"{BASE_URL}/prompts", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code != 200:
        print_error(f"Error getting prompts: {response.text}")
        return False
    
    prompts_data = response.json()
    
    # Find the first prompt
    prompt_id = None
    prompt_content = None
    
    if "internal" in prompts_data and prompts_data["internal"]:
        prompt_id = prompts_data["internal"][0]["id"]
        prompt_content = prompts_data["internal"][0]["content"]
    elif "external" in prompts_data and prompts_data["external"]:
        prompt_id = prompts_data["external"][0]["id"]
        prompt_content = prompts_data["external"][0]["content"]
    
    if not prompt_id:
        print_error("No prompts found to test with")
        return False
    
    print_success(f"Using prompt ID: {prompt_id} for testing")
    
    # Extract variables from the prompt content
    import re
    variables_in_content = re.findall(r'\{([^}]+)\}', prompt_content)
    
    # Create test variables
    test_variables = []
    for var in variables_in_content:
        test_variables.append({
            "name": var,
            "value": f"Test value for {var}"
        })
    
    if not test_variables:
        # If no variables in the prompt, add a dummy one for testing
        test_variables = [
            {"name": "test_variable", "value": "Test value"}
        ]
        # Modify the content to include our test variable
        modified_content = prompt_content + "\n\nTest variable: {test_variable}"
    else:
        modified_content = None
    
    # Test POST /api/prompts/{prompt_id}/validate
    print_info(f"\nTesting POST /api/prompts/{prompt_id}/validate with simple variables")
    response = requests.post(
        f"{BASE_URL}/prompts/{prompt_id}/validate", 
        json=test_variables,
        headers=headers
    )
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        validation = response.json()
        print_success(f"Validation result: is_valid={validation.get('is_valid')}")
        print_info(f"Required variables: {validation.get('required_variables')}")
        print_info(f"Provided variables: {validation.get('provided_variables')}")
        
        if validation.get('is_valid') == False:
            print_warning(f"Missing variables: {validation.get('missing_variables')}")
            # Add missing variables to our test set
            for var in validation.get('missing_variables', []):
                test_variables.append({
                    "name": var,
                    "value": f"Test value for {var}"
                })
    else:
        print_error(f"Error: {response.text}")
        return False
    
    # Test POST /api/prompts/{prompt_id}/build-final
    print_info(f"\nTesting POST /api/prompts/{prompt_id}/build-final with modified content")
    request_data = {
        "prompt_id": prompt_id,
        "variables": test_variables,
        "files": [],
        "modified_content": modified_content or prompt_content + "\n\nThis is modified content for testing."
    }
    
    response = requests.post(
        f"{BASE_URL}/prompts/{prompt_id}/build-final", 
        json=request_data,
        headers=headers
    )
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print_success("Successfully built final prompt")
        print_info(f"Final prompt length: {len(result.get('final_prompt', ''))}")
        print_info(f"Logs: {len(result.get('logs', []))} entries")
    else:
        print_error(f"Error: {response.text}")
        return False
    
    return True

def test_cockpit_variables(token):
    """Test Cockpit Variables API endpoint."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_subheader("Testing Cockpit Variables API")
    
    # Test GET /api/cockpit/variables
    print_info("Testing GET /api/cockpit/variables")
    response = requests.get(f"{BASE_URL}/cockpit/variables", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        variables = response.json()
        print_success(f"Retrieved {len(variables)} variables")
        if len(variables) > 0:
            print_info("Sample variables:")
            for var in variables[:3]:  # Show first 3 variables
                print(f"  - {var.get('key')}: {var.get('label')}")
    else:
        print_error(f"Error: {response.text}")
        return False
    
    return True

def run_tests():
    """Run the specified backend API tests."""
    print_header("PromptAchat Backend API Tests - Fixes Verification")
    
    # Get authentication token
    token = login()
    if not token:
        print_error("Authentication failed. Cannot proceed with tests.")
        sys.exit(1)
    
    print_success(f"Successfully authenticated with token: {token[:10]}...")
    
    # Run the specified tests
    test_results = {
        "Admin LLM Servers API": test_admin_llm_servers(token),
        "Prompt Execution": test_prompt_execution(token),
        "Cockpit Variables": test_cockpit_variables(token)
    }
    
    # Print summary
    print_header("Test Results Summary")
    
    all_passed = True
    for test_name, result in test_results.items():
        if result:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
            all_passed = False
    
    if all_passed:
        print_header("🎉 All tests passed! The fixes are working correctly.")
    else:
        print_header("❌ Some tests failed. Please check the logs above for details.")

if __name__ == "__main__":
    run_tests()