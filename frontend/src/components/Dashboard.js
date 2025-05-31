import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import {
  BookOpenIcon,
  PlusIcon,
  SparklesIcon,
  ChartBarIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function Dashboard() {
  const [stats, setStats] = useState({
    totalPrompts: 0,
    userPrompts: 0,
    categories: [],
    recentPrompts: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [promptsResponse, categoriesResponse] = await Promise.all([
        axios.get(`${API}/prompts`),
        axios.get(`${API}/prompts/categories`)
      ]);

      const allPrompts = [...promptsResponse.data.internal, ...promptsResponse.data.external];
      const userPrompts = allPrompts.filter(p => p.source === 'user');
      const recentPrompts = allPrompts
        .filter(p => p.created_at || p.updated_at)
        .sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at))
        .slice(0, 5);

      setStats({
        totalPrompts: allPrompts.length,
        userPrompts: userPrompts.length,
        categories: categoriesResponse.data,
        recentPrompts
      });
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
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
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Tableau de bord</h1>
        <p className="mt-2 text-gray-600">
          Bienvenue dans votre bibliothèque de prompts IA pour la filière Achat
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BookOpenIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total prompts
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.totalPrompts}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <SparklesIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Mes prompts
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.userPrompts}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <ChartBarIcon className="h-6 w-6 text-gray-400" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Catégories
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.categories.length}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Actions rapides
          </h3>
          <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Link
              to="/prompts"
              className="relative block w-full border-2 border-gray-300 border-dashed rounded-lg p-6 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              <BookOpenIcon className="mx-auto h-12 w-12 text-gray-400" />
              <span className="mt-2 block text-sm font-medium text-gray-900">
                Parcourir la bibliothèque
              </span>
              <span className="mt-1 block text-xs text-gray-500">
                Explorez tous les prompts disponibles
              </span>
            </Link>

            <Link
              to="/prompts/new"
              className="relative block w-full border-2 border-gray-300 border-dashed rounded-lg p-6 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              <PlusIcon className="mx-auto h-12 w-12 text-gray-400" />
              <span className="mt-2 block text-sm font-medium text-gray-900">
                Créer un nouveau prompt
              </span>
              <span className="mt-1 block text-xs text-gray-500">
                Ajoutez votre propre prompt personnalisé
              </span>
            </Link>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      {stats.recentPrompts.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Prompts récents
            </h3>
            <div className="space-y-3">
              {stats.recentPrompts.map((prompt) => (
                <div key={prompt.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${prompt.type === 'internal' ? 'bg-green-100' : 'bg-blue-100'}`}>
                      {prompt.type === 'internal' ? (
                        <SparklesIcon className={`h-4 w-4 ${prompt.type === 'internal' ? 'text-green-600' : 'text-blue-600'}`} />
                      ) : (
                        <ClockIcon className={`h-4 w-4 ${prompt.type === 'internal' ? 'text-green-600' : 'text-blue-600'}`} />
                      )}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{prompt.title}</p>
                      <p className="text-xs text-gray-500">
                        {prompt.category} • {prompt.type === 'internal' ? 'Interne' : 'Externe'}
                      </p>
                    </div>
                  </div>
                  <Link
                    to={`/prompts/${prompt.id}/execute`}
                    className="text-blue-600 hover:text-blue-500 text-sm font-medium"
                  >
                    Utiliser
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Categories Overview */}
      {stats.categories.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Catégories disponibles
            </h3>
            <div className="flex flex-wrap gap-2">
              {stats.categories.map((category) => (
                <span
                  key={category}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-700"
                >
                  {category}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;