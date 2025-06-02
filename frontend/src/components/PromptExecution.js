import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import {
  ArrowLeftIcon,
  PlayIcon,
  DocumentDuplicateIcon,
  EyeIcon,
  EyeSlashIcon,
  ExclamationTriangleIcon,
  ClipboardDocumentIcon,
  PaperClipIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function PromptExecution() {
  const { id } = useParams();
  
  const [prompt, setPrompt] = useState(null);
  const [modifiedContent, setModifiedContent] = useState('');
  const [variables, setVariables] = useState([]);
  const [files, setFiles] = useState([]);
  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [availableModels, setAvailableModels] = useState([]);
  
  // Execution states
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [streamingResult, setStreamingResult] = useState('');
  const [finalPrompt, setFinalPrompt] = useState('');
  const [validationErrors, setValidationErrors] = useState([]);
  const [executionLogs, setExecutionLogs] = useState([]);
  
  // UI states
  const [showFinalPrompt, setShowFinalPrompt] = useState(false);
  const [showLogs, setShowLogs] = useState(false);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadData();
  }, [id]);

  useEffect(() => {
    if (modifiedContent || variables.length > 0 || files.length > 0) {
      buildFinalPrompt();
    }
  }, [modifiedContent, variables, files]);

  const loadData = async () => {
    try {
      const [promptResponse, serversResponse] = await Promise.all([
        axios.get(`${API}/prompts/${id}`),
        axios.get(`${API}/user/llm-servers/all`)
      ]);
      
      const promptData = promptResponse.data;
      setPrompt(promptData);
      setModifiedContent(promptData.content);
      
      // Initialize variables
      const promptVars = promptData.variables || [];
      const initialVars = promptVars.map(varName => ({
        name: varName,
        value: '',
        is_cockpit: false
      }));
      setVariables(initialVars);
      
      setServers(serversResponse.data);
      if (serversResponse.data.length > 0) {
        setSelectedServer(serversResponse.data[0].id);
      }
      
    } catch (error) {
      console.error('Error loading prompt:', error);
      setMessage({ type: 'error', text: 'Erreur lors du chargement du prompt' });
    } finally {
      setLoading(false);
    }
  };

  const buildFinalPrompt = async () => {
    try {
      const response = await axios.post(`${API}/prompts/${id}/build-final`, {
        prompt_id: id,
        variables: variables,
        modified_content: modifiedContent,
        files: files,
        server_id: selectedServer,
        model: selectedModel
      });
      
      setFinalPrompt(response.data.final_prompt);
      setExecutionLogs(response.data.logs || []);
    } catch (error) {
      console.error('Error building final prompt:', error);
    }
  };

  const validateExecution = async () => {
    try {
      const response = await axios.post(`${API}/prompts/${id}/validate`, variables);
      
      if (!response.data.is_valid) {
        setValidationErrors(response.data.missing_variables);
        return false;
      }
      
      setValidationErrors([]);
      return true;
    } catch (error) {
      console.error('Error validating execution:', error);
      return false;
    }
  };

  const executePrompt = async () => {
    // Validate first
    const isValid = await validateExecution();
    if (!isValid) {
      setMessage({ 
        type: 'error', 
        text: `Variables manquantes: ${validationErrors.join(', ')}` 
      });
      return;
    }

    setIsExecuting(true);
    setStreamingResult('');
    setExecutionResult(null);
    setMessage(null);

    try {
      // Use streaming for real-time results
      const params = new URLSearchParams({
        variables: JSON.stringify(variables),
        modified_content: modifiedContent,
        files: JSON.stringify(files),
        server_id: selectedServer,
        model: selectedModel
      });

      const response = await fetch(`${API}/prompts/${id}/stream?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.chunk) {
                setStreamingResult(prev => prev + data.chunk);
              }
              if (data.done) {
                // Execution completed
                const finalResult = await axios.post(`${API}/prompts/${id}/execute`, {
                  prompt_id: id,
                  variables: variables,
                  modified_content: modifiedContent,
                  files: files,
                  server_id: selectedServer,
                  model: selectedModel
                });
                setExecutionResult(finalResult.data);
                setExecutionLogs(finalResult.data.logs || []);
              }
            } catch (e) {
              // Ignore JSON parse errors
            }
          }
        }
      }

    } catch (error) {
      console.error('Error executing prompt:', error);
      setMessage({ type: 'error', text: 'Erreur lors de l\'exécution du prompt' });
    } finally {
      setIsExecuting(false);
    }
  };

  const handleVariableChange = (index, field, value) => {
    const newVariables = [...variables];
    newVariables[index][field] = value;
    setVariables(newVariables);
  };

  const addVariable = () => {
    setVariables([...variables, { name: '', value: '', is_cockpit: false }]);
  };

  const removeVariable = (index) => {
    const newVariables = variables.filter((_, i) => i !== index);
    setVariables(newVariables);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target.result.split(',')[1];
        setFiles([...files, { name: file.name, data: base64 }]);
      };
      reader.readAsDataURL(file);
    } else {
      setMessage({ type: 'error', text: 'Seuls les fichiers PDF sont acceptés' });
    }
  };

  const removeFile = (index) => {
    const newFiles = files.filter((_, i) => i !== index);
    setFiles(newFiles);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      setMessage({ type: 'success', text: 'Copié dans le presse-papier !' });
      setTimeout(() => setMessage(null), 2000);
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!prompt) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900">Prompt non trouvé</h1>
          <Link to="/prompts" className="text-blue-600 hover:text-blue-500">
            Retour à la bibliothèque
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to="/prompts"
            className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
          >
            <ArrowLeftIcon className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{prompt.title}</h1>
            <p className="text-gray-600">Exécution du prompt</p>
          </div>
        </div>

        <button
          onClick={executePrompt}
          disabled={isExecuting || validationErrors.length > 0}
          className={`inline-flex items-center px-6 py-3 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
            isExecuting || validationErrors.length > 0
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
          }`}
        >
          {isExecuting ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          ) : (
            <PlayIcon className="h-4 w-4 mr-2" />
          )}
          {isExecuting ? 'Exécution...' : 'Exécuter le prompt'}
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

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Variables manquantes
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <ul className="list-disc pl-5 space-y-1">
                  {validationErrors.map(variable => (
                    <li key={variable}>{variable}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Configuration */}
        <div className="space-y-6">
          {/* Original Prompt */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Prompt Original</h3>
            <div className="bg-gray-50 p-4 rounded-md">
              <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                {prompt.content}
              </pre>
            </div>
            <button
              onClick={() => copyToClipboard(prompt.content)}
              className="mt-2 inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
              Copier
            </button>
          </div>

          {/* Modified Prompt */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              Modifier le Prompt (optionnel)
            </h3>
            <textarea
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              rows={12}
              value={modifiedContent}
              onChange={(e) => setModifiedContent(e.target.value)}
              placeholder="Modifiez le contenu du prompt ici..."
            />
          </div>

          {/* Variables */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Variables</h3>
              <button
                onClick={addVariable}
                className="inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                + Ajouter
              </button>
            </div>
            
            <div className="space-y-3">
              {variables.map((variable, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <input
                    type="text"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Nom de la variable"
                    value={variable.name}
                    onChange={(e) => handleVariableChange(index, 'name', e.target.value)}
                  />
                  <input
                    type="text"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Valeur"
                    value={variable.value}
                    onChange={(e) => handleVariableChange(index, 'value', e.target.value)}
                  />
                  <button
                    onClick={() => removeVariable(index)}
                    className="p-2 text-red-600 hover:text-red-500"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* File Upload */}
          {prompt.accepts_files && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Fichiers PDF</h3>
              
              <div className="mb-4">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              
              {files.length > 0 && (
                <div className="space-y-2">
                  {files.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <div className="flex items-center">
                        <PaperClipIcon className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-700">{file.name}</span>
                      </div>
                      <button
                        onClick={() => removeFile(index)}
                        className="text-red-600 hover:text-red-500"
                      >
                        <XCircleIcon className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Server Selection */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Configuration LLM</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Serveur LLM
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={selectedServer}
                  onChange={(e) => setSelectedServer(e.target.value)}
                >
                  {servers.map(server => (
                    <option key={server.id} value={server.id}>
                      {server.name} ({server.type})
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Modèle
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Modèle (ex: llama3, gpt-4)"
                  value={selectedModel}
                  onChange={(e) => setSelectedModel(e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Results */}
        <div className="space-y-6">
          {/* Final Prompt */}
          <div className="bg-white shadow rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Prompt Final</h3>
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowFinalPrompt(!showFinalPrompt)}
                  className="inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  {showFinalPrompt ? <EyeSlashIcon className="h-4 w-4" /> : <EyeIcon className="h-4 w-4" />}
                </button>
                <button
                  onClick={() => copyToClipboard(finalPrompt)}
                  className="inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  <ClipboardDocumentIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
            
            {showFinalPrompt && (
              <div className="bg-gray-50 p-4 rounded-md max-h-64 overflow-y-auto">
                <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono">
                  {finalPrompt || 'Le prompt final apparaîtra ici après configuration des variables...'}
                </pre>
              </div>
            )}
          </div>

          {/* Execution Result */}
          {(streamingResult || executionResult) && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Résultat</h3>
                <button
                  onClick={() => copyToClipboard(streamingResult || executionResult?.result)}
                  className="inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                  Copier
                </button>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-md max-h-96 overflow-y-auto">
                <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                  {streamingResult || executionResult?.result}
                  {isExecuting && <span className="animate-pulse">▊</span>}
                </pre>
              </div>
            </div>
          )}

          {/* Execution Logs */}
          {executionLogs.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Logs d'Exécution</h3>
                <button
                  onClick={() => setShowLogs(!showLogs)}
                  className="inline-flex items-center px-3 py-1 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  {showLogs ? <EyeSlashIcon className="h-4 w-4" /> : <EyeIcon className="h-4 w-4" />}
                </button>
              </div>
              
              {showLogs && (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {executionLogs.map((log, index) => (
                    <div key={index} className="flex items-start space-x-2 text-sm">
                      <div className="flex-shrink-0 mt-0.5">
                        {log.success ? (
                          <CheckCircleIcon className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircleIcon className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-gray-900">{log.action}</div>
                        <div className="text-gray-600">{log.details}</div>
                        <div className="text-xs text-gray-500">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Execution Stats */}
          {executionResult && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Statistiques</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-600">Temps d'exécution</div>
                  <div className="font-medium">{executionResult.execution_time?.toFixed(2)}s</div>
                </div>
                <div>
                  <div className="text-gray-600">ID d'exécution</div>
                  <div className="font-medium font-mono text-xs">{executionResult.execution_id}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default PromptExecution;