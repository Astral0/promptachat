import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  PlusIcon,
  PlayIcon,
  PencilIcon,
  DocumentDuplicateIcon,
  TrashIcon,
  ExternalLinkIcon,
  ComputerDesktopIcon
} from '@heroicons/react/24/outline';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function PromptLibrary() {
  const [prompts, setPrompts] = useState({ internal: [], external: [] });
  const [filteredPrompts, setFilteredPrompts] = useState({ internal: [], external: [] });
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedType, setSelectedType] = useState('all');

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    filterPrompts();
  }, [prompts, searchQuery, selectedCategory, selectedType]);

  const loadData = async () => {
    try {
      const [promptsResponse, categoriesResponse] = await Promise.all([
        axios.get(`${API}/prompts`),
        axios.get(`${API}/prompts/categories`)
      ]);

      setPrompts(promptsResponse.data);
      setCategories(categoriesResponse.data);
    } catch (error) {
      console.error('Error loading prompts:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterPrompts = () => {
    const filtered = { internal: [], external: [] };

    ['internal', 'external'].forEach(type => {
      if (selectedType === 'all' || selectedType === type) {
        filtered[type] = prompts[type].filter(prompt => {
          const matchesSearch = prompt.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                               prompt.content.toLowerCase().includes(searchQuery.toLowerCase());
          const matchesCategory = !selectedCategory || prompt.category === selectedCategory;
          return matchesSearch && matchesCategory;
        });
      }
    });

    setFilteredPrompts(filtered);
  };

  const handleDuplicate = async (promptId) => {
    try {
      await axios.post(`${API}/prompts/${promptId}/duplicate`);
      loadData(); // Reload to show new prompt
    } catch (error) {
      console.error('Error duplicating prompt:', error);
    }
  };

  const handleDelete = async (promptId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer ce prompt ?')) {
      try {
        await axios.delete(`${API}/prompts/${promptId}`);
        loadData(); // Reload to remove deleted prompt
      } catch (error) {
        console.error('Error deleting prompt:', error);
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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Bibliothèque de Prompts</h1>
          <p className="mt-2 text-gray-600">
            Explorez et utilisez les prompts disponibles pour vos tâches d'achat
          </p>
        </div>
        <Link
          to="/prompts/new"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Nouveau prompt
        </Link>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Rechercher un prompt..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          {/* Category filter */}
          <div className="relative">
            <select
              className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="">Toutes les catégories</option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>

          {/* Type filter */}
          <div className="relative">
            <select
              className="block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 rounded-md"
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
            >
              <option value="all">Tous les types</option>
              <option value="internal">Prompts internes</option>
              <option value="external">Prompts externes</option>
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="space-y-6">
        {/* Internal Prompts */}
        {(selectedType === 'all' || selectedType === 'internal') && filteredPrompts.internal.length > 0 && (
          <PromptSection
            title="Prompts Internes"
            subtitle="Exécutés directement avec les LLMs internes"
            prompts={filteredPrompts.internal}
            type="internal"
            onDuplicate={handleDuplicate}
            onDelete={handleDelete}
          />
        )}

        {/* External Prompts */}
        {(selectedType === 'all' || selectedType === 'external') && filteredPrompts.external.length > 0 && (
          <PromptSection
            title="Prompts Externes"
            subtitle="Génèrent du texte pour les plateformes IA externes"
            prompts={filteredPrompts.external}
            type="external"
            onDuplicate={handleDuplicate}
            onDelete={handleDelete}
          />
        )}

        {/* No results */}
        {filteredPrompts.internal.length === 0 && filteredPrompts.external.length === 0 && (
          <div className="text-center py-12">
            <FunnelIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Aucun prompt trouvé</h3>
            <p className="mt-1 text-sm text-gray-500">
              Essayez de modifier vos critères de recherche
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function PromptSection({ title, subtitle, prompts, type, onDuplicate, onDelete }) {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center">
          {type === 'internal' ? (
            <ComputerDesktopIcon className="h-6 w-6 text-green-600 mr-3" />
          ) : (
            <ExternalLinkIcon className="h-6 w-6 text-blue-600 mr-3" />
          )}
          <div>
            <h3 className="text-lg font-medium text-gray-900">{title}</h3>
            <p className="text-sm text-gray-500">{subtitle}</p>
          </div>
        </div>
      </div>

      <div className="divide-y divide-gray-200">
        {prompts.map((prompt) => (
          <PromptCard
            key={prompt.id}
            prompt={prompt}
            type={type}
            onDuplicate={onDuplicate}
            onDelete={onDelete}
          />
        ))}
      </div>
    </div>
  );
}

function PromptCard({ prompt, type, onDuplicate, onDelete }) {
  return (
    <div className="p-6 hover:bg-gray-50 transition-colors">
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-3">
            <h4 className="text-lg font-medium text-gray-900 truncate">
              {prompt.title}
            </h4>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
              prompt.source === 'system' 
                ? 'bg-gray-100 text-gray-800' 
                : 'bg-blue-100 text-blue-800'
            }`}>
              {prompt.source === 'system' ? 'Système' : 'Utilisateur'}
            </span>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
              {prompt.category}
            </span>
          </div>
          
          <p className="mt-2 text-sm text-gray-600 line-clamp-2">
            {prompt.content.substring(0, 200)}...
          </p>

          {prompt.variables && prompt.variables.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1">
              {prompt.variables.map((variable) => (
                <span
                  key={variable}
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800"
                >
                  {variable}
                </span>
              ))}
            </div>
          )}

          <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
            {prompt.accepts_files && (
              <span className="flex items-center">
                📎 Accepte les fichiers
              </span>
            )}
            {prompt.needs_cockpit && (
              <span className="flex items-center">
                🔗 Données Cockpit
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2 ml-4">
          <Link
            to={`/prompts/${prompt.id}/execute`}
            className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            title="Exécuter le prompt"
          >
            <PlayIcon className="h-4 w-4" />
          </Link>

          {prompt.editable && (
            <Link
              to={`/prompts/${prompt.id}/edit`}
              className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              title="Modifier le prompt"
            >
              <PencilIcon className="h-4 w-4" />
            </Link>
          )}

          <button
            onClick={() => onDuplicate(prompt.id)}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            title="Dupliquer le prompt"
          >
            <DocumentDuplicateIcon className="h-4 w-4" />
          </button>

          {prompt.editable && (
            <button
              onClick={() => onDelete(prompt.id)}
              className="inline-flex items-center px-3 py-1.5 border border-red-300 text-xs font-medium rounded-md text-red-700 bg-white hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              title="Supprimer le prompt"
            >
              <TrashIcon className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default PromptLibrary;