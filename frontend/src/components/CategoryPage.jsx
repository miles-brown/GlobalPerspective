import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Globe, Clock, User, TrendingUp, Filter } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { BannerAd, SidebarAd, NewsletterSubscription } from './AdSystem.jsx'

// Sample category data
const categoryData = {
  world: {
    name: "World Affairs",
    description: "Global politics, international relations, and world events",
    color: "red",
    articles: [
      {
        id: 1,
        title: "The Future of Global Trade in an Uncertain World",
        excerpt: "As geopolitical tensions rise and supply chains evolve, a new paradigm of global trade is emerging.",
        author: "Sarah Chen",
        publishedAt: "2024-01-15",
        readTime: "8 min read",
        featuredImage: "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=600&h=400&fit=crop",
        trending: true
      },
      {
        id: 7,
        title: "Diplomatic Relations in the Digital Age",
        excerpt: "How technology is reshaping international diplomacy and global communication.",
        author: "Ambassador Lisa Park",
        publishedAt: "2024-01-14",
        readTime: "6 min read",
        featuredImage: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop"
      }
    ]
  },
  business: {
    name: "Business",
    description: "Corporate news, market analysis, and economic insights",
    color: "blue",
    articles: [
      {
        id: 4,
        title: "Sustainable Finance: Beyond ESG",
        excerpt: "Financial institutions are developing new frameworks that go beyond traditional ESG metrics.",
        author: "David Kim",
        publishedAt: "2024-01-12",
        readTime: "7 min read",
        featuredImage: "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=600&h=400&fit=crop",
        trending: true
      }
    ]
  },
  technology: {
    name: "Technology",
    description: "Innovation, digital transformation, and tech industry news",
    color: "purple",
    articles: [
      {
        id: 5,
        title: "The New Diplomacy: Digital Statecraft",
        excerpt: "Traditional diplomatic channels are being supplemented by digital platforms.",
        author: "Ambassador Lisa Park",
        publishedAt: "2024-01-11",
        readTime: "5 min read",
        featuredImage: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop"
      }
    ]
  },
  culture: {
    name: "Culture",
    description: "Arts, society, lifestyle, and cultural trends",
    color: "green",
    articles: [
      {
        id: 3,
        title: "The Art of Slow Journalism",
        excerpt: "A growing movement of journalists and publications are choosing depth over immediacy.",
        author: "Elena Rodriguez",
        publishedAt: "2024-01-13",
        readTime: "6 min read",
        featuredImage: "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&h=400&fit=crop",
        trending: true
      },
      {
        id: 6,
        title: "Cultural Bridges: Art in Times of Division",
        excerpt: "Cultural institutions worldwide are fostering cross-cultural understanding.",
        author: "Dr. Amara Okafor",
        publishedAt: "2024-01-10",
        readTime: "8 min read",
        featuredImage: "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=600&h=400&fit=crop"
      }
    ]
  },
  design: {
    name: "Design",
    description: "Architecture, urban planning, and design innovation",
    color: "orange",
    articles: [
      {
        id: 2,
        title: "Design Renaissance in Post-Pandemic Cities",
        excerpt: "Cities worldwide are reimagining public spaces with a focus on mental health.",
        author: "Marcus Thompson",
        publishedAt: "2024-01-14",
        readTime: "7 min read",
        featuredImage: "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=600&h=400&fit=crop"
      }
    ]
  }
}

