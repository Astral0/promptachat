import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import {
  PlayIcon,
  StopIcon,
  DocumentArrowUpIcon,
  ClipboardDocumentIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowLeftIcon,
  SparklesIcon,
  ComputerDesktopIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/react/24/outline';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function PromptExecutor() {
  const { id } = useParams();
  const [prompt, setPrompt] = useState(null);
  const [variables, setVariables] = useState({});
  const [cockpitId, setCockpitId] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [response, setResponse] = useState('');
  const [externalPrompt, setExternalPrompt] = useState(null);
  const [privacyCheck, setPrivacyCheck] = useState(null);
  const [copied, setCopied] = useState(false);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    loadPrompt();
  }, [id]);

  const loadPrompt = async () => {
    try {
      const response = await axios.get(`${API}/prompts/${id}`);
      setPrompt(response.data);
      
      // Initialize variables
      const initialVariables = {};
      response.data.variables?.forEach(variable => {
        initialVariables[variable] = '';
      });
      setVariables(initialVariables);
    } catch (error) {
      console.error('Error loading prompt:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/files/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadedFiles(prev => [...prev, response.data]);
      
      // Add extracted text to variables if there's a relevant variable
      if (prompt.variables?.includes('contrat_content') || prompt.variables?.includes('document_content')) {
        setVariables(prev => ({
          ...prev,
          contrat_content: prev.contrat_content + '\n\n' + response.data.extracted_text,
          document_content: prev.document_content + '\n\n' + response.data.extracted_text
        }));
      }
    } catch (error) {
      console.error('Error uploading file:', error);
      alert('Erreur lors du téléversement du fichier');
    }
  };

  const executeInternal = async () => {
    setExecuting(true);
    setResponse('');
    
    const requestData = {
      prompt_id: id,
      context_variables: variables,
      cockpit_id: cockpitId || null
    };

    try {
      abortControllerRef.current = new AbortController();
      
      const response = await fetch(`${API}/llm/chat/ollama`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(requestData),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la requête');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              setExecuting(false);
              return;
            }

            try {
              const json = JSON.parse(data);
              if (json.content) {
                setResponse(prev => prev + json.content);
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Error executing prompt:', error);
        alert('Erreur lors de l\'exécution du prompt');
      }
    } finally {
      setExecuting(false);
    }
  };

  const executeExternal = async () => {
    setExecuting(true);
    setExternalPrompt(null);
    setPrivacyCheck(null);

    const requestData = {
      prompt_id: id,
      context_variables: variables,
      cockpit_id: cockpitId || null
    };

    try {
      const response = await axios.post(`${API}/llm/generate-external`, requestData);
      setExternalPrompt(response.data.prompt);
      setPrivacyCheck(response.data.privacy_check);
    } catch (error) {
      console.error('Error generating external prompt:', error);
      alert('Erreur lors de la génération du prompt');
    } finally {
      setExecuting(false);
    }
  };

  const stopExecution = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setExecuting(false);
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(externalPrompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Error copying to clipboard:', error);
    }
  };

  const getPrivacyLevelColor = (level) => {
    switch (level) {
      case 'C0': return 'text-green-600 bg-green-100';
      case 'C1': return 'text-yellow-600 bg-yellow-100';
      case 'C2': return 'text-orange-600 bg-orange-100';
      case 'C3': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
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
      <div className="text-center py-12">
        <h3 className="text-lg font-medium text-gray-900">Prompt non trouvé</h3>
        <Link to="/prompts" className="text-blue-600 hover:text-blue-500">
          Retourner à la bibliothèque
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
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
            <div className="flex items-center space-x-2 mt-1">
              {prompt.type === 'internal' ? (
                <ComputerDesktopIcon className="h-5 w-5 text-green-600" />
              ) : (
                <ExternalLinkIcon className="h-5 w-5 text-blue-600" />
              )}
              <span className="text-sm text-gray-500">
                {prompt.type === 'internal' ? 'Prompt Interne' : 'Prompt Externe'}
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                {prompt.category}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Welcome Page */}
      {prompt.welcome_page_html && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div dangerouslySetInnerHTML={{ __html: prompt.welcome_page_html }} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Section */}
        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Configuration</h3>

            {/* Variables */}
            {prompt.variables && prompt.variables.length > 0 && (
              <div className="space-y-4">
                <h4 className="text-sm font-medium text-gray-700">Variables du prompt</h4>
                {prompt.variables.map((variable) => (
                  <div key={variable}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      {variable}
                    </label>
                    <textarea
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      rows={3}
                      value={variables[variable] || ''}
                      onChange={(e) => setVariables(prev => ({
                        ...prev,
                        [variable]: e.target.value
                      }))}
                      placeholder={`Saisissez ${variable}...`}
                    />
                  </div>
                ))}
              </div>
            )}

            {/* Cockpit ID */}
            {prompt.needs_cockpit && (
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  ID Cockpit (optionnel)
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={cockpitId}
                  onChange={(e) => setCockpitId(e.target.value)}
                  placeholder="Saisissez l'ID Cockpit..."
                />
              </div>
            )}

            {/* File Upload */}
            {prompt.accepts_files && (
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Fichiers PDF
                </label>
                <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                  <div className="space-y-1 text-center">
                    <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <div className="flex text-sm text-gray-600">
                      <label className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                        <span>Téléverser un fichier</span>
                        <input
                          type="file"
                          className="sr-only"
                          accept=".pdf"
                          onChange={handleFileUpload}
                        />
                      </label>
                      <p className="pl-1">ou glisser-déposer</p>
                    </div>
                    <p className="text-xs text-gray-500">PDF seulement</p>
                  </div>
                </div>

                {/* Uploaded Files */}
                {uploadedFiles.length > 0 && (
                  <div className="mt-4 space-y-2">
                    {uploadedFiles.map((file) => (
                      <div key={file.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm text-gray-700">{file.filename}</span>
                        <span className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Execute Button */}
            <div className="mt-6">
              {prompt.type === 'internal' ? (
                <button
                  onClick={executing ? stopExecution : executeInternal}
                  disabled={!prompt.variables?.every(v => variables[v]?.trim()) && prompt.variables?.length > 0}
                  className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {executing ? (
                    <>
                      <StopIcon className="h-4 w-4 mr-2" />
                      Arrêter
                    </>
                  ) : (
                    <>
                      <PlayIcon className="h-4 w-4 mr-2" />
                      Exécuter avec Ollama
                    </>
                  )}
                </button>
              ) : (
                <button
                  onClick={executeExternal}
                  disabled={executing || (!prompt.variables?.every(v => variables[v]?.trim()) && prompt.variables?.length > 0)}
                  className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {executing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Génération...
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="h-4 w-4 mr-2" />
                      Générer le prompt
                    </>
                  )}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Output Section */}
        <div className="space-y-6">
          {/* Internal Response */}
          {prompt.type === 'internal' && (
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Réponse de l'IA</h3>
              {response ? (
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{response}</ReactMarkdown>
                </div>
              ) : (
                <p className="text-gray-500 italic">
                  Cliquez sur "Exécuter" pour obtenir une réponse de l'IA...
                </p>
              )}
            </div>
          )}

          {/* External Prompt */}
          {prompt.type === 'external' && (
            <>
              {/* Privacy Check */}
              {privacyCheck && (
                <div className="bg-white shadow rounded-lg p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Vérification de Confidentialité</h3>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-gray-700">Niveau:</span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPrivacyLevelColor(privacyCheck.confidentiality_level)}`}>
                        {privacyCheck.confidentiality_level}
                      </span>
                    </div>
                    
                    {privacyCheck.concerns && privacyCheck.concerns.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Préoccupations:</h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {privacyCheck.concerns.map((concern, index) => (
                            <li key={index} className="flex items-start">
                              <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500 mr-1 mt-0.5 flex-shrink-0" />
                              {concern}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {privacyCheck.recommendations && privacyCheck.recommendations.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Recommandations:</h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {privacyCheck.recommendations.map((rec, index) => (
                            <li key={index} className="flex items-start">
                              <CheckCircleIcon className="h-4 w-4 text-green-500 mr-1 mt-0.5 flex-shrink-0" />
                              {rec}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Generated Prompt */}
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Prompt Généré</h3>
                  {externalPrompt && (
                    <button
                      onClick={copyToClipboard}
                      className={`inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${copied ? 'bg-green-50 border-green-300 text-green-700' : ''}`}
                    >
                      <ClipboardDocumentIcon className="h-4 w-4 mr-1" />
                      {copied ? 'Copié!' : 'Copier'}
                    </button>
                  )}
                </div>

                {externalPrompt ? (
                  <div className="bg-gray-50 rounded-md p-4">
                    <pre className="whitespace-pre-wrap text-sm text-gray-900 font-mono">
                      {externalPrompt}
                    </pre>
                  </div>
                ) : (
                  <p className="text-gray-500 italic">
                    Cliquez sur "Générer le prompt" pour créer le texte à copier...
                  </p>
                )}

                {/* External Links */}
                {externalPrompt && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Plateformes IA suggérées:</h4>
                    <div className="flex flex-wrap gap-2">
                      <a
                        href="https://chat.openai.com/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                      >
                        ChatGPT
                        <ExternalLinkIcon className="h-3 w-3 ml-1" />
                      </a>
                      <a
                        href="https://claude.ai/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                      >
                        Claude
                        <ExternalLinkIcon className="h-3 w-3 ml-1" />
                      </a>
                      <a
                        href="https://www.perplexity.ai/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                      >
                        Perplexity
                        <ExternalLinkIcon className="h-3 w-3 ml-1" />
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default PromptExecutor;