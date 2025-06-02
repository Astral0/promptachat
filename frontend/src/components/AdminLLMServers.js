import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  ServerIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function AdminLLMServers() {
  const [servers, setServers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingServer, setEditingServer] = useState(null);
  const [serverForm, setServerForm] = useState({
    name: '',
    type: 'ollama',
    url: '',
    api_key: '',
    default_model: ''
  });
  const [testResults, setTestResults] = useState({});

  useEffect(() => {
    loadServers();
  }, []);

  const loadServers = async () => {
    try {
      const response = await axios.get(`${API}/admin/llm-servers`);
      setServers(response.data);
    } catch (error) {
      console.error('Error loading servers:', error);
      setMessage({ type: 'error', text: 'Erreur lors du chargement des serveurs' });
    } finally {
      setLoading(false);
    }
  };

  const openModal = (server = null) => {
    if (server) {
      setEditingServer(server);
      setServerForm({
        name: server.name,
        type: server.type,
        url: server.url,
        api_key: server.api_key || '',
        default_model: server.default_model
      });
    } else {
      setEditingServer(null);
      setServerForm({
        name: '',
        type: 'ollama',
        url: '',
        api_key: '',
        default_model: ''
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingServer(null);
    setServerForm({
      name: '',
      type: 'ollama',
      url: '',
      api_key: '',
      default_model: ''
    });
  };

  const saveServer = async () => {
    try {
      if (editingServer) {
        await axios.put(`${API}/admin/llm-servers/${editingServer.id}`, serverForm);
        setMessage({ type: 'success', text: 'Serveur modifié avec succès !' });
      } else {
        await axios.post(`${API}/admin/llm-servers`, serverForm);
        setMessage({ type: 'success', text: 'Serveur créé avec succès !' });
      }
      
      closeModal();
      loadServers();
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error saving server:', error);
      setMessage({ type: 'error', text: 'Erreur lors de la sauvegarde' });
    }
  };

  const deleteServer = async (serverId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce serveur ?')) {
      return;
    }

    try {
      await axios.delete(`${API}/admin/llm-servers/${serverId}`);
      setMessage({ type: 'success', text: 'Serveur supprimé avec succès !' });
      loadServers();
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error deleting server:', error);
      setMessage({ type: 'error', text: 'Erreur lors de la suppression' });
    }
  };

  const testServer = async (serverId) => {
    try {
      setTestResults(prev => ({ ...prev, [serverId]: { status: 'testing' } }));
      const response = await axios.post(`${API}/admin/llm-servers/${serverId}/test`);
      setTestResults(prev => ({ ...prev, [serverId]: response.data }));
    } catch (error) {
      console.error('Error testing server:', error);
      setTestResults(prev => ({ 
        ...prev, 
        [serverId]: { 
          status: 'error', 
          message: 'Erreur lors du test' 
        } 
      }));
    }
  };

  const getStatusIcon = (serverId) => {
    const test = testResults[serverId];
    if (!test) return <ClockIcon className="h-5 w-5 text-gray-400" />;
    
    if (test.status === 'testing') {
      return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>;
    }
    
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

  const getStatusText = (serverId) => {
    const test = testResults[serverId];
    if (!test) return 'Non testé';
    if (test.status === 'testing') return 'Test en cours...';
    
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Serveurs LLM Système</h1>
          <p className="mt-2 text-gray-600">
            Gestion des serveurs LLM disponibles pour tous les utilisateurs
          </p>
        </div>
        <button
          onClick={() => openModal()}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Ajouter un serveur
        </button>
      </div>

      {/* Message */}
      {message && (
        <div className={`rounded-md p-4 ${
          message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          {message.text}
        </div>
      )}

      {/* Servers List */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">
            <ServerIcon className="h-5 w-5 inline mr-2" />
            Serveurs configurés ({servers.length})
          </h3>
        </div>

        {servers.length === 0 ? (
          <div className="text-center py-12">
            <ServerIcon className="h-12 w-12 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun serveur configuré</h3>
            <p className="text-gray-500 mb-4">
              Ajoutez votre premier serveur LLM pour commencer
            </p>
            <button
              onClick={() => openModal()}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
            >
              <PlusIcon className="h-4 w-4 mr-2" />
              Ajouter un serveur
            </button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {servers.map((server) => (
              <div key={server.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    {getStatusIcon(server.id)}
                    <div>
                      <h4 className="text-sm font-medium text-gray-900">
                        {server.name}
                      </h4>
                      <div className="text-sm text-gray-500">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mr-2">
                          {server.type}
                        </span>
                        {server.url} • {server.default_model}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        Status: {getStatusText(server.id)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => testServer(server.id)}
                      className="text-sm text-blue-600 hover:text-blue-500"
                    >
                      Tester
                    </button>
                    <button
                      onClick={() => openModal(server)}
                      className="p-1 text-gray-400 hover:text-blue-600"
                    >
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => deleteServer(server.id)}
                      className="p-1 text-gray-400 hover:text-red-600"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Test Results */}
                {testResults[server.id] && testResults[server.id].available_models && testResults[server.id].available_models.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs font-medium text-gray-700 mb-1">Modèles disponibles:</p>
                    <div className="flex flex-wrap gap-1">
                      {testResults[server.id].available_models.map(model => (
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

      {/* Modal */}
      {showModal && (
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
                    placeholder="Serveur principal"
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
                  onClick={closeModal}
                  className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  onClick={saveServer}
                  disabled={!serverForm.name || !serverForm.url || !serverForm.default_model}
                  className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  {editingServer ? 'Modifier' : 'Créer'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminLLMServers;