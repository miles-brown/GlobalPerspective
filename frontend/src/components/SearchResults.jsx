import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { Globe, Search, Clock, User, Filter, X } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { BannerAd, SidebarAd } from './AdSystem.jsx'

// Sample search results data
const sampleResults = [
  {
    id: 1,
    title: "The Future of Global Trade in an Uncertain World",
    excerpt: "As geopolitical tensions rise and supply chains evolve, a new paradigm of global trade is emerging that challenges traditional economic models.",
    author: "Sarah Chen",
    publishedAt: "2024-01-15",
    readTime: "8 min read",
    category: "World Affairs",
    featuredImage: "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=400&h=200&fit=crop",
    relevanceScore: 95
  },
  {
    id: 4,
    title: "Sustainable Finance: Beyond ESG",
    excerpt: "Financial institutions are developing new frameworks that go beyond traditional ESG metrics to measure environmental and social impact.",
    author: "David Kim",
    publishedAt: "2024-01-12",
    readTime: "7 min read",
    category: "Business",
    featuredImage: "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=400&h=200&fit=crop",
    relevanceScore: 87
  },
  {
    id: 5,
    title: "The New Diplomacy: Digital Statecraft",
    excerpt: "Traditional diplomatic channels are being supplemented by digital platforms and virtual negotiations in the modern era.",
    author: "Ambassador Lisa Park",
    publishedAt: "2024-01-11",
    readTime: "5 min read",
    category: "Technology",
    featuredImage: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=200&fit=crop",
    relevanceScore: 82
  }
]

