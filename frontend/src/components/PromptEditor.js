import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import {
  ArrowLeftIcon,
  CheckIcon,
  XMarkIcon,
  EyeIcon,
  PlusIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function PromptEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEdit = Boolean(id);

  const [formData, setFormData] = useState({
    title: '',
    content: '',
    variables: [],
    accepts_files: false,
    needs_cockpit: false,
    category: '',
    welcome_page_html: '',
    type: 'internal',
    is_public: false
  });

  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [newVariable, setNewVariable] = useState('');

  useEffect(() => {
    loadCategories();
    if (isEdit) {
      loadPrompt();
    }
  }, [id]);

  const loadCategories = async () => {
    try {
      const response = await axios.get(`${API}/prompts/categories`);
      setCategories(response.data);
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  };

  const loadPrompt = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/prompts/${id}`);
      const prompt = response.data;
      
      setFormData({
        title: prompt.title || '',
        content: prompt.content || '',
        variables: prompt.variables || [],
        accepts_files: prompt.accepts_files || false,
        needs_cockpit: prompt.needs_cockpit || false,
        category: prompt.category || '',
        welcome_page_html: prompt.welcome_page_html || '',
        type: prompt.type || 'internal',
        is_public: prompt.is_public || false
      });
    } catch (error) {
      console.error('Error loading prompt:', error);
      alert('Erreur lors du chargement du prompt');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!formData.title.trim() || !formData.content.trim()) {
      alert('Le titre et le contenu sont requis');
      return;
    }

    setSaving(true);
    try {
      if (isEdit) {
        await axios.put(`${API}/prompts/${id}`, formData);
      } else {
        await axios.post(`${API}/prompts`, formData);
      }
      
      navigate('/prompts');
    } catch (error) {
      console.error('Error saving prompt:', error);
      alert('Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addVariable = () => {
    if (newVariable.trim() && !formData.variables.includes(newVariable.trim())) {
      setFormData(prev => ({
        ...prev,
        variables: [...prev.variables, newVariable.trim()]
      }));
      setNewVariable('');
    }
  };

  const removeVariable = (variableToRemove) => {
    setFormData(prev => ({
      ...prev,
      variables: prev.variables.filter(v => v !== variableToRemove)
    }));
  };

  const extractVariablesFromContent = () => {
    const matches = formData.content.match(/\{([^}]+)\}/g);
    if (matches) {
      const extractedVars = matches.map(match => match.slice(1, -1));
      const newVars = extractedVars.filter(v => !formData.variables.includes(v));
      
      if (newVars.length > 0) {
        setFormData(prev => ({
          ...prev,
          variables: [...prev.variables, ...newVars]
        }));
      }
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
            <h1 className="text-2xl font-bold text-gray-900">
              {isEdit ? 'Modifier le prompt' : 'Nouveau prompt'}
            </h1>
            <p className="text-gray-600">
              {isEdit ? 'Modifiez votre prompt personnalisé' : 'Créez un nouveau prompt personnalisé'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <EyeIcon className="h-4 w-4 mr-2" />
            {showPreview ? 'Masquer' : 'Aperçu'}
          </button>

          <button
            onClick={handleSave}
            disabled={saving}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {saving ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            ) : (
              <CheckIcon className="h-4 w-4 mr-2" />
            )}
            {saving ? 'Sauvegarde...' : 'Sauvegarder'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form */}
        <div className={`space-y-6 ${showPreview ? 'lg:col-span-2' : 'lg:col-span-3'}`}>
          <div className="bg-white shadow rounded-lg p-6">
            <div className="grid grid-cols-1 gap-6">
              {/* Title */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Titre *
                </label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  value={formData.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  placeholder="Titre du prompt..."
                />
              </div>

              {/* Type and Category */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type *
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={formData.type}
                    onChange={(e) => handleChange('type', e.target.value)}
                  >
                    <option value="internal">Interne</option>
                    <option value="external">Externe</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Catégorie
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={formData.category}
                    onChange={(e) => handleChange('category', e.target.value)}
                    placeholder="Catégorie..."
                    list="categories"
                  />
                  <datalist id="categories">
                    {categories.map(cat => (
                      <option key={cat} value={cat} />
                    ))}
                  </datalist>
                </div>
              </div>

              {/* Content */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Contenu du prompt *
                  </label>
                  <button
                    onClick={extractVariablesFromContent}
                    className="text-xs text-blue-600 hover:text-blue-500"
                  >
                    Extraire les variables {"{variable}"}
                  </button>
                </div>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={12}
                  value={formData.content}
                  onChange={(e) => handleChange('content', e.target.value)}
                  placeholder="Contenu du prompt avec variables {nom_variable}..."
                />
                <p className="mt-1 text-xs text-gray-500">
                  Utilisez {"{nom_variable}"} pour définir des variables dynamiques
                </p>
              </div>

              {/* Variables */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Variables
                </label>
                
                {/* Add variable */}
                <div className="flex space-x-2 mb-3">
                  <input
                    type="text"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={newVariable}
                    onChange={(e) => setNewVariable(e.target.value)}
                    placeholder="Nom de la variable..."
                    onKeyPress={(e) => e.key === 'Enter' && addVariable()}
                  />
                  <button
                    onClick={addVariable}
                    className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <PlusIcon className="h-4 w-4" />
                  </button>
                </div>

                {/* Variables list */}
                {formData.variables.length > 0 && (
                  <div className="space-y-2">
                    {formData.variables.map((variable) => (
                      <div key={variable} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                        <span className="text-sm font-mono">{variable}</span>
                        <button
                          onClick={() => removeVariable(variable)}
                          className="p-1 text-red-600 hover:text-red-500"
                        >
                          <XMarkIcon className="h-4 w-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Options */}
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    checked={formData.accepts_files}
                    onChange={(e) => handleChange('accepts_files', e.target.checked)}
                  />
                  <span className="ml-2 text-sm text-gray-700">Accepte les fichiers PDF</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    checked={formData.needs_cockpit}
                    onChange={(e) => handleChange('needs_cockpit', e.target.checked)}
                  />
                  <span className="ml-2 text-sm text-gray-700">Utilise les données Cockpit</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    checked={formData.is_public}
                    onChange={(e) => handleChange('is_public', e.target.checked)}
                  />
                  <span className="ml-2 text-sm text-gray-700">Rendre public (visible par tous)</span>
                </label>
              </div>

              {/* Welcome Page HTML */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Page d'accueil HTML (optionnel)
                </label>
                <textarea
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={4}
                  value={formData.welcome_page_html}
                  onChange={(e) => handleChange('welcome_page_html', e.target.value)}
                  placeholder="HTML pour la page d'accueil du prompt..."
                />
                <p className="mt-1 text-xs text-gray-500">
                  HTML affiché avant l'utilisation du prompt
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Preview */}
        {showPreview && (
          <div className="lg:col-span-1">
            <div className="bg-white shadow rounded-lg p-6 sticky top-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Aperçu</h3>
              
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900">{formData.title || 'Titre du prompt'}</h4>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      formData.type === 'internal' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                    }`}>
                      {formData.type === 'internal' ? 'Interne' : 'Externe'}
                    </span>
                    {formData.category && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        {formData.category}
                      </span>
                    )}
                  </div>
                </div>

                {formData.welcome_page_html && (
                  <div className="bg-blue-50 border border-blue-200 rounded p-3">
                    <div dangerouslySetInnerHTML={{ __html: formData.welcome_page_html }} />
                  </div>
                )}

                <div>
                  <h5 className="text-sm font-medium text-gray-700 mb-2">Contenu:</h5>
                  <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                    {formData.content || 'Contenu du prompt...'}
                  </div>
                </div>

                {formData.variables.length > 0 && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Variables:</h5>
                    <div className="flex flex-wrap gap-1">
                      {formData.variables.map(variable => (
                        <span key={variable} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                          {variable}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="text-xs text-gray-500 space-y-1">
                  {formData.accepts_files && <div>📎 Accepte les fichiers</div>}
                  {formData.needs_cockpit && <div>🔗 Données Cockpit</div>}
                  {formData.is_public && <div>🌍 Public</div>}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default PromptEditor;