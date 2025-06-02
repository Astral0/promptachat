import { useState, useEffect } from 'react';
import axios from 'axios';
import { AuthContext } from '../App';
import {
  UserIcon,
  CogIcon,
  ComputerDesktopIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  ServerIcon
} from '@heroicons/react/24/outline';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function UserSettings() {
  const { user } = AuthContext;
  const [preferences, setPreferences] = useState({
    preferred_llm_server: '',
    preferred_model: ''
  });
  const [servers, setServers] = useState({});
  const [userServers, setUserServers] = useState([]);
  const [allServers, setAllServers] = useState([]);
  const [serverTests, setServerTests] = useState({});
  const [models, setModels] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState(null);
  
  // Modal states for user server management
  const [showServerModal, setShowServerModal] = useState(false);
  const [editingServer, setEditingServer] = useState(null);
  const [serverForm, setServerForm] = useState({
    name: '',
    type: 'ollama',
    url: '',
    api_key: '',
    default_model: '',
    port: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [prefsResponse, serversResponse, modelsResponse, userServersResponse, allServersResponse] = await Promise.all([
        axios.get(`${API}/user/preferences`),
        axios.get(`${API}/llm/servers`),
        axios.get(`${API}/llm/models`),
        axios.get(`${API}/user/llm-servers`),
        axios.get(`${API}/user/llm-servers/all`)
      ]);

      setPreferences(prefsResponse.data);
      setServers(serversResponse.data);
      setModels(modelsResponse.data);
      setUserServers(userServersResponse.data);
      setAllServers(allServersResponse.data);
    } catch (error) {
      console.error('Error loading user settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const testAllServers = async () => {
    setTesting(true);
    try {
      const response = await axios.get(`${API}/llm/servers/test-all`);
      setServerTests(response.data);
    } catch (error) {
      console.error('Error testing servers:', error);
    } finally {
      setTesting(false);
    }
  };

  const testServer = async (serverName) => {
    try {
      const response = await axios.get(`${API}/llm/servers/${serverName}/test`);
      setServerTests(prev => ({
        ...prev,
        [serverName]: response.data
      }));
    } catch (error) {
      console.error(`Error testing server ${serverName}:`, error);
    }
  };

  const testUserServer = async (serverId) => {
    try {
      const response = await axios.post(`${API}/user/llm-servers/${serverId}/test`);
      setServerTests(prev => ({
        ...prev,
        [serverId]: response.data
      }));
    } catch (error) {
      console.error(`Error testing user server ${serverId}:`, error);
    }
  };

  const loadServerModels = async (serverName) => {
    try {
      const response = await axios.get(`${API}/llm/servers/${serverName}/models`);
      setModels(prev => ({
        ...prev,
        [serverName]: response.data.models
      }));
    } catch (error) {
      console.error(`Error loading models for ${serverName}:`, error);
    }
  };

  const savePreferences = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/user/preferences`, preferences);
      setMessage({ type: 'success', text: 'Préférences sauvegardées avec succès !' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error saving preferences:', error);
      setMessage({ type: 'error', text: 'Erreur lors de la sauvegarde' });
      setTimeout(() => setMessage(null), 3000);
    } finally {
      setSaving(false);
    }
  };

  // User Server Management Functions
  const openServerModal = (server = null) => {
    if (server) {
      setEditingServer(server);
      setServerForm({
        name: server.name,
        type: server.type,
        url: server.url,
        api_key: server.api_key || '',
        default_model: server.default_model,
        port: server.port || ''
      });
    } else {
      setEditingServer(null);
      setServerForm({
        name: '',
        type: 'ollama',
        url: '',
        api_key: '',
        default_model: '',
        port: ''
      });
    }
    setShowServerModal(true);
  };

  const closeServerModal = () => {
    setShowServerModal(false);
    setEditingServer(null);
    setServerForm({
      name: '',
      type: 'ollama',
      url: '',
      api_key: '',
      default_model: '',
      port: ''
    });
  };

  const saveUserServer = async () => {
    try {
      const serverData = {
        ...serverForm,
        port: serverForm.port ? parseInt(serverForm.port) : undefined
      };

      if (editingServer) {
        await axios.put(`${API}/user/llm-servers/${editingServer.id}`, serverData);
        setMessage({ type: 'success', text: 'Serveur modifié avec succès !' });
      } else {
        await axios.post(`${API}/user/llm-servers`, serverData);
        setMessage({ type: 'success', text: 'Serveur ajouté avec succès !' });
      }

      closeServerModal();
      loadData(); // Reload data
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error saving server:', error);
      setMessage({ type: 'error', text: 'Erreur lors de la sauvegarde du serveur' });
      setTimeout(() => setMessage(null), 3000);
    }
  };

  const deleteUserServer = async (serverId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce serveur ?')) {
      return;
    }

    try {
      await axios.delete(`${API}/user/llm-servers/${serverId}`);
      setMessage({ type: 'success', text: 'Serveur supprimé avec succès !' });
      loadData(); // Reload data
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error deleting server:', error);
      setMessage({ type: 'error', text: 'Erreur lors de la suppression' });
      setTimeout(() => setMessage(null), 3000);
    }
  };

  const getServerStatusIcon = (serverName) => {
    const test = serverTests[serverName];
    if (!test) return <ClockIcon className="h-5 w-5 text-gray-400" />;
    
    switch (test.status) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'error':
      case 'timeout':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      default:
        return <ClockIcon className="h-5 w-5 text-gray-400" />;
    }
  };

  const getServerStatusText = (serverName) => {
    const test = serverTests[serverName];
    if (!test) return 'Non testé';
    
    switch (test.status) {
      case 'success':
        return `Connecté (${Math.round(test.response_time * 1000)}ms)`;
      case 'error':
        return `Erreur: ${test.message}`;
      case 'timeout':
        return 'Timeout';
      default:
        return 'Non testé';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Paramètres Utilisateur</h1>
        <p className="mt-2 text-gray-600">
          Configurez vos préférences pour les serveurs LLM et modèles
        </p>
      </div>

      {/* Message */}
      {message && (
        <div className={`rounded-md p-4 ${
          message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          {message.text}
        </div>
      )}

      {/* User Info */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center space-x-4">
          <UserIcon className="h-12 w-12 text-gray-400" />
          <div>
            <h3 className="text-lg font-medium text-gray-900">{user?.full_name}</h3>
            <p className="text-sm text-gray-500">{user?.email}</p>
            <div className="flex items-center space-x-2 mt-1">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                user?.role === 'admin' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
              }`}>
                {user?.role}
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {user?.auth_source === 'ldap' ? 'LDAP' : 'Local'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* LLM Preferences */}
      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          <CogIcon className="h-5 w-5 inline mr-2" />
          Préférences LLM
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Preferred Server */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Serveur LLM préféré
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={preferences.preferred_llm_server || ''}
              onChange={(e) => setPreferences(prev => ({
                ...prev,
                preferred_llm_server: e.target.value || null
              }))}
            >
              <option value="">Aucune préférence</option>
              {allServers.map((server) => (
                <option key={server.id} value={server.id}>
                  {server.name} ({server.type}) - {server.default_model}
                  {server.is_system ? ' (Système)' : ' (Personnel)'}
                </option>
              ))}
            </select>
          </div>

          {/* Preferred Model */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Modèle préféré
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              value={preferences.preferred_model || ''}
              onChange={(e) => setPreferences(prev => ({
                ...prev,
                preferred_model: e.target.value || null
              }))}
            >
              <option value="">Aucune préférence</option>
              {preferences.preferred_llm_server && models[preferences.preferred_llm_server] && 
                models[preferences.preferred_llm_server].map(model => (
                  <option key={model} value={model}>{model}</option>
                ))
              }
              {!preferences.preferred_llm_server && Object.entries(models).map(([serverName, serverModels]) => 
                serverModels.map(model => (
                  <option key={`${serverName}_${model}`} value={model}>
                    {model} ({servers[serverName]?.name})
                  </option>
                ))
              )}
            </select>
          </div>
        </div>

        <div className="mt-6">
          <button
            onClick={savePreferences}
            disabled={saving}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {saving ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : (
              <CogIcon className="h-4 w-4 mr-2" />
            )}
            {saving ? 'Sauvegarde...' : 'Sauvegarder les préférences'}
          </button>
        </div>
      </div>

      {/* My LLM Servers */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            <ServerIcon className="h-5 w-5 inline mr-2" />
            Mes Serveurs LLM
          </h3>
          <button
            onClick={() => openServerModal()}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Ajouter un serveur
          </button>
        </div>

        {userServers.length === 0 ? (
          <div className="text-center py-6 text-gray-500">
            <ServerIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
            <p>Aucun serveur personnel configuré</p>
            <p className="text-sm">Ajoutez votre propre serveur LLM pour l'utiliser dans PromptAchat</p>
          </div>
        ) : (
          <div className="space-y-4">
            {userServers.map((server) => (
              <div key={server.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getServerStatusIcon(server.id)}
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">
                        {server.name}
                      </h4>
                      <p className="text-xs text-gray-500">
                        {server.type} • {server.url} • {server.default_model}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500">
                      {getServerStatusText(server.id)}
                    </span>
                    <button
                      onClick={() => testUserServer(server.id)}
                      className="text-xs text-blue-600 hover:text-blue-500"
                    >
                      Tester
                    </button>
                    <button
                      onClick={() => openServerModal(server)}
                      className="p-1 text-gray-400 hover:text-blue-600"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => deleteUserServer(server.id)}
                      className="p-1 text-gray-400 hover:text-red-600"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Test details */}
                {serverTests[server.id] && serverTests[server.id].status === 'error' && (
                  <div className="mt-3">
                    <p className="text-xs text-red-600">
                      <strong>Erreur:</strong> {serverTests[server.id].message}
                    </p>
                  </div>
                )}

                {/* Available models */}
                {serverTests[server.id] && serverTests[server.id].status === 'success' && 
                 serverTests[server.id].available_models && serverTests[server.id].available_models.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs font-medium text-gray-700 mb-1">Modèles disponibles:</p>
                    <div className="flex flex-wrap gap-1">
                      {serverTests[server.id].available_models.map(model => (
                        <span key={model} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">
                          {model}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* System LLM Servers Status */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            <ComputerDesktopIcon className="h-5 w-5 inline mr-2" />
            Serveurs LLM Système
          </h3>
          <button
            onClick={testAllServers}
            disabled={testing}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {testing ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
            ) : (
              <CheckCircleIcon className="h-4 w-4 mr-2" />
            )}
            {testing ? 'Test en cours...' : 'Tester tous'}
          </button>
        </div>

        <div className="space-y-4">
          {Object.entries(servers).map(([name, server]) => (
            <div key={name} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getServerStatusIcon(name)}
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">
                      {server.name}
                    </h4>
                    <p className="text-xs text-gray-500">
                      {server.type} • {server.url} • {server.default_model}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-gray-500">
                    {getServerStatusText(name)}
                  </span>
                  <button
                    onClick={() => testServer(name)}
                    className="text-xs text-blue-600 hover:text-blue-500"
                  >
                    Tester
                  </button>
                  <button
                    onClick={() => loadServerModels(name)}
                    className="text-xs text-green-600 hover:text-green-500"
                  >
                    Charger modèles
                  </button>
                </div>
              </div>

              {/* Models for this server */}
              {models[name] && models[name].length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-medium text-gray-700 mb-1">Modèles disponibles:</p>
                  <div className="flex flex-wrap gap-1">
                    {models[name].map(model => (
                      <span key={model} className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-700">
                        {model}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Test details */}
              {serverTests[name] && serverTests[name].status === 'error' && (
                <div className="mt-3">
                  <p className="text-xs text-red-600">
                    <strong>Erreur:</strong> {serverTests[name].message}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Server Modal */}
      {showServerModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingServer ? 'Modifier le serveur' : 'Ajouter un serveur LLM'}
              </h3>
              
              <div className="space-y-4">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom du serveur *
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={serverForm.name}
                    onChange={(e) => setServerForm(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Mon serveur LLM"
                  />
                </div>

                {/* Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Type *
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={serverForm.type}
                    onChange={(e) => setServerForm(prev => ({ ...prev, type: e.target.value }))}
                  >
                    <option value="ollama">Ollama</option>
                    <option value="openai">OpenAI Compatible</option>
                  </select>
                </div>

                {/* URL */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    URL *
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={serverForm.url}
                    onChange={(e) => setServerForm(prev => ({ ...prev, url: e.target.value }))}
                    placeholder="http://localhost:11434"
                  />
                </div>

                {/* Port */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Port (optionnel)
                  </label>
                  <input
                    type="number"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={serverForm.port}
                    onChange={(e) => setServerForm(prev => ({ ...prev, port: e.target.value }))}
                    placeholder="11434"
                  />
                </div>

                {/* API Key */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Clé API (si nécessaire)
                  </label>
                  <input
                    type="password"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={serverForm.api_key}
                    onChange={(e) => setServerForm(prev => ({ ...prev, api_key: e.target.value }))}
                    placeholder="sk-..."
                  />
                </div>

                {/* Default Model */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Modèle par défaut *
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={serverForm.default_model}
                    onChange={(e) => setServerForm(prev => ({ ...prev, default_model: e.target.value }))}
                    placeholder="llama3, gpt-4, etc."
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={closeServerModal}
                  className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  onClick={saveUserServer}
                  disabled={!serverForm.name || !serverForm.url || !serverForm.default_model}
                  className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  {editingServer ? 'Modifier' : 'Ajouter'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default UserSettings;