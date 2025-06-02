
import requests
import json
import time
import sys
from pprint import pprint

# Base URL for API
BASE_URL = "http://localhost:8001/api"

# Authentication credentials
AUTH_CREDENTIALS = {
    "uid": "admin",
    "password": "admin"
}

def login():
    """Login and get authentication token."""
    response = requests.post(f"{BASE_URL}/auth/login", json=AUTH_CREDENTIALS)
    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_user_llm_servers_api(token):
    """Test User LLM Servers API endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing User LLM Servers API ===")
    
    # Test GET /api/user/llm-servers/all
    print("\nTesting GET /api/user/llm-servers/all")
    response = requests.get(f"{BASE_URL}/user/llm-servers/all", headers=headers)
    print(f"Status code: {response.status_code}")
    if response.status_code == 200:
        servers = response.json()
        print(f"Found {len(servers)} available servers")
        pprint(servers[:2] if len(servers) > 2 else servers)  # Show first 2 servers or all if less
    else:
        print(f"Error: {response.text}")
    
    # Create a test server
    print("\nCreating a test LLM server")
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
        print(f"Created server with ID: {server_id}")
        
        # Test the server connection
        print("\nTesting server connection")
        response = requests.post(f"{BASE_URL}/user/llm-servers/{server_id}/test", headers=headers)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Test result: {result.get('status')} - {result.get('message')}")
        else:
            print(f"Error: {response.text}")
        
        # Clean up - delete the test server
        print("\nDeleting test server")
        response = requests.delete(f"{BASE_URL}/user/llm-servers/{server_id}", headers=headers)
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Server deleted successfully")
        else:
            print(f"Error: {response.text}")
    else:
        print(f"Error creating server: {response.text}")

def test_enriched_prompts(token):
    """Test enriched prompts functionality."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Testing Enriched Prompts ===")
    
    # Test GET /api/prompts
    print("\nTesting GET /api/prompts")
    response = requests.get(f"{BASE_URL}/prompts", headers=headers)
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        prompts = response.json()
        print(f"Found {len(prompts)} prompts")
        
        # Check for specific categories
        categories = set()
        for prompt in prompts:
            if isinstance(prompt, dict) and "category" in prompt:
                categories.add(prompt["category"])
        
        print(f"\nFound {len(categories)} categories:")
        for category in categories:
            print(f"- {category}")
        
        # Check for specific prompts in the required categories
        required_categories = [
            "Évaluation Fournisseur", 
            "Négociation", 
            "RSE et Développement Durable",
            "Analyse Contractuelle"
        ]
        
        print("\nChecking for prompts in required categories:")
        for category in required_categories:
            category_prompts = [p for p in prompts if isinstance(p, dict) and p.get("category") == category]
            if category_prompts:
                print(f"✅ Found {len(category_prompts)} prompts in category '{category}'")
                # Print first prompt title in this category
                if category_prompts:
                    print(f"   Example: '{category_prompts[0].get('title')}'")
            else:
                print(f"❌ No prompts found in category '{category}'")
    else:
        print(f"Error: {response.text}")

def main():
    """Main test function."""
    token = login()
    if not token:
        print("Authentication failed. Cannot proceed with tests.")
        sys.exit(1)
    
    print(f"Successfully authenticated with token: {token[:10]}...")
    
    # Test User LLM Servers API
    test_user_llm_servers_api(token)
    
    # Test Enriched Prompts
    test_enriched_prompts(token)

if __name__ == "__main__":
    main()
