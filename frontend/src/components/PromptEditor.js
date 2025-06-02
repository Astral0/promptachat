import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axios from 'axios';
import {
  ArrowLeftIcon,
  CheckIcon,
  XMarkIcon,
  EyeIcon,
  PlusIcon,
  TrashIcon,
  ChevronDownIcon,
  MagnifyingGlassIcon
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
    uses_cockpit_data: false,
    category: '',
    welcome_page_html: '',
    type: 'internal',
    is_public: false
  });

  const [categories, setCategories] = useState([]);
  const [cockpitVariables, setCockpitVariables] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [newVariable, setNewVariable] = useState('');
  const [message, setMessage] = useState(null);

  // Category management
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [newCategory, setNewCategory] = useState({ name: '', description: '' });
  const [categorySearch, setCategorySearch] = useState('');

  // Variable management
  const [showVariableDropdown, setShowVariableDropdown] = useState(false);
  const [variableSearch, setVariableSearch] = useState('');
  const [cockpitVariablesInContent, setCockpitVariablesInContent] = useState([]);

  useEffect(() => {
    loadInitialData();
    if (isEdit) {
      loadPrompt();
    }
  }, [id]);

  useEffect(() => {
    // Auto-detect Cockpit variables when content changes
    if (formData.content) {
      detectCockpitVariables(formData.content);
    }
  }, [formData.content, cockpitVariables]);

  const loadInitialData = async () => {
    try {
      const [categoriesResponse, cockpitResponse] = await Promise.all([
        axios.get(`${API}/categories`),
        axios.get(`${API}/cockpit/variables`)
      ]);
      
      setCategories(categoriesResponse.data);
      setCockpitVariables(cockpitResponse.data);
    } catch (error) {
      console.error('Error loading initial data:', error);
    }
  };

  const detectCockpitVariables = async (content) => {
    try {
      const response = await axios.post(`${API}/cockpit/extract-variables`, { content });
      const { cockpit_variables, uses_cockpit_data } = response.data;
      
      setCockpitVariablesInContent(cockpit_variables);
      
      // Auto-update the checkbox
      setFormData(prev => ({
        ...prev,
        uses_cockpit_data: uses_cockpit_data
      }));
    } catch (error) {
      console.error('Error detecting cockpit variables:', error);
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
        uses_cockpit_data: prompt.uses_cockpit_data || false,
        category: prompt.category || '',
        welcome_page_html: prompt.welcome_page_html || '',
        type: prompt.type || 'internal',
        is_public: prompt.is_public || false
      });
    } catch (error) {
      console.error('Error loading prompt:', error);
      setMessage({ type: 'error', text: 'Erreur lors du chargement du prompt' });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!formData.title.trim() || !formData.content.trim()) {
      setMessage({ type: 'error', text: 'Le titre et le contenu sont requis' });
      return;
    }

    setSaving(true);
    try {
      if (isEdit) {
        await axios.put(`${API}/prompts/${id}`, formData);
        setMessage({ type: 'success', text: 'Prompt modifié avec succès !' });
      } else {
        await axios.post(`${API}/prompts`, formData);
        setMessage({ type: 'success', text: 'Prompt créé avec succès !' });
      }
      
      setTimeout(() => {
        navigate('/prompts');
      }, 1500);
    } catch (error) {
      console.error('Error saving prompt:', error);
      setMessage({ type: 'error', text: 'Erreur lors de la sauvegarde' });
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

  const addVariable = (variableName = null) => {
    const varToAdd = variableName || newVariable.trim();
    if (varToAdd && !formData.variables.includes(varToAdd)) {
      setFormData(prev => ({
        ...prev,
        variables: [...prev.variables, varToAdd]
      }));
      setNewVariable('');
      setShowVariableDropdown(false);
    }
  };

  const addCockpitVariable = (cockpitVar) => {
    // Add the variable to the content at cursor position
    const textarea = document.getElementById('content-textarea');
    const cursorPos = textarea.selectionStart;
    const textBefore = formData.content.substring(0, cursorPos);
    const textAfter = formData.content.substring(cursorPos);
    const newContent = textBefore + `{${cockpitVar.key}}` + textAfter;
    
    handleChange('content', newContent);
    setShowVariableDropdown(false);
    
    // Focus back to textarea
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(cursorPos + cockpitVar.key.length + 2, cursorPos + cockpitVar.key.length + 2);
    }, 100);
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

  const suggestCategory = async () => {
    if (!formData.title && !formData.content) return;
    
    try {
      const response = await axios.post(`${API}/categories/suggest`, {
        title: formData.title,
        content: formData.content
      });
      
      if (response.data.suggested_category_id) {
        const category = categories.find(c => c.id === response.data.suggested_category_id);
        if (category) {
          handleChange('category', category.name);
          setMessage({ type: 'success', text: `Catégorie suggérée: ${category.name}` });
          setTimeout(() => setMessage(null), 3000);
        }
      }
    } catch (error) {
      console.error('Error suggesting category:', error);
    }
  };

  const createCategory = async () => {
    if (!newCategory.name.trim()) {
      setMessage({ type: 'error', text: 'Le nom de la catégorie est requis' });
      return;
    }

    try {
      const response = await axios.post(`${API}/categories`, newCategory);
      setCategories(prev => [...prev, response.data]);
      handleChange('category', response.data.name);
      setNewCategory({ name: '', description: '' });
      setShowCategoryModal(false);
      setMessage({ type: 'success', text: 'Catégorie créée avec succès !' });
      setTimeout(() => setMessage(null), 3000);
    } catch (error) {
      console.error('Error creating category:', error);
      setMessage({ type: 'error', text: 'Erreur lors de la création de la catégorie' });
    }
  };

  const filteredCategories = categories.filter(cat =>
    cat.name.toLowerCase().includes(categorySearch.toLowerCase())
  );

  const filteredCockpitVariables = cockpitVariables.filter(variable =>
    variable.key.toLowerCase().includes(variableSearch.toLowerCase()) ||
    variable.label.toLowerCase().includes(variableSearch.toLowerCase())
  );

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

      {/* Message */}
      {message && (
        <div className={`rounded-md p-4 ${
          message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          {message.text}
        </div>
      )}

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
                    <option value="internal">Interne (LLM Local)</option>
                    <option value="external">Externe (Copier/Coller)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Catégorie
                  </label>
                  <div className="flex space-x-2">
                    <div className="flex-1 relative">
                      <input
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        value={formData.category}
                        onChange={(e) => {
                          handleChange('category', e.target.value);
                          setCategorySearch(e.target.value);
                        }}
                        placeholder="Sélectionner ou créer..."
                        list="categories"
                      />
                      <datalist id="categories">
                        {filteredCategories.map(cat => (
                          <option key={cat.id} value={cat.name} />
                        ))}
                      </datalist>
                    </div>
                    <button
                      onClick={() => setShowCategoryModal(true)}
                      className="px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                    >
                      <PlusIcon className="h-4 w-4" />
                    </button>
                    <button
                      onClick={suggestCategory}
                      className="px-3 py-2 border border-green-300 text-sm font-medium rounded-md text-green-700 bg-green-50 hover:bg-green-100"
                    >
                      <MagnifyingGlassIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Contenu du prompt *
                  </label>
                  <div className="flex space-x-2">
                    <div className="relative">
                      <button
                        onClick={() => setShowVariableDropdown(!showVariableDropdown)}
                        className="inline-flex items-center px-3 py-1 border border-blue-300 text-xs font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100"
                      >
                        <PlusIcon className="h-3 w-3 mr-1" />
                        Variables Cockpit
                        <ChevronDownIcon className="h-3 w-3 ml-1" />
                      </button>
                      
                      {showVariableDropdown && (
                        <div className="absolute right-0 mt-1 w-80 bg-white border border-gray-200 rounded-md shadow-lg z-10">
                          <div className="p-3">
                            <input
                              type="text"
                              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                              placeholder="Rechercher une variable..."
                              value={variableSearch}
                              onChange={(e) => setVariableSearch(e.target.value)}
                            />
                          </div>
                          <div className="max-h-48 overflow-y-auto border-t border-gray-200">
                            {filteredCockpitVariables.map((variable) => (
                              <button
                                key={variable.key}
                                onClick={() => addCockpitVariable(variable)}
                                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-50 border-b border-gray-100"
                              >
                                <div className="font-medium text-gray-900">{variable.label}</div>
                                <div className="text-xs text-gray-500 font-mono">{`{${variable.key}}`}</div>
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                    <button
                      onClick={extractVariablesFromContent}
                      className="text-xs text-blue-600 hover:text-blue-500"
                    >
                      Extraire les variables {"{variable}"}
                    </button>
                  </div>
                </div>
                <textarea
                  id="content-textarea"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  rows={16}
                  value={formData.content}
                  onChange={(e) => handleChange('content', e.target.value)}
                  placeholder="Contenu du prompt avec variables {nom_variable}..."
                />
                <div className="flex items-center justify-between mt-1">
                  <p className="text-xs text-gray-500">
                    Utilisez {"{nom_variable}"} pour définir des variables dynamiques
                  </p>
                  {cockpitVariablesInContent.length > 0 && (
                    <div className="flex items-center space-x-1">
                      <span className="text-xs text-green-600">Variables Cockpit détectées:</span>
                      {cockpitVariablesInContent.map(variable => (
                        <span key={variable} className="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-green-100 text-green-800">
                          {variable}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Variables */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Variables personnalisées
                </label>
                
                {/* Add variable */}
                <div className="flex space-x-2 mb-3">
                  <input
                    type="text"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    value={newVariable}
                    onChange={(e) => setNewVariable(e.target.value)}
                    placeholder="Nom de la variable personnalisée..."
                    onKeyPress={(e) => e.key === 'Enter' && addVariable()}
                  />
                  <button
                    onClick={() => addVariable()}
                    className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                  >
                    <PlusIcon className="h-4 w-4" />
                  </button>
                </div>

                {/* Variables list */}
                {formData.variables.length > 0 && (
                  <div className="space-y-2">
                    {formData.variables.map((variable) => {
                      const isCockpitVar = cockpitVariables.some(cv => cv.key === variable);
                      return (
                        <div key={variable} className={`flex items-center justify-between p-2 rounded ${
                          isCockpitVar ? 'bg-green-50 border border-green-200' : 'bg-gray-50'
                        }`}>
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-mono">{variable}</span>
                            {isCockpitVar && (
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-xs bg-green-100 text-green-800">
                                Cockpit
                              </span>
                            )}
                          </div>
                          <button
                            onClick={() => removeVariable(variable)}
                            className="p-1 text-red-600 hover:text-red-500"
                          >
                            <XMarkIcon className="h-4 w-4" />
                          </button>
                        </div>
                      );
                    })}
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
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
                    checked={formData.uses_cockpit_data}
                    disabled={true}
                    title="Cette option est automatiquement gérée selon les variables Cockpit détectées"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    Utilise les données Cockpit 
                    <span className="text-xs text-gray-500 ml-1">(automatique)</span>
                  </span>
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
                    {formData.uses_cockpit_data && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        Cockpit
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
                  <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded max-h-48 overflow-y-auto">
                    {formData.content || 'Contenu du prompt...'}
                  </div>
                </div>

                {(formData.variables.length > 0 || cockpitVariablesInContent.length > 0) && (
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Variables:</h5>
                    <div className="flex flex-wrap gap-1">
                      {/* Cockpit variables */}
                      {cockpitVariablesInContent.map(variable => (
                        <span key={variable} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                          {variable} (Cockpit)
                        </span>
                      ))}
                      {/* Custom variables */}
                      {formData.variables.filter(v => !cockpitVariablesInContent.includes(v)).map(variable => (
                        <span key={variable} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                          {variable}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="text-xs text-gray-500 space-y-1">
                  {formData.accepts_files && <div>📎 Accepte les fichiers</div>}
                  {formData.uses_cockpit_data && <div>🔗 Données Cockpit</div>}
                  {formData.is_public && <div>🌍 Public</div>}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Category Modal */}
      {showCategoryModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Créer une nouvelle catégorie
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Nom de la catégorie *
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={newCategory.name}
                    onChange={(e) => setNewCategory(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Ex: Analyse Contractuelle"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description (optionnel)
                  </label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    value={newCategory.description}
                    onChange={(e) => setNewCategory(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Description de la catégorie..."
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button
                  onClick={() => {
                    setShowCategoryModal(false);
                    setNewCategory({ name: '', description: '' });
                  }}
                  className="px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Annuler
                </button>
                <button
                  onClick={createCategory}
                  disabled={!newCategory.name.trim()}
                  className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  Créer
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PromptEditor;