export default function SearchResults() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('q') || '')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [filters, setFilters] = useState({
    category: '',
    dateRange: '',
    sortBy: 'relevance'
  })
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    const searchQuery = searchParams.get('q')
    if (searchQuery) {
      setQuery(searchQuery)
      performSearch(searchQuery)
    }
  }, [searchParams])

  const performSearch = async (searchQuery) => {
    setLoading(true)
    // Simulate API call
    setTimeout(() => {
      // Filter sample results based on query
      const filteredResults = sampleResults.filter(article =>
        article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        article.excerpt.toLowerCase().includes(searchQuery.toLowerCase()) ||
        article.category.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setResults(filteredResults)
      setLoading(false)
    }, 500)
  }

  const handleSearch = (e) => {
    e.preventDefault()
    if (query.trim()) {
      setSearchParams({ q: query.trim() })
    }
  }

  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({
      ...prev,
      [filterType]: value
    }))
  }

  const clearFilters = () => {
    setFilters({
      category: '',
      dateRange: '',
      sortBy: 'relevance'
    })
  }

  const filteredResults = results.filter(article => {
    if (filters.category && article.category !== filters.category) return false
    // Add more filter logic here
    return true
  }).sort((a, b) => {
    if (filters.sortBy === 'relevance') {
      return b.relevanceScore - a.relevanceScore
    } else if (filters.sortBy === 'date') {
      return new Date(b.publishedAt) - new Date(a.publishedAt)
    }
    return 0
  })

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
        <BannerAd position="top" size="leaderboard" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center">
              <Globe className="h-8 w-8 text-red-600 mr-3" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Global Affairs</h1>
                <p className="text-xs text-gray-600">International News & Analysis</p>
              </div>
            </Link>

            <nav className="hidden md:flex space-x-8">
              <Link to="/category/world" className="text-gray-700 hover:text-red-600 font-medium transition-colors">World</Link>
              <Link to="/category/business" className="text-gray-700 hover:text-red-600 font-medium transition-colors">Business</Link>
              <Link to="/category/technology" className="text-gray-700 hover:text-red-600 font-medium transition-colors">Technology</Link>
              <Link to="/category/culture" className="text-gray-700 hover:text-red-600 font-medium transition-colors">Culture</Link>
              <Link to="/category/design" className="text-gray-700 hover:text-red-600 font-medium transition-colors">Design</Link>
            </nav>

            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm" className="border-red-600 text-red-600 hover:bg-red-50">
                Subscribe
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Search Header */}
      <div className="bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Search Results</h1>
            <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
              <div className="relative">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search articles, topics, authors..."
                  className="w-full px-4 py-3 pl-12 pr-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Button 
                  type="submit"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-red-600 hover:bg-red-700"
                >
                  Search
                </Button>
              </div>
            </form>
          </div>

          {query && (
            <div className="text-center">
              <p className="text-gray-600">
                {loading ? 'Searching...' : `${filteredResults.length} results for "${query}"`}
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Search Results */}
          <div className="lg:col-span-3">
            {/* Filters Bar */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-md text-sm hover:bg-gray-50"
                >
                  <Filter className="h-4 w-4" />
                  <span>Filters</span>
                </button>

                {(filters.category || filters.dateRange) && (
                  <button
                    onClick={clearFilters}
                    className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900"
                  >
                    <X className="h-4 w-4" />
                    <span>Clear filters</span>
                  </button>
                )}
              </div>

              <select 
                value={filters.sortBy}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                <option value="relevance">Most Relevant</option>
                <option value="date">Most Recent</option>
              </select>
            </div>

            {/* Filters Panel */}
            {showFilters && (
              <div className="bg-gray-50 rounded-lg p-6 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                    <select 
                      value={filters.category}
                      onChange={(e) => handleFilterChange('category', e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                    >
                      <option value="">All Categories</option>
                      <option value="World Affairs">World Affairs</option>
                      <option value="Business">Business</option>
                      <option value="Technology">Technology</option>
                      <option value="Culture">Culture</option>
                      <option value="Design">Design</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
                    <select 
                      value={filters.dateRange}
                      onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                    >
                      <option value="">All Time</option>
                      <option value="today">Today</option>
                      <option value="week">This Week</option>
                      <option value="month">This Month</option>
                      <option value="year">This Year</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Author</label>
                    <input
                      type="text"
                      placeholder="Search by author"
                      className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Results */}
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mx-auto"></div>
                <p className="text-gray-600 mt-4">Searching...</p>
              </div>
            ) : filteredResults.length > 0 ? (
              <div className="space-y-6">
                {filteredResults.map((article) => (
                  <article key={article.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
                    <div className="md:flex">
                      <div className="md:w-1/4">
                        <img 
                          src={article.featuredImage} 
                          alt={article.title}
                          className="w-full h-48 md:h-full object-cover"
                        />
                      </div>
                      <div className="md:w-3/4 p-6">
                        <div className="flex items-center space-x-4 mb-3">
                          <span className="bg-red-600 text-white px-3 py-1 rounded text-sm font-medium">
                            {article.category}
                          </span>
                          <div className="flex items-center text-sm text-gray-500">
                            <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                              {article.relevanceScore}% match
                            </span>
                          </div>
                        </div>

                        <Link to={`/article/${article.id}`}>
                          <h2 className="text-xl font-bold text-gray-900 mb-3 hover:text-red-600 transition-colors">
                            {article.title}
                          </h2>
                        </Link>

                        <p className="text-gray-700 mb-4 leading-relaxed">
                          {article.excerpt}
                        </p>

                        <div className="flex items-center justify-between text-sm text-gray-500">
                          <div className="flex items-center space-x-4">
                            <div className="flex items-center">
                              <User className="h-4 w-4 mr-1" />
                              {article.author}
                            </div>
                            <div className="flex items-center">
                              <Clock className="h-4 w-4 mr-1" />
                              {article.readTime}
                            </div>
                          </div>
                          <span>{article.publishedAt}</span>
                        </div>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            ) : query ? (
              <div className="text-center py-12">
                <Search className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No results found</h3>
                <p className="text-gray-600 mb-6">
                  We couldn't find any articles matching "{query}". Try different keywords or browse our categories.
                </p>
                <div className="flex justify-center space-x-4">
                  <Link to="/category/world">
                    <Button variant="outline">Browse World Affairs</Button>
                  </Link>
                  <Link to="/category/business">
                    <Button variant="outline">Browse Business</Button>
                  </Link>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <Search className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Start your search</h3>
                <p className="text-gray-600">
                  Enter keywords to find articles, topics, or authors.
                </p>
              </div>
            )}

            {/* Pagination */}
            {filteredResults.length > 0 && (
              <div className="flex justify-center mt-12">
                <div className="flex space-x-2">
                  <Button variant="outline" disabled>Previous</Button>
                  <Button className="bg-red-600 hover:bg-red-700">1</Button>
                  <Button variant="outline">2</Button>
                  <Button variant="outline">3</Button>
                  <Button variant="outline">Next</Button>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-8">
              {/* Sidebar Ad */}
              <SidebarAd />

              {/* Popular Searches */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Popular Searches</h3>
                <div className="space-y-2">
                  <button className="block w-full text-left text-sm text-gray-600 hover:text-red-600 transition-colors">
                    Global trade
                  </button>
                  <button className="block w-full text-left text-sm text-gray-600 hover:text-red-600 transition-colors">
                    Digital diplomacy
                  </button>
                  <button className="block w-full text-left text-sm text-gray-600 hover:text-red-600 transition-colors">
                    Sustainable finance
                  </button>
                  <button className="block w-full text-left text-sm text-gray-600 hover:text-red-600 transition-colors">
                    Urban design
                  </button>
                  <button className="block w-full text-left text-sm text-gray-600 hover:text-red-600 transition-colors">
                    Cultural diplomacy
                  </button>
                </div>
              </div>

              {/* Search Tips */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Search Tips</h3>
                <div className="space-y-3 text-sm text-gray-600">
                  <p>• Use quotes for exact phrases: "global trade"</p>
                  <p>• Use + to require words: trade +emerging</p>
                  <p>• Use - to exclude words: trade -domestic</p>
                  <p>• Search by author name or category</p>
                </div>
              </div>

              {/* Another Sidebar Ad */}
              <SidebarAd />
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