export default function CategoryPage() {
  const { category } = useParams()
  const [categoryInfo, setCategoryInfo] = useState(null)
  const [sortBy, setSortBy] = useState('latest')
  const [showFilters, setShowFilters] = useState(false)

  useEffect(() => {
    const info = categoryData[category?.toLowerCase()]
    if (info) {
      setCategoryInfo(info)
    }
  }, [category])

  if (!categoryInfo) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Category Not Found</h2>
          <Link to="/" className="text-red-600 hover:text-red-700">
            Return to Homepage
          </Link>
        </div>
      </div>
    )
  }

  const colorClasses = {
    red: 'bg-red-600 text-white',
    blue: 'bg-blue-600 text-white',
    purple: 'bg-purple-600 text-white',
    green: 'bg-green-600 text-white',
    orange: 'bg-orange-600 text-white'
  }

  const sortedArticles = [...categoryInfo.articles].sort((a, b) => {
    if (sortBy === 'latest') {
      return new Date(b.publishedAt) - new Date(a.publishedAt)
    } else if (sortBy === 'trending') {
      return (b.trending ? 1 : 0) - (a.trending ? 1 : 0)
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
              <Link to="/category/world" className={`font-medium transition-colors ${category === 'world' ? 'text-red-600' : 'text-gray-700 hover:text-red-600'}`}>World</Link>
              <Link to="/category/business" className={`font-medium transition-colors ${category === 'business' ? 'text-red-600' : 'text-gray-700 hover:text-red-600'}`}>Business</Link>
              <Link to="/category/technology" className={`font-medium transition-colors ${category === 'technology' ? 'text-red-600' : 'text-gray-700 hover:text-red-600'}`}>Technology</Link>
              <Link to="/category/culture" className={`font-medium transition-colors ${category === 'culture' ? 'text-red-600' : 'text-gray-700 hover:text-red-600'}`}>Culture</Link>
              <Link to="/category/design" className={`font-medium transition-colors ${category === 'design' ? 'text-red-600' : 'text-gray-700 hover:text-red-600'}`}>Design</Link>
            </nav>

            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm" className="border-red-600 text-red-600 hover:bg-red-50">
                Subscribe
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Category Header */}
      <div className={`${colorClasses[categoryInfo.color]} py-12`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold mb-4">{categoryInfo.name}</h1>
            <p className="text-xl opacity-90 max-w-2xl mx-auto">
              {categoryInfo.description}
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Articles List */}
          <div className="lg:col-span-3">
            {/* Filters and Sorting */}
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center space-x-4">
                <h2 className="text-2xl font-bold text-gray-900">
                  Latest in {categoryInfo.name}
                </h2>
                <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
                  {categoryInfo.articles.length} articles
                </span>
              </div>

              <div className="flex items-center space-x-4">
                <select 
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  <option value="latest">Latest</option>
                  <option value="trending">Trending</option>
                </select>

                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center space-x-2 px-3 py-2 border border-gray-300 rounded-md text-sm hover:bg-gray-50"
                >
                  <Filter className="h-4 w-4" />
                  <span>Filters</span>
                </button>
              </div>
            </div>

            {/* Articles Grid */}
            <div className="space-y-8">
              {sortedArticles.map((article, index) => (
                <article key={article.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
                  <div className="md:flex">
                    <div className="md:w-1/3">
                      <img 
                        src={article.featuredImage} 
                        alt={article.title}
                        className="w-full h-48 md:h-full object-cover"
                      />
                    </div>
                    <div className="md:w-2/3 p-6">
                      <div className="flex items-center space-x-4 mb-3">
                        <span className={`px-3 py-1 rounded text-sm font-medium ${colorClasses[categoryInfo.color]}`}>
                          {categoryInfo.name}
                        </span>
                        {article.trending && (
                          <div className="flex items-center text-orange-600">
                            <TrendingUp className="h-4 w-4 mr-1" />
                            <span className="text-sm font-medium">Trending</span>
                          </div>
                        )}
                      </div>

                      <Link to={`/article/${article.id}`}>
                        <h2 className="text-2xl font-bold text-gray-900 mb-3 hover:text-red-600 transition-colors">
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

            {/* Load More */}
            <div className="text-center mt-12">
              <Button variant="outline" className="border-gray-300 text-gray-700 hover:bg-gray-50">
                Load More Articles
              </Button>
            </div>

            {/* Newsletter Subscription */}
            <div className="mt-12">
              <NewsletterSubscription />
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-8">
              {/* Sidebar Ad */}
              <SidebarAd />

              {/* Trending in Category */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  Trending in {categoryInfo.name}
                </h3>
                <div className="space-y-4">
                  {categoryInfo.articles.filter(article => article.trending).map((article, index) => (
                    <div key={article.id} className="flex items-start space-x-3">
                      <span className="text-2xl font-bold text-red-600 leading-none">
                        {index + 1}
                      </span>
                      <div>
                        <Link to={`/article/${article.id}`}>
                          <h4 className="font-medium text-gray-900 text-sm leading-tight hover:text-red-600 cursor-pointer">
                            {article.title}
                          </h4>
                        </Link>
                        <p className="text-xs text-gray-500 mt-1">{article.readTime}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Category Stats */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Category Stats</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Articles</span>
                    <span className="font-semibold">{categoryInfo.articles.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">This Week</span>
                    <span className="font-semibold">3</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Trending</span>
                    <span className="font-semibold">{categoryInfo.articles.filter(a => a.trending).length}</span>
                  </div>
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

