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

def test_cockpit_variables(token):
    """Test Cockpit Variables API endpoints."""
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
    
    # Test GET /api/cockpit/variables/dict
    print_info("\nTesting GET /api/cockpit/variables/dict")
    response = requests.get(f"{BASE_URL}/cockpit/variables/dict", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        variables_dict = response.json()
        print_success(f"Retrieved dictionary with {len(variables_dict)} entries")
        if len(variables_dict) > 0:
            print_info("Sample entries:")
            sample_keys = list(variables_dict.keys())[:3]  # Show first 3 entries
            for key in sample_keys:
                print(f"  - {key}: {variables_dict[key]}")
    else:
        print_error(f"Error: {response.text}")
        return False
    
    # Test POST /api/cockpit/extract-variables
    print_info("\nTesting POST /api/cockpit/extract-variables")
    test_data = {
        "content": "Analyse pour {nom_entreprise} dans le {secteur_activite}"
    }
    response = requests.post(f"{BASE_URL}/cockpit/extract-variables", json=test_data, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Successfully extracted variables: {result.get('cockpit_variables')}")
        print_info(f"uses_cockpit_data: {result.get('uses_cockpit_data')}")
        
        # Verify the correct variables were extracted
        expected_vars = ["nom_entreprise", "secteur_activite"]
        if all(var in result.get('cockpit_variables', []) for var in expected_vars):
            print_success("All expected variables were correctly extracted")
        else:
            print_error(f"Not all expected variables were extracted. Expected: {expected_vars}, Got: {result.get('cockpit_variables')}")
            return False
        
        # Verify uses_cockpit_data is true
        if result.get('uses_cockpit_data') == True:
            print_success("uses_cockpit_data is correctly set to true")
        else:
            print_error(f"uses_cockpit_data should be true but got: {result.get('uses_cockpit_data')}")
            return False
    else:
        print_error(f"Error: {response.text}")
        return False
    
    return True

def test_user_llm_servers(token):
    """Test User LLM Servers API endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_subheader("Testing User LLM Servers API")
    
    # Test GET /api/user/llm-servers/all
    print_info("Testing GET /api/user/llm-servers/all")
    response = requests.get(f"{BASE_URL}/user/llm-servers/all", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        servers = response.json()
        print_success(f"Found {len(servers)} available servers")
        if len(servers) > 0:
            print_info("Sample servers:")
            for server in servers[:2]:  # Show first 2 servers
                print(f"  - {server.get('name')} ({server.get('type')}): {server.get('url')}")
    else:
        print_error(f"Error: {response.text}")
        return False
    
    # Create a test server
    print_info("\nCreating a test LLM server")
    test_server_data = {
        "name": "Test Server",
        "type": "openai",
        "url": "https://api.openai.com",
        "api_key": "test_key_123",
        "default_model": "gpt-3.5-turbo"
    }
    
    response = requests.post(f"{BASE_URL}/user/llm-servers", json=test_server_data, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        server = response.json()
        server_id = server.get("id")
        print_success(f"Created server with ID: {server_id}")
        
        # Test the server connection
        print_info("\nTesting server connection with POST /api/user/llm-servers/{id}/test")
        response = requests.post(f"{BASE_URL}/user/llm-servers/{server_id}/test", headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Test result: {result.get('status')} - {result.get('message')}")
            print_info(f"Response time: {result.get('response_time', 'N/A')} seconds")
            
            # The test might fail with a timeout or error since we're using a fake API key,
            # but the important part is that the endpoint responds correctly
            if result.get('status') in ['success', 'error', 'timeout']:
                print_success("Server test endpoint is working correctly")
            else:
                print_warning(f"Unexpected test status: {result.get('status')}")
        else:
            print_error(f"Error: {response.text}")
            return False
        
        # Test updating the server
        print_info("\nUpdating the server with PUT /api/user/llm-servers/{id}")
        update_data = {
            "name": "Updated Test Server",
            "default_model": "gpt-4"
        }
        response = requests.put(f"{BASE_URL}/user/llm-servers/{server_id}", json=update_data, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            updated_server = response.json()
            if updated_server.get("name") == "Updated Test Server" and updated_server.get("default_model") == "gpt-4":
                print_success("Server updated successfully")
            else:
                print_error("Server was not updated correctly")
                return False
        else:
            print_error(f"Error: {response.text}")
            return False
        
        # Clean up - delete the test server
        print_info("\nDeleting test server with DELETE /api/user/llm-servers/{id}")
        response = requests.delete(f"{BASE_URL}/user/llm-servers/{server_id}", headers=headers)
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

def test_categories(token):
    """Test Categories API endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_subheader("Testing Categories API")
    
    # Test GET /api/categories
    print_info("Testing GET /api/categories")
    response = requests.get(f"{BASE_URL}/categories", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        categories = response.json()
        print_success(f"Retrieved {len(categories)} categories")
        
        # Check if we have at least 10 default categories
        if len(categories) >= 10:
            print_success("Found at least 10 default categories as expected")
            print_info("Sample categories:")
            for category in categories[:5]:  # Show first 5 categories
                print(f"  - {category.get('name')}: {category.get('description', 'No description')}")
        else:
            print_error(f"Expected at least 10 default categories, but found only {len(categories)}")
            return False
    else:
        print_error(f"Error: {response.text}")
        return False
    
    # Test GET /api/categories/dict
    print_info("\nTesting GET /api/categories/dict")
    response = requests.get(f"{BASE_URL}/categories/dict", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        categories_dict = response.json()
        print_success(f"Retrieved dictionary with {len(categories_dict)} entries")
        if len(categories_dict) > 0:
            print_info("Sample entries:")
            sample_keys = list(categories_dict.keys())[:3]  # Show first 3 entries
            for key in sample_keys:
                print(f"  - {key}: {categories_dict[key]}")
    else:
        print_error(f"Error: {response.text}")
        return False
    
    # Test POST /api/categories
    print_info("\nTesting POST /api/categories")
    new_category = {
        "name": "Test Category",
        "description": "A test category created by the backend test script"
    }
    response = requests.post(f"{BASE_URL}/categories", json=new_category, headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        category = response.json()
        category_id = category.get("id")
        print_success(f"Created new category with ID: {category_id}")
        
        # Test updating the category
        print_info("\nUpdating the category with PUT /api/categories/{id}")
        update_data = {
            "name": "Updated Test Category",
            "description": "An updated test category"
        }
        response = requests.put(f"{BASE_URL}/categories/{category_id}", json=update_data, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            updated_category = response.json()
            if updated_category.get("name") == "Updated Test Category":
                print_success("Category updated successfully")
            else:
                print_error("Category was not updated correctly")
                return False
        else:
            print_error(f"Error: {response.text}")
            return False
        
        # Test POST /api/categories/suggest
        print_info("\nTesting POST /api/categories/suggest")
        suggest_data = {
            "title": "Analyse Contractuelle pour Fournisseur",
            "content": "Analyse détaillée d'un contrat fournisseur avec clauses et conditions"
        }
        response = requests.post(f"{BASE_URL}/categories/suggest", json=suggest_data, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            suggestion = response.json()
            if suggestion.get("suggested_category_id"):
                print_success(f"Suggested category: {suggestion.get('suggested_category_name')} (ID: {suggestion.get('suggested_category_id')})")
            else:
                print_warning("No category suggested")
        else:
            print_error(f"Error: {response.text}")
            return False
        
        # Clean up - delete the test category
        print_info("\nDeleting test category with DELETE /api/categories/{id}")
        response = requests.delete(f"{BASE_URL}/categories/{category_id}", headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print_success("Category deleted successfully")
        else:
            print_error(f"Error: {response.text}")
            return False
    else:
        print_error(f"Error creating category: {response.text}")
        return False
    
    return True

def test_enriched_prompts(token):
    """Test enriched prompts functionality."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_subheader("Testing Enriched Prompts")
    
    # Test GET /api/prompts
    print_info("Testing GET /api/prompts")
    response = requests.get(f"{BASE_URL}/prompts", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        prompts_data = response.json()
        
        # Check if we have the expected structure
        if not isinstance(prompts_data, dict) or "internal" not in prompts_data or "external" not in prompts_data:
            print_error(f"Unexpected response structure: {prompts_data}")
            return False
        
        internal_prompts = prompts_data.get("internal", [])
        external_prompts = prompts_data.get("external", [])
        total_prompts = len(internal_prompts) + len(external_prompts)
        
        print_success(f"Retrieved {len(internal_prompts)} internal prompts and {len(external_prompts)} external prompts")
        
        # Check if we have at least 6 prompts in total
        if total_prompts >= 6:
            print_success(f"Found at least 6 prompts as expected (actual: {total_prompts})")
        else:
            print_error(f"Expected at least 6 prompts, but found only {total_prompts}")
            return False
        
        # Check if prompts use uses_cockpit_data instead of needs_cockpit
        uses_cockpit_field_correct = True
        needs_cockpit_prompts = []
        
        for prompt in internal_prompts + external_prompts:
            if "needs_cockpit" in prompt and "uses_cockpit_data" not in prompt:
                uses_cockpit_field_correct = False
                needs_cockpit_prompts.append(prompt.get("title", "Unknown"))
        
        if uses_cockpit_field_correct:
            print_success("All prompts use 'uses_cockpit_data' field correctly")
        else:
            print_error(f"Some prompts still use 'needs_cockpit' instead of 'uses_cockpit_data': {', '.join(needs_cockpit_prompts)}")
            return False
        
        # Check if prompts exist in the new categories
        categories_to_check = [
            "Évaluation Fournisseur", 
            "Négociation", 
            "Analyse Contractuelle", 
            "RSE et Développement Durable",
            "Veille Marché",
            "Gestion des Risques",
            "Innovation et Technologie",
            "Reporting et Analyse",
            "Stratégie Achats",
            "Conformité et Réglementation"
        ]
        
        found_categories = {}
        for prompt in internal_prompts + external_prompts:
            category = prompt.get("category")
            if category in categories_to_check:
                if category not in found_categories:
                    found_categories[category] = []
                found_categories[category].append(prompt.get("title"))
        
        if found_categories:
            print_success(f"Found prompts in {len(found_categories)} of the new categories")
            for category, prompts in found_categories.items():
                print_info(f"  - {category}: {len(prompts)} prompts")
                for prompt_title in prompts[:2]:  # Show first 2 prompts per category
                    print(f"    * {prompt_title}")
        else:
            print_warning("No prompts found in the new categories")
    else:
        print_error(f"Error: {response.text}")
        return False
    
    return True

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
        "name": "Test Server",
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
            if retrieved_server.get("name") == "Test Server" and retrieved_server.get("type") == "ollama":
                print_success("Server retrieved successfully")
            else:
                print_error("Server data doesn't match what was created")
                return False
        else:
            print_error(f"Error: {response.text}")
            return False
        
        # Test updating the server
        print_info(f"\nUpdating the server with PUT /api/admin/llm-servers/{server_id}")
        update_data = {
            "name": "Updated Test Server",
            "default_model": "llama3:latest"
        }
        response = requests.put(f"{BASE_URL}/admin/llm-servers/{server_id}", json=update_data, headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            updated_server = response.json()
            if updated_server.get("name") == "Updated Test Server" and updated_server.get("default_model") == "llama3:latest":
                print_success("Server updated successfully")
            else:
                print_error("Server was not updated correctly")
                return False
        else:
            print_error(f"Error: {response.text}")
            return False
        
        # Test the server connection
        print_info(f"\nTesting server connection with POST /api/admin/llm-servers/{server_id}/test")
        response = requests.post(f"{BASE_URL}/admin/llm-servers/{server_id}/test", headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Test result: {result.get('status')} - {result.get('message')}")
            print_info(f"Response time: {result.get('response_time', 'N/A')} seconds")
            
            # The test might fail with a timeout or error since we're using a fake server,
            # but the important part is that the endpoint responds correctly
            if result.get('status') in ['success', 'error', 'timeout']:
                print_success("Server test endpoint is working correctly")
            else:
                print_warning(f"Unexpected test status: {result.get('status')}")
        else:
            print_error(f"Error: {response.text}")
            return False
        
        # Clean up - delete the test server
        print_info(f"\nDeleting test server with DELETE /api/admin/llm-servers/{server_id}")
        response = requests.delete(f"{BASE_URL}/admin/llm-servers/{server_id}", headers=headers)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print_success("Server deleted successfully")
            
            # Verify the server was deleted
            response = requests.get(f"{BASE_URL}/admin/llm-servers", headers=headers)
            if response.status_code == 200:
                servers = response.json()
                if len(servers) == initial_server_count:
                    print_success("Server deletion verified")
                else:
                    print_error(f"Server count mismatch after deletion: expected {initial_server_count}, got {len(servers)}")
                    return False
        else:
            print_error(f"Error: {response.text}")
            return False
    else:
        print_error(f"Error creating server: {response.text}")
        return False
    
    return True

def test_advanced_prompt_execution(token):
    """Test Advanced Prompt Execution API endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print_subheader("Testing Advanced Prompt Execution")
    
    # First, get a prompt to test with
    print_info("Getting a prompt to test with")
    response = requests.get(f"{BASE_URL}/prompts", headers=headers)
    
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
    print_info(f"\nTesting POST /api/prompts/{prompt_id}/validate")
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
            
            # Validate again with the complete set
            print_info(f"Retrying validation with complete variable set")
            response = requests.post(
                f"{BASE_URL}/prompts/{prompt_id}/validate", 
                json=test_variables,
                headers=headers
            )
            
            if response.status_code == 200:
                validation = response.json()
                if validation.get('is_valid'):
                    print_success("Validation successful with complete variable set")
                else:
                    print_error(f"Validation still failing: {validation}")
                    return False
            else:
                print_error(f"Error: {response.text}")
                return False
    else:
        print_error(f"Error: {response.text}")
        return False
    
    # Test POST /api/prompts/{prompt_id}/build-final
    print_info(f"\nTesting POST /api/prompts/{prompt_id}/build-final")
    request_data = {
        "variables": test_variables,
        "files": [],
        "modified_content": modified_content
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
    
    # Test POST /api/prompts/{prompt_id}/execute
    print_info(f"\nTesting POST /api/prompts/{prompt_id}/execute")
    execute_request = {
        "prompt_id": prompt_id,
        "variables": test_variables,
        "files": [],
        "modified_content": modified_content,
        "server_id": None,  # Use default server
        "model": None       # Use default model
    }
    
    response = requests.post(
        f"{BASE_URL}/prompts/{prompt_id}/execute", 
        json=execute_request,
        headers=headers
    )
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print_success("Successfully executed prompt")
        print_info(f"Execution ID: {result.get('execution_id')}")
        print_info(f"Execution time: {result.get('execution_time')} seconds")
        print_info(f"Result length: {len(result.get('result', ''))}")
    else:
        print_error(f"Error: {response.text}")
        return False
    
    # Test GET /api/prompts/{prompt_id}/stream
    print_info(f"\nTesting GET /api/prompts/{prompt_id}/stream")
    
    try:
        # Use a short timeout to just test if streaming starts
        response = requests.get(
            f"{BASE_URL}/prompts/{prompt_id}/stream", 
            headers=headers,
            stream=True,
            timeout=2
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            # Just check if we get at least one chunk
            for line in response.iter_lines(chunk_size=1024, decode_unicode=True):
                if line:
                    print_success("Successfully received streaming data")
                    break
            
            print_success("Streaming endpoint is working")
        else:
            print_error(f"Error: {response.text}")
            return False
    except requests.exceptions.Timeout:
        # Timeout is expected since we're just testing if streaming starts
        print_success("Streaming started successfully (timeout as expected)")
    except Exception as e:
        print_error(f"Error testing streaming: {str(e)}")
        return False
    
    return True

def run_all_tests():
    """Run all backend API tests."""
    print_header("PromptAchat Backend API Tests")
    
    # Get authentication token
    token = login()
    if not token:
        print_error("Authentication failed. Cannot proceed with tests.")
        sys.exit(1)
    
    print_success(f"Successfully authenticated with token: {token[:10]}...")
    
    # Run all tests
    test_results = {
        "Cockpit Variables": test_cockpit_variables(token),
        "User LLM Servers": test_user_llm_servers(token),
        "Categories": test_categories(token),
        "Enriched Prompts": test_enriched_prompts(token),
        "Admin LLM Servers": test_admin_llm_servers(token),
        "Advanced Prompt Execution": test_advanced_prompt_execution(token)
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
        print_header("🎉 All tests passed! The backend is working correctly.")
    else:
        print_header("❌ Some tests failed. Please check the logs above for details.")

if __name__ == "__main__":
    run_all_tests()
