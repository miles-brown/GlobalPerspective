import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { 
  Bot, 
  TrendingUp, 
  FileText, 
  Settings, 
  BarChart3, 
  Plus, 
  Search,
  Filter,
  RefreshCw,
  Eye,
  Edit,
  Trash2,
  Play,
  Pause,
  CheckCircle,
  XCircle,
  Clock,
  DollarSign,
  Users,
  Globe,
  Zap
} from 'lucide-react'
import './App.css'

// Mock API base URL - replace with actual backend URL
const API_BASE = 'http://localhost:5000/api/ai'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <div className="ml-64">
          <Header />
          <main className="p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/keywords" element={<KeywordManagement />} />
              <Route path="/trends" element={<TrendMonitoring />} />
              <Route path="/articles" element={<ArticleManagement />} />
              <Route path="/providers" element={<AIProviders />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

function Sidebar() {
  const location = useLocation()
  
  const navigation = [
    { name: 'Dashboard', href: '/', icon: BarChart3 },
    { name: 'Keywords', href: '/keywords', icon: Search },
    { name: 'Trends', href: '/trends', icon: TrendingUp },
    { name: 'Articles', href: '/articles', icon: FileText },
    { name: 'AI Providers', href: '/providers', icon: Bot },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  ]

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg">
      <div className="flex h-16 items-center px-6 border-b">
        <Globe className="h-8 w-8 text-red-600 mr-3" />
        <div>
          <h1 className="text-xl font-bold text-gray-900">AI Content</h1>
          <p className="text-sm text-gray-600">Dashboard</p>
        </div>
      </div>
      
      <nav className="mt-6 px-3">
        {navigation.map((item) => {
          const isActive = location.pathname === item.href
          return (
            <Link
              key={item.name}
              to={item.href}
              className={`flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 transition-colors ${
                isActive
                  ? 'bg-red-50 text-red-600'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </Link>
          )
        })}
      </nav>
    </div>
  )
}

function Header() {
  return (
    <header className="bg-white shadow-sm border-b h-16 flex items-center justify-between px-6">
      <h2 className="text-2xl font-semibold text-gray-900">AI Content Management</h2>
      <div className="flex items-center space-x-4">
        <button className="p-2 text-gray-500 hover:text-gray-700 rounded-md hover:bg-gray-100">
          <RefreshCw className="h-5 w-5" />
        </button>
        <button className="p-2 text-gray-500 hover:text-gray-700 rounded-md hover:bg-gray-100">
          <Settings className="h-5 w-5" />
        </button>
      </div>
    </header>
  )
}

function Dashboard() {
  const [stats, setStats] = useState({
    active_keywords: 0,
    trends_this_week: 0,
    total_articles: 0,
    published_articles: 0
  })
  const [recentTrends, setRecentTrends] = useState([])
  const [recentArticles, setRecentArticles] = useState([])

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE}/analytics/dashboard`)
      const data = await response.json()
      if (data.success) {
        setStats(data.analytics.counts)
        setRecentTrends(data.analytics.recent_trends)
        setRecentArticles(data.analytics.recent_articles)
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Active Keywords"
          value={stats.active_keywords}
          icon={Search}
          color="blue"
        />
        <StatCard
          title="Trends This Week"
          value={stats.trends_this_week}
          icon={TrendingUp}
          color="green"
        />
        <StatCard
          title="Total Articles"
          value={stats.total_articles}
          icon={FileText}
          color="purple"
        />
        <StatCard
          title="Published Articles"
          value={stats.published_articles}
          icon={CheckCircle}
          color="red"
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Trends</h3>
          <div className="space-y-3">
            {recentTrends.map((trend, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div>
                  <p className="font-medium text-gray-900 truncate">{trend.topic}</p>
                  <p className="text-sm text-gray-500">{trend.source}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{trend.engagement_score}</p>
                  <p className="text-xs text-gray-500">engagement</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Articles</h3>
          <div className="space-y-3">
            {recentArticles.map((article, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div>
                  <p className="font-medium text-gray-900 truncate">{article.title}</p>
                  <p className="text-sm text-gray-500">{article.category}</p>
                </div>
                <div className="text-right">
                  <StatusBadge status={article.status} />
                  <p className="text-xs text-gray-500 mt-1">{article.ai_provider}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-red-300 hover:bg-red-50 transition-colors">
            <Plus className="h-6 w-6 text-gray-400 mr-2" />
            <span className="text-gray-600">Add Keyword</span>
          </button>
          <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-300 hover:bg-green-50 transition-colors">
            <TrendingUp className="h-6 w-6 text-gray-400 mr-2" />
            <span className="text-gray-600">Monitor Trends</span>
          </button>
          <button className="flex items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors">
            <Zap className="h-6 w-6 text-gray-400 mr-2" />
            <span className="text-gray-600">Generate Article</span>
          </button>
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, icon: Icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    red: 'bg-red-50 text-red-600'
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-md ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="ml-4">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  )
}

function StatusBadge({ status }) {
  const statusConfig = {
    draft: { color: 'gray', text: 'Draft' },
    review: { color: 'yellow', text: 'Review' },
    approved: { color: 'green', text: 'Approved' },
    published: { color: 'blue', text: 'Published' },
    rejected: { color: 'red', text: 'Rejected' }
  }

  const config = statusConfig[status] || statusConfig.draft
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-${config.color}-100 text-${config.color}-800`}>
      {config.text}
    </span>
  )
}

function KeywordManagement() {
  const [keywords, setKeywords] = useState([])
  const [showAddForm, setShowAddForm] = useState(false)
  const [newKeyword, setNewKeyword] = useState({
    keyword: '',
    category: 'World Affairs',
    priority: 1
  })

  useEffect(() => {
    fetchKeywords()
  }, [])

  const fetchKeywords = async () => {
    try {
      const response = await fetch(`${API_BASE}/keywords`)
      const data = await response.json()
      if (data.success) {
        setKeywords(data.keywords)
      }
    } catch (error) {
      console.error('Failed to fetch keywords:', error)
    }
  }

  const addKeyword = async () => {
    try {
      const response = await fetch(`${API_BASE}/keywords`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newKeyword)
      })
      const data = await response.json()
      if (data.success) {
        setKeywords([...keywords, data.keyword])
        setNewKeyword({ keyword: '', category: 'World Affairs', priority: 1 })
        setShowAddForm(false)
      }
    } catch (error) {
      console.error('Failed to add keyword:', error)
    }
  }

  const deleteKeyword = async (id) => {
    try {
      const response = await fetch(`${API_BASE}/keywords/${id}`, {
        method: 'DELETE'
      })
      if (response.ok) {
        setKeywords(keywords.filter(k => k.id !== id))
      }
    } catch (error) {
      console.error('Failed to delete keyword:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Keyword Management</h2>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 flex items-center"
        >
          <Plus className="h-4 w-4 mr-2" />
          Add Keyword
        </button>
      </div>

      {showAddForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Add New Keyword</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Keyword"
              value={newKeyword.keyword}
              onChange={(e) => setNewKeyword({...newKeyword, keyword: e.target.value})}
              className="border border-gray-300 rounded-md px-3 py-2"
            />
            <select
              value={newKeyword.category}
              onChange={(e) => setNewKeyword({...newKeyword, category: e.target.value})}
              className="border border-gray-300 rounded-md px-3 py-2"
            >
              <option>World Affairs</option>
              <option>Business</option>
              <option>Technology</option>
              <option>Culture</option>
              <option>Design</option>
            </select>
            <select
              value={newKeyword.priority}
              onChange={(e) => setNewKeyword({...newKeyword, priority: parseInt(e.target.value)})}
              className="border border-gray-300 rounded-md px-3 py-2"
            >
              <option value={1}>Priority 1 (Low)</option>
              <option value={2}>Priority 2</option>
              <option value={3}>Priority 3 (Medium)</option>
              <option value={4}>Priority 4</option>
              <option value={5}>Priority 5 (High)</option>
            </select>
          </div>
          <div className="mt-4 flex space-x-3">
            <button
              onClick={addKeyword}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
            >
              Add Keyword
            </button>
            <button
              onClick={() => setShowAddForm(false)}
              className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-semibold">Active Keywords</h3>
        </div>
        <div className="divide-y">
          {keywords.map((keyword) => (
            <div key={keyword.id} className="px-6 py-4 flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">{keyword.keyword}</p>
                <p className="text-sm text-gray-500">{keyword.category} • Priority {keyword.priority}</p>
              </div>
              <div className="flex items-center space-x-2">
                <button className="text-blue-600 hover:text-blue-800">
                  <Edit className="h-4 w-4" />
                </button>
                <button
                  onClick={() => deleteKeyword(keyword.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function TrendMonitoring() {
  const [trends, setTrends] = useState([])
  const [isMonitoring, setIsMonitoring] = useState(false)

  useEffect(() => {
    fetchTrends()
  }, [])

  const fetchTrends = async () => {
    try {
      const response = await fetch(`${API_BASE}/trends`)
      const data = await response.json()
      if (data.success) {
        setTrends(data.trends)
      }
    } catch (error) {
      console.error('Failed to fetch trends:', error)
    }
  }

  const startMonitoring = async () => {
    setIsMonitoring(true)
    try {
      const response = await fetch(`${API_BASE}/trends/monitor`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hours_back: 24 })
      })
      const data = await response.json()
      if (data.success) {
        setTrends(data.trends)
      }
    } catch (error) {
      console.error('Failed to start monitoring:', error)
    } finally {
      setIsMonitoring(false)
    }
  }

  const generateArticle = async (trend) => {
    try {
      const response = await fetch(`${API_BASE}/articles/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: trend.topic,
          category: 'World Affairs',
          trend_id: trend.id,
          provider: 'openai'
        })
      })
      const data = await response.json()
      if (data.success) {
        alert('Article generated successfully!')
      }
    } catch (error) {
      console.error('Failed to generate article:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Trend Monitoring</h2>
        <button
          onClick={startMonitoring}
          disabled={isMonitoring}
          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 flex items-center disabled:opacity-50"
        >
          {isMonitoring ? (
            <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <Play className="h-4 w-4 mr-2" />
          )}
          {isMonitoring ? 'Monitoring...' : 'Start Monitoring'}
        </button>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-semibold">Trending Topics</h3>
        </div>
        <div className="divide-y">
          {trends.map((trend, index) => (
            <div key={index} className="px-6 py-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="font-medium text-gray-900 mb-2">{trend.topic}</p>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>Source: {trend.source}</span>
                    <span>Engagement: {trend.engagement_score}</span>
                    <span>Velocity: {trend.trend_velocity}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => generateArticle(trend)}
                    className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                  >
                    Generate Article
                  </button>
                  <button className="text-gray-400 hover:text-gray-600">
                    <Eye className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function ArticleManagement() {
  const [articles, setArticles] = useState([])

  useEffect(() => {
    fetchArticles()
  }, [])

  const fetchArticles = async () => {
    try {
      const response = await fetch(`${API_BASE}/articles`)
      const data = await response.json()
      if (data.success) {
        setArticles(data.articles)
      }
    } catch (error) {
      console.error('Failed to fetch articles:', error)
    }
  }

  const updateStatus = async (id, status) => {
    try {
      const response = await fetch(`${API_BASE}/articles/${id}/status`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      })
      if (response.ok) {
        fetchArticles()
      }
    } catch (error) {
      console.error('Failed to update status:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Article Management</h2>
        <div className="flex space-x-2">
          <select className="border border-gray-300 rounded-md px-3 py-2">
            <option>All Status</option>
            <option>Draft</option>
            <option>Review</option>
            <option>Approved</option>
            <option>Published</option>
          </select>
          <select className="border border-gray-300 rounded-md px-3 py-2">
            <option>All Categories</option>
            <option>World Affairs</option>
            <option>Business</option>
            <option>Technology</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="text-lg font-semibold">Generated Articles</h3>
        </div>
        <div className="divide-y">
          {articles.map((article) => (
            <div key={article.id} className="px-6 py-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900 mb-2">{article.title}</h4>
                  {article.subtitle && (
                    <p className="text-gray-600 mb-2">{article.subtitle}</p>
                  )}
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span>{article.category}</span>
                    <span>By {article.author_name}</span>
                    <span>{article.ai_provider}</span>
                    <span>{new Date(article.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <StatusBadge status={article.status} />
                  <select
                    value={article.status}
                    onChange={(e) => updateStatus(article.id, e.target.value)}
                    className="border border-gray-300 rounded px-2 py-1 text-sm"
                  >
                    <option value="draft">Draft</option>
                    <option value="review">Review</option>
                    <option value="approved">Approved</option>
                    <option value="published">Published</option>
                    <option value="rejected">Rejected</option>
                  </select>
                  <button className="text-blue-600 hover:text-blue-800">
                    <Edit className="h-4 w-4" />
                  </button>
                  <button className="text-gray-400 hover:text-gray-600">
                    <Eye className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function AIProviders() {
  const [providers, setProviders] = useState([])

  useEffect(() => {
    fetchProviders()
  }, [])

  const fetchProviders = async () => {
    try {
      const response = await fetch(`${API_BASE}/providers`)
      const data = await response.json()
      if (data.success) {
        setProviders(data.configured_providers)
      }
    } catch (error) {
      console.error('Failed to fetch providers:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">AI Providers</h2>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center">
          <Plus className="h-4 w-4 mr-2" />
          Add Provider
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {providers.map((provider) => (
          <div key={provider.id} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold capitalize">{provider.name}</h3>
              <div className={`w-3 h-3 rounded-full ${provider.is_active ? 'bg-green-500' : 'bg-gray-300'}`} />
            </div>
            <div className="space-y-2 text-sm text-gray-600">
              <p>Model: {provider.model_name}</p>
              <p>Cost: ${provider.cost_per_token}/token</p>
              <p>Max Tokens: {provider.max_tokens}</p>
              <p>Temperature: {provider.temperature}</p>
            </div>
            <div className="mt-4 flex flex-wrap gap-2">
              {provider.preferred_for_news && (
                <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">News</span>
              )}
              {provider.preferred_for_analysis && (
                <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">Analysis</span>
              )}
              {provider.preferred_for_opinion && (
                <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">Opinion</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function Analytics() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Content Generation Trends</h3>
          <div className="h-64 flex items-center justify-center text-gray-500">
            Chart placeholder - Integration with Recharts
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Provider Performance</h3>
          <div className="h-64 flex items-center justify-center text-gray-500">
            Chart placeholder - Integration with Recharts
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

