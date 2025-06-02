
import requests
import sys
import json
import time
from datetime import datetime

class PromptAchatTester:
    def __init__(self, base_url=None):
        # Try to get the base URL from frontend/.env if not provided
        if base_url is None:
            try:
                with open('/app/frontend/.env', 'r') as f:
                    for line in f:
                        if line.startswith('REACT_APP_BACKEND_URL='):
                            base_url = line.strip().split('=')[1].strip('"\'')
                            break
            except Exception as e:
                print(f"Error reading frontend/.env: {e}")
                base_url = "http://localhost:8001"
        
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.current_user = None
        self.created_prompt_id = None
        self.created_resources = {
            "llm_servers": [],
            "categories": []
        }

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        
        if headers is None:
            headers = {'Content-Type': 'application/json'}
            if self.token:
                headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"Response: {response.text}")
                    return False, response.json()
                except:
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health(self):
        """Test health check endpoint"""
        return self.run_test("Health Check", "GET", "health", 200)

    def test_login(self, username, password):
        """Test login and get token"""
        success, response = self.run_test(
            "Login",
            "POST",
            "auth/login",
            200,
            data={"uid": username, "password": password}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_get_current_user(self):
        """Test getting current user info"""
        success, response = self.run_test("Get Current User", "GET", "auth/me", 200)
        if success:
            self.current_user = response
        return success

    def test_get_prompts(self):
        """Test getting all prompts"""
        return self.run_test("Get All Prompts", "GET", "prompts", 200)

    def test_create_prompt(self, title, content, prompt_type="internal"):
        """Test creating a new prompt"""
        data = {
            "title": title,
            "content": content,
            "variables": ["var1", "var2"],
            "type": prompt_type,
            "category": "Test"
        }
        success, response = self.run_test("Create Prompt", "POST", "prompts", 200, data=data)
        if success and 'id' in response:
            self.created_prompt_id = response['id']
        return success

    def test_get_prompt(self, prompt_id):
        """Test getting a specific prompt"""
        return self.run_test("Get Specific Prompt", "GET", f"prompts/{prompt_id}", 200)

    def test_update_prompt(self, prompt_id, title, content):
        """Test updating a prompt"""
        data = {
            "title": title,
            "content": content
        }
        return self.run_test("Update Prompt", "PUT", f"prompts/{prompt_id}", 200, data=data)

    def test_duplicate_prompt(self, prompt_id):
        """Test duplicating a prompt"""
        return self.run_test(
            "Duplicate Prompt", 
            "POST", 
            f"prompts/{prompt_id}/duplicate", 
            200
        )

    def test_delete_prompt(self, prompt_id):
        """Test deleting a prompt"""
        return self.run_test("Delete Prompt", "DELETE", f"prompts/{prompt_id}", 200)

    def test_get_categories(self):
        """Test getting prompt categories"""
        return self.run_test("Get Categories", "GET", "prompts/categories", 200)

    def test_search_prompts(self, query):
        """Test searching prompts"""
        return self.run_test("Search Prompts", "GET", f"prompts/search?q={query}", 200)

    def test_admin_list_users(self):
        """Test admin listing users"""
        return self.run_test("Admin List Users", "GET", "admin/users", 200)

    def test_admin_create_user(self, uid, email, full_name, role="user"):
        """Test admin creating a user"""
        data = {
            "uid": uid,
            "email": email,
            "full_name": full_name,
            "role": role
        }
        return self.run_test("Admin Create User", "POST", "admin/users", 200, data=data)

    def test_admin_update_user(self, user_uid, email=None, full_name=None, role=None, is_active=None):
        """Test admin updating a user"""
        data = {}
        if email:
            data["email"] = email
        if full_name:
            data["full_name"] = full_name
        if role:
            data["role"] = role
        if is_active is not None:
            data["is_active"] = is_active
            
        return self.run_test("Admin Update User", "PUT", f"admin/users/{user_uid}", 200, data=data)

    def test_admin_delete_user(self, user_uid):
        """Test admin deleting a user"""
        return self.run_test("Admin Delete User", "DELETE", f"admin/users/{user_uid}", 200)

    def test_llm_generate_external(self, prompt_id, context_variables=None):
        """Test generating external prompt"""
        if context_variables is None:
            context_variables = {"var1": "test value 1", "var2": "test value 2"}
            
        data = {
            "prompt_id": prompt_id,
            "user_message": "Test message",
            "context_variables": context_variables
        }
        return self.run_test("Generate External Prompt", "POST", "llm/generate-external", 200, data=data)

    def test_get_llm_models(self):
        """Test getting available LLM models"""
        return self.run_test("Get LLM Models", "GET", "llm/models", 200)
        
    def test_get_llm_servers(self):
        """Test getting all LLM servers"""
        return self.run_test("Get LLM Servers", "GET", "llm/servers", 200)
        
    def test_test_all_llm_servers(self):
        """Test testing all LLM servers"""
        return self.run_test("Test All LLM Servers", "GET", "llm/servers/test-all", 200)
        
    def test_test_llm_server(self, server_name):
        """Test testing a specific LLM server"""
        return self.run_test(f"Test LLM Server {server_name}", "GET", f"llm/servers/{server_name}/test", 200)
        
    def test_get_llm_server_models(self, server_name):
        """Test getting models for a specific LLM server"""
        return self.run_test(f"Get Models for LLM Server {server_name}", "GET", f"llm/servers/{server_name}/models", 200)
        
    def test_get_user_preferences(self):
        """Test getting user preferences"""
        return self.run_test("Get User Preferences", "GET", "user/preferences", 200)
        
    def test_update_user_preferences(self, preferred_server=None, preferred_model=None):
        """Test updating user preferences"""
        data = {}
        if preferred_server is not None:
            data["preferred_llm_server"] = preferred_server
        if preferred_model is not None:
            data["preferred_model"] = preferred_model
            
        return self.run_test("Update User Preferences", "PUT", "user/preferences", 200, data=data)
        
    def test_chat_with_server(self, server_name, model, prompt_text="Bonjour, comment ça va?"):
        """Test chat with a specific server"""
        data = {
            "prompt": prompt_text,
            "stream": False
        }
        endpoint = f"llm/chat/server?server_name={server_name}&model={model}"
        return self.run_test(f"Chat with Server {server_name} using {model}", "POST", endpoint, 200, data=data)
        
    # ===============================
    # Cockpit Variables Tests
    # ===============================
    
    def test_get_cockpit_variables(self):
        """Test GET /api/cockpit/variables."""
        return self.run_test("Get Cockpit Variables", "GET", "cockpit/variables", 200)
    
    def test_get_cockpit_variables_dict(self):
        """Test GET /api/cockpit/variables/dict."""
        return self.run_test("Get Cockpit Variables Dict", "GET", "cockpit/variables/dict", 200)
    
    def test_extract_cockpit_variables(self, content):
        """Test POST /api/cockpit/extract-variables."""
        data = {"content": content}
        return self.run_test("Extract Cockpit Variables", "POST", "cockpit/extract-variables", 200, data=data)
    
    # ===============================
    # User LLM Servers Tests
    # ===============================
    
    def test_get_user_llm_servers(self):
        """Test GET /api/user/llm-servers."""
        return self.run_test("Get User LLM Servers", "GET", "user/llm-servers", 200)
    
    def test_get_all_available_servers(self):
        """Test GET /api/user/llm-servers/all."""
        return self.run_test("Get All Available Servers", "GET", "user/llm-servers/all", 200)
    
    def test_create_user_llm_server(self, name, server_type, url, default_model, api_key=None):
        """Test POST /api/user/llm-servers."""
        data = {
            "name": name,
            "type": server_type,
            "url": url,
            "default_model": default_model
        }
        if api_key:
            data["api_key"] = api_key
            
        success, response = self.run_test("Create User LLM Server", "POST", "user/llm-servers", 200, data=data)
        if success and 'id' in response:
            self.created_resources["llm_servers"].append(response['id'])
        return success, response
    
    def test_get_user_llm_server(self, server_id):
        """Test GET /api/user/llm-servers/{server_id}."""
        return self.run_test(f"Get User LLM Server {server_id}", "GET", f"user/llm-servers/{server_id}", 200)
    
    def test_update_user_llm_server(self, server_id, updates):
        """Test PUT /api/user/llm-servers/{server_id}."""
        return self.run_test(f"Update User LLM Server {server_id}", "PUT", f"user/llm-servers/{server_id}", 200, data=updates)
    
    def test_test_user_llm_server(self, server_id):
        """Test POST /api/user/llm-servers/{server_id}/test."""
        return self.run_test(f"Test User LLM Server {server_id}", "POST", f"user/llm-servers/{server_id}/test", 200)
    
    def test_delete_user_llm_server(self, server_id):
        """Test DELETE /api/user/llm-servers/{server_id}."""
        success, _ = self.run_test(f"Delete User LLM Server {server_id}", "DELETE", f"user/llm-servers/{server_id}", 200)
        if success and server_id in self.created_resources["llm_servers"]:
            self.created_resources["llm_servers"].remove(server_id)
        return success
    
    # ===============================
    # Categories Tests
    # ===============================
    
    def test_get_categories_api(self):
        """Test GET /api/categories."""
        return self.run_test("Get Categories API", "GET", "categories", 200)
    
    def test_get_categories_dict(self):
        """Test GET /api/categories/dict."""
        return self.run_test("Get Categories Dict", "GET", "categories/dict", 200)
    
    def test_create_category(self, name, description=None):
        """Test POST /api/categories."""
        data = {"name": name}
        if description:
            data["description"] = description
            
        success, response = self.run_test("Create Category", "POST", "categories", 200, data=data)
        if success and 'id' in response:
            self.created_resources["categories"].append(response['id'])
        return success, response
    
    def test_update_category(self, category_id, updates):
        """Test PUT /api/categories/{category_id}."""
        return self.run_test(f"Update Category {category_id}", "PUT", f"categories/{category_id}", 200, data=updates)
    
    def test_suggest_category(self, title, content):
        """Test POST /api/categories/suggest."""
        data = {"title": title, "content": content}
        return self.run_test("Suggest Category", "POST", "categories/suggest", 200, data=data)
    
    def test_delete_category(self, category_id):
        """Test DELETE /api/categories/{category_id}."""
        success, _ = self.run_test(f"Delete Category {category_id}", "DELETE", f"categories/{category_id}", 200)
        if success and category_id in self.created_resources["categories"]:
            self.created_resources["categories"].remove(category_id)
        return success

def main():
    # Setup
    tester = PromptAchatTester()
    timestamp = datetime.now().strftime('%H%M%S')
    
    print("=" * 50)
    print("PromptAchat API Test Suite")
    print("=" * 50)
    
    # Test health check
    tester.test_health()
    
    # Test authentication
    if not tester.test_login("admin", "admin"):
        print("❌ Login failed, stopping tests")
        return 1
    
    # Test getting current user
    tester.test_get_current_user()
    
    # ===============================
    # Test Cockpit Variables
    # ===============================
    print("\n" + "=" * 50)
    print("Testing Cockpit Variables")
    print("=" * 50)
    
    # Test getting all cockpit variables
    success, variables = tester.test_get_cockpit_variables()
    if success:
        print(f"✅ Found {len(variables)} cockpit variables")
        if len(variables) < 60:
            print(f"⚠️ Warning: Expected at least 60 variables, got {len(variables)}")
    
    # Test getting cockpit variables as dictionary
    success, variables_dict = tester.test_get_cockpit_variables_dict()
    if success:
        print(f"✅ Found {len(variables_dict)} cockpit variables in dictionary")
    
    # Test extracting cockpit variables from content
    test_content = "Analyse pour {nom_entreprise} dans le {secteur_activite}"
    success, extract_result = tester.test_extract_cockpit_variables(test_content)
    if success:
        uses_cockpit = extract_result.get("uses_cockpit_data", False)
        variables = extract_result.get("cockpit_variables", [])
        print(f"✅ Extracted variables: {variables}")
        print(f"✅ Uses cockpit data: {uses_cockpit}")
        
        if not uses_cockpit:
            print("⚠️ Warning: Expected uses_cockpit_data to be true")
    
    # ===============================
    # Test User LLM Servers
    # ===============================
    print("\n" + "=" * 50)
    print("Testing User LLM Servers")
    print("=" * 50)
    
    # Test getting user LLM servers
    success, user_servers = tester.test_get_user_llm_servers()
    if success:
        print(f"✅ Found {len(user_servers)} user LLM servers")
    
    # Test getting all available servers
    success, all_servers = tester.test_get_all_available_servers()
    if success:
        print(f"✅ Found {len(all_servers)} total available servers (system + user)")
    
    # Test creating a user LLM server
    server_name = f"Test Ollama {timestamp}"
    success, created_server = tester.test_create_user_llm_server(
        name=server_name,
        server_type="ollama",
        url="http://localhost:11434",
        default_model="llama3"
    )
    
    if success and 'id' in created_server:
        server_id = created_server['id']
        print(f"✅ Created user LLM server with ID: {server_id}")
        
        # Test getting the created server
        success, server = tester.test_get_user_llm_server(server_id)
        if success:
            print(f"✅ Retrieved server: {server['name']}")
        
        # Test updating the server
        update_data = {
            "name": f"Updated {server_name}",
            "default_model": "llama3:latest"
        }
        success, updated_server = tester.test_update_user_llm_server(server_id, update_data)
        if success:
            print(f"✅ Updated server name to: {updated_server['name']}")
        
        # Test server connection
        success, test_result = tester.test_test_user_llm_server(server_id)
        print(f"Server connection test result: {test_result.get('status', 'unknown')}")
        
        # Test deleting the server
        if tester.test_delete_user_llm_server(server_id):
            print(f"✅ Deleted server with ID: {server_id}")
    
    # ===============================
    # Test Categories
    # ===============================
    print("\n" + "=" * 50)
    print("Testing Categories")
    print("=" * 50)
    
    # Test getting all categories
    success, categories = tester.test_get_categories_api()
    if success:
        print(f"✅ Found {len(categories)} categories")
        if len(categories) < 10:
            print(f"⚠️ Warning: Expected at least 10 default categories, got {len(categories)}")
        
        # Check for specific categories
        category_names = [cat["name"] for cat in categories]
        expected_categories = [
            "Analyse Contractuelle",
            "Évaluation Fournisseur",
            "Négociation",
            "Veille Marché",
            "RSE et Développement Durable"
        ]
        
        for cat_name in expected_categories:
            if cat_name in category_names:
                print(f"✅ Found expected category: {cat_name}")
            else:
                print(f"⚠️ Missing expected category: {cat_name}")
    
    # Test getting categories as dictionary
    success, categories_dict = tester.test_get_categories_dict()
    if success:
        print(f"✅ Retrieved categories dictionary with {len(categories_dict)} entries")
    
    # Test creating a category
    category_name = f"Test Category {timestamp}"
    success, created_category = tester.test_create_category(
        name=category_name,
        description="Test category description"
    )
    
    if success and 'id' in created_category:
        category_id = created_category['id']
        print(f"✅ Created category with ID: {category_id}")
        
        # Test updating the category
        update_data = {
            "name": f"Updated {category_name}",
            "description": "Updated test category description"
        }
        success, updated_category = tester.test_update_category(category_id, update_data)
        if success:
            print(f"✅ Updated category name to: {updated_category['name']}")
        
        # Test category suggestion
        test_title = "Analyse contrat"
        test_content = "Analyser le contrat fournisseur"
        success, suggestion = tester.test_suggest_category(test_title, test_content)
        if success:
            suggested_name = suggestion.get("suggested_category_name")
            if suggested_name:
                print(f"✅ Suggested category: {suggested_name}")
                if suggested_name == "Analyse Contractuelle":
                    print("✅ Correct category suggested")
                else:
                    print(f"⚠️ Expected 'Analyse Contractuelle', got '{suggested_name}'")
            else:
                print("⚠️ No category was suggested")
        
        # Test deleting the category
        if tester.test_delete_category(category_id):
            print(f"✅ Deleted category with ID: {category_id}")
    
    # ===============================
    # Test Enriched Prompts
    # ===============================
    print("\n" + "=" * 50)
    print("Testing Enriched Prompts")
    print("=" * 50)
    
    # Test getting all prompts
    success, prompts = tester.test_get_prompts()
    if success:
        print(f"✅ Found {len(prompts)} prompts")
        if len(prompts) < 20:
            print(f"⚠️ Warning: Expected at least 20 prompts, got {len(prompts)}")
        
        # Check for prompts in specific categories
        categories_to_check = [
            "Évaluation Fournisseur",
            "Négociation",
            "Analyse Contractuelle",
            "Veille Marché",
            "RSE et Développement Durable"
        ]
        
        category_counts = {}
        for cat in categories_to_check:
            category_counts[cat] = 0
        
        for prompt in prompts:
            if prompt["category"] in categories_to_check:
                category_counts[prompt["category"]] += 1
        
        for cat, count in category_counts.items():
            if count > 0:
                print(f"✅ Found {count} prompts in category: {cat}")
            else:
                print(f"⚠️ No prompts found in category: {cat}")
    
    # ===============================
    # Clean up any remaining resources
    # ===============================
    for server_id in tester.created_resources["llm_servers"]:
        tester.test_delete_user_llm_server(server_id)
    
    for category_id in tester.created_resources["categories"]:
        tester.test_delete_category(category_id)
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print("=" * 50)
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())
