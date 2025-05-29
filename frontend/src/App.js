import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import "./App.css";

// Components
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import PromptLibrary from "./components/PromptLibrary";
import PromptEditor from "./components/PromptEditor";
import PromptExecutor from "./components/PromptExecutor";
import AdminPanel from "./components/AdminPanel";
import Layout from "./components/Layout";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Axios interceptor for authentication
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth context
export const AuthContext = {
  user: null,
  setUser: () => {},
  logout: () => {},
  appConfig: {}
};

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [appConfig, setAppConfig] = useState({
    app_name: 'edf',
    app_title: 'PromptAchat',
    logo_url: 'https://upload.wikimedia.org/wikipedia/commons/thumb/1/16/EDF_logo.svg/1200px-EDF_logo.svg.png',
    contact_email: 'contact@edf.fr'
  });

  // Initialize app
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Get app configuration
      const configResponse = await axios.get(`${API}/auth/config`);
      setAppConfig(configResponse.data);

      // Check if user is already authenticated
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const userResponse = await axios.get(`${API}/auth/me`);
          setUser(userResponse.data);
        } catch (error) {
          // Token is invalid, remove it
          localStorage.removeItem('auth_token');
        }
      }
    } catch (error) {
      console.error('Failed to initialize app:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (uid, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { uid, password });
      const { access_token } = response.data;
      
      localStorage.setItem('auth_token', access_token);
      
      // Get user info
      const userResponse = await axios.get(`${API}/auth/me`);
      setUser(userResponse.data);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Erreur de connexion' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
  };

  // Auth context value
  AuthContext.user = user;
  AuthContext.setUser = setUser;
  AuthContext.logout = logout;
  AuthContext.appConfig = appConfig;

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement de {appConfig.app_title}...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          {!user ? (
            // Not authenticated routes
            <Route path="*" element={<Login onLogin={login} appConfig={appConfig} />} />
          ) : (
            // Authenticated routes
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="prompts" element={<PromptLibrary />} />
              <Route path="prompts/new" element={<PromptEditor />} />
              <Route path="prompts/:id/edit" element={<PromptEditor />} />
              <Route path="prompts/:id/execute" element={<PromptExecutor />} />
              {user.role === 'admin' && (
                <Route path="admin" element={<AdminPanel />} />
              )}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          )}
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;