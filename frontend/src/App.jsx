import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom'
import { Search, Menu, Globe, User, Settings, PenTool, Bell, Bookmark, Share2, Heart, MessageCircle } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import CMS from './components/CMS.jsx'
import EnhancedCommentSystem from './components/EnhancedCommentSystem.jsx'
import AdvancedSearchSystem from './components/AdvancedSearchSystem.jsx'
import WYSIWYGEditor from './components/WYSIWYGEditor.jsx'
import AdminDashboard from './components/AdminDashboard.jsx'
import { 
  BannerAd, 
  NativeAd, 
  PremiumMembership, 
  NewsletterSubscription, 
  SidebarAd,
  SponsoredMarker 
} from './components/AdSystem.jsx'
import ArticleDetail from './components/ArticleDetail.jsx'
import CategoryPage from './components/CategoryPage.jsx'
import SearchResults from './components/SearchResults.jsx'
import UserProfile from './components/UserProfile.jsx'
import './App.css'

// Sample data - in production this would come from the API
const sampleArticles = [
  {
    id: 1,
    title: "The Future of Global Trade in an Uncertain World",
    subtitle: "How emerging markets are reshaping international commerce",
    excerpt: "As geopolitical tensions rise and supply chains evolve, a new paradigm of global trade is emerging that challenges traditional economic models.",
    category: "World Affairs",
    author: "Sarah Chen",
    publishedAt: "2024-01-15",
    featuredImage: "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&h=600&fit=crop",
    isFeatured: true,
    isBreaking: false
  },
  {
    id: 2,
    title: "Design Renaissance in Post-Pandemic Cities",
    subtitle: "Urban planning meets human psychology",
    excerpt: "Cities worldwide are reimagining public spaces with a focus on mental health and community connection.",
    category: "Design",
    author: "Marcus Thompson",
    publishedAt: "2024-01-14",
    featuredImage: "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=600&h=400&fit=crop",
    isFeatured: false,
    isBreaking: false
  },
  {
    id: 3,
    title: "The Art of Slow Journalism",
    subtitle: "Quality over speed in the digital age",
    excerpt: "A growing movement of journalists and publications are choosing depth over immediacy.",
    category: "Culture",
    author: "Elena Rodriguez",
    publishedAt: "2024-01-13",
    featuredImage: "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&h=400&fit=crop",
    isFeatured: false,
    isBreaking: true
  },
  {
    id: 4,
    title: "Sustainable Finance: Beyond ESG",
    subtitle: "The next evolution of responsible investing",
    excerpt: "Financial institutions are developing new frameworks that go beyond traditional ESG metrics.",
    category: "Business",
    author: "David Kim",
    publishedAt: "2024-01-12",
    featuredImage: "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=600&h=400&fit=crop",
    isFeatured: false,
    isBreaking: false
  },
  {
    id: 5,
    title: "The New Diplomacy: Digital Statecraft",
    subtitle: "How nations navigate cyberspace politics",
    excerpt: "Traditional diplomatic channels are being supplemented by digital platforms and virtual negotiations.",
    category: "Technology",
    author: "Ambassador Lisa Park",
    publishedAt: "2024-01-11",
    featuredImage: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop",
    isFeatured: false,
    isBreaking: false
  },
  {
    id: 6,
    title: "Cultural Bridges: Art in Times of Division",
    subtitle: "Museums and galleries as spaces for dialogue",
    excerpt: "Cultural institutions worldwide are fostering cross-cultural understanding through innovative programming.",
    category: "Culture",
    author: "Dr. Amara Okafor",
    publishedAt: "2024-01-10",
    featuredImage: "https://images.unsplash.com/photo-1541961017774-22349e4a1262?w=600&h=400&fit=crop",
    isFeatured: false,
    isBreaking: false
  }
]

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/cms" element={<CMS />} />
          <Route path="/article/:id" element={<ArticleDetail />} />
          <Route path="/category/:category" element={<CategoryPage />} />
          <Route path="/search" element={<SearchResults />} />
          <Route path="/profile" element={<UserProfile />} />
          <Route path="/*" element={<NewsWebsite />} />
        </Routes>
      </div>
    </Router>
  )
}

function NewsWebsite() {
  const [articles] = useState(sampleArticles)
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const featuredArticle = articles.find(article => article.isFeatured)
  const breakingNews = articles.filter(article => article.isBreaking)
  const regularArticles = articles.filter(article => !article.isFeatured && !article.isBreaking)

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-200 bg-white sticky top-0 z-50">
        {/* Top Banner Ad */}
        <BannerAd position="top" size="leaderboard" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Globe className="h-8 w-8 text-red-600 mr-3" />
              <div>
                <h1 className="text-xl font-bold text-gray-900">Global Affairs</h1>
                <p className="text-xs text-gray-600">International News & Analysis</p>
              </div>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex space-x-8">
              <a href="#" className="text-gray-700 hover:text-red-600 font-medium transition-colors">World</a>
              <a href="#" className="text-gray-700 hover:text-red-600 font-medium transition-colors">Business</a>
              <a href="#" className="text-gray-700 hover:text-red-600 font-medium transition-colors">Technology</a>
              <a href="#" className="text-gray-700 hover:text-red-600 font-medium transition-colors">Culture</a>
              <a href="#" className="text-gray-700 hover:text-red-600 font-medium transition-colors">Design</a>
            </nav>

            {/* Right side */}
            <div className="flex items-center space-x-4">
              <Search className="h-5 w-5 text-gray-600 cursor-pointer hover:text-gray-900" />
              <User className="h-5 w-5 text-gray-600 cursor-pointer hover:text-gray-900" />
              <Button 
                variant="outline" 
                size="sm"
                className="hidden sm:inline-flex border-red-600 text-red-600 hover:bg-red-50"
              >
                Subscribe
              </Button>
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="md:hidden"
              >
                <Menu className="h-5 w-5 text-gray-600" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Breaking News Banner */}
      {breakingNews.length > 0 && (
        <div className="bg-red-600 text-white py-2">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center">
              <span className="bg-white text-red-600 px-2 py-1 rounded text-xs font-bold mr-3">
                BREAKING
              </span>
              <span className="text-sm font-medium">
                {breakingNews[0].title}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content Area */}
          <div className="lg:col-span-3">
            {/* Featured Article */}
            {featuredArticle && (
              <section className="mb-12">
                <article className="bg-white rounded-lg shadow-lg overflow-hidden">
                  <div className="relative">
                    <img 
                      src={featuredArticle.featuredImage} 
                      alt={featuredArticle.title}
                      className="w-full h-96 object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                    <div className="absolute bottom-0 left-0 right-0 p-8 text-white">
                      <span className="inline-block bg-red-600 text-white px-3 py-1 rounded text-sm font-medium mb-3">
                        {featuredArticle.category}
                      </span>
                      <h1 className="text-4xl font-bold mb-3">{featuredArticle.title}</h1>
                      {featuredArticle.subtitle && (
                        <h2 className="text-xl text-gray-200 mb-4">{featuredArticle.subtitle}</h2>
                      )}
                      <div className="flex items-center text-sm text-gray-300">
                        <span>{featuredArticle.author}</span>
                        <span className="mx-2">•</span>
                        <span>{featuredArticle.publishedAt}</span>
                      </div>
                    </div>
                  </div>
                </article>
              </section>
            )}

            {/* Premium Membership Promotion */}
            <PremiumMembership />

            {/* Article Grid */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-8">Latest Stories</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {regularArticles.slice(0, 4).map((article, index) => (
                  <div key={article.id}>
                    <ArticleCard article={article} />
                    {/* Insert Native Ad after 2nd article */}
                    {index === 1 && (
                      <div className="mt-8">
                        <NativeAd />
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>

            {/* Newsletter Subscription */}
            <NewsletterSubscription />

            {/* More Articles */}
            <section className="mb-12">
              <h2 className="text-2xl font-bold text-gray-900 mb-8">More Stories</h2>
              <div className="space-y-6">
                {regularArticles.slice(4).map((article) => (
                  <ArticleListItem key={article.id} article={article} />
                ))}
              </div>
            </section>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-24 space-y-8">
              {/* Sidebar Ad */}
              <SidebarAd />

              {/* Trending Section */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Trending Now</h3>
                <div className="space-y-4">
                  {articles.slice(0, 5).map((article, index) => (
                    <div key={article.id} className="flex items-start space-x-3">
                      <span className="text-2xl font-bold text-red-600 leading-none">
                        {index + 1}
                      </span>
                      <div>
                        <h4 className="font-medium text-gray-900 text-sm leading-tight hover:text-red-600 cursor-pointer">
                          {article.title}
                        </h4>
                        <p className="text-xs text-gray-500 mt-1">{article.category}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Another Sidebar Ad */}
              <div className="mt-8">
                <SidebarAd />
              </div>

              {/* Categories */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Categories</h3>
                <div className="space-y-2">
                  {['World Affairs', 'Business', 'Technology', 'Culture', 'Design'].map((category) => (
                    <a 
                      key={category}
                      href="#" 
                      className="block text-gray-700 hover:text-red-600 transition-colors"
                    >
                      {category}
                    </a>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center mb-4">
                <Globe className="h-6 w-6 text-red-600 mr-2" />
                <span className="text-lg font-bold">Global Affairs</span>
              </div>
              <p className="text-gray-400 text-sm">
                Independent journalism for a connected world. Delivering in-depth analysis and global perspectives.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Sections</h3>
              <div className="space-y-2 text-sm">
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">World Affairs</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Business</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Technology</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Culture</a>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <div className="space-y-2 text-sm">
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">About Us</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Careers</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Contact</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Advertise</a>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Connect</h3>
              <div className="space-y-2 text-sm">
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Newsletter</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">Twitter</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">LinkedIn</a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">RSS Feed</a>
              </div>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">
              © 2024 Global Affairs. All rights reserved.
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Privacy Policy</a>
              <a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Terms of Service</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

function ArticleCard({ article }) {
  return (
    <article className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <img 
        src={article.featuredImage} 
        alt={article.title}
        className="w-full h-48 object-cover"
      />
      <div className="p-6">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-red-600">{article.category}</span>
          {article.isBreaking && (
            <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-medium">
              BREAKING
            </span>
          )}
        </div>
        <h2 className="text-xl font-bold text-gray-900 mb-2 hover:text-red-600 transition-colors cursor-pointer">
          {article.title}
        </h2>
        {article.subtitle && (
          <h3 className="text-lg text-gray-600 mb-3">{article.subtitle}</h3>
        )}
        <p className="text-gray-700 mb-4 leading-relaxed">{article.excerpt}</p>
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>{article.author}</span>
          <span>{article.publishedAt}</span>
        </div>
      </div>
    </article>
  )
}

function ArticleListItem({ article }) {
  return (
    <article className="flex space-x-4 p-4 bg-white rounded-lg border border-gray-200 hover:shadow-sm transition-shadow">
      <img 
        src={article.featuredImage} 
        alt={article.title}
        className="w-24 h-24 object-cover rounded-md flex-shrink-0"
      />
      <div className="flex-1">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-xs font-medium text-red-600">{article.category}</span>
          {article.isBreaking && (
            <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs font-medium">
              BREAKING
            </span>
          )}
        </div>
        <h3 className="font-bold text-gray-900 mb-1 hover:text-red-600 transition-colors cursor-pointer">
          {article.title}
        </h3>
        <p className="text-gray-600 text-sm mb-2 line-clamp-2">{article.excerpt}</p>
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{article.author}</span>
          <span>{article.publishedAt}</span>
        </div>
      </div>
    </article>
  )
}

export default App
    category: "Business",
    author: "David Kim",
    publishedAt: "2024-01-12",
    featuredImage: "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=600&h=400&fit=crop",
    isFeatured: false,
    isBreaking: false
  }
]

const categories = [
  "Editorial", "World Affairs", "Business", "Culture", "Design", "Technology"
]

function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const location = useLocation()
  const isCMS = location.pathname === '/cms'

  return (
    <header className="border-b border-gray-200 bg-white/95 backdrop-blur sticky top-0 z-50">
      {/* Top Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-3 border-b border-gray-100">
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              {new Date().toLocaleDateString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
              })}
            </span>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" className="text-sm font-medium text-gray-700 hover:text-red-600">
              <User className="h-4 w-4 mr-2" />
              Sign In
            </Button>
            <Link to={isCMS ? "/" : "/cms"}>
              <Button variant="ghost" size="sm" className="text-sm font-medium text-gray-700 hover:text-red-600">
                <PenTool className="h-4 w-4 mr-2" />
                {isCMS ? "View Site" : "CMS"}
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between py-6">
          {/* Logo */}
          <Link to="/" className="flex items-center">
            <Globe className="h-8 w-8 text-red-600 mr-3" />
            <div>
              <h1 className="headline-secondary text-2xl font-bold tracking-tight text-gray-900">Global Affairs</h1>
              <p className="caption-text text-sm text-gray-600">News & World Analysis</p>
            </div>
          </Link>

          {/* Desktop Navigation - Hide on CMS */}
          {!isCMS && (
            <nav className="hidden md:flex items-center space-x-8">
              {categories.map((category, index) => (
                <a 
                  key={category} 
                  href="#" 
                  className={`navigation-text text-sm font-medium transition-colors duration-200 ${
                    index === 0 
                      ? "text-red-600" 
                      : "text-gray-700 hover:text-red-600"
                  }`}
                >
                  {category}
                </a>
              ))}
            </nav>
          )}

          {/* Search and Menu */}
          <div className="flex items-center space-x-4">
            {!isCMS && (
              <Button variant="ghost" size="sm">
                <Search className="h-5 w-5" />
              </Button>
            )}
            <Button 
              variant="ghost" 
              size="sm" 
              className="md:hidden"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && !isCMS && (
        <div className="md:hidden border-t border-gray-200 bg-white">
          <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex flex-col space-y-3">
              {categories.map((category, index) => (
                <a 
                  key={category} 
                  href="#" 
                  className={`text-sm font-medium transition-colors duration-200 ${
                    index === 0 
                      ? "text-red-600" 
                      : "text-gray-700 hover:text-red-600"
                  }`}
                >
                  {category}
                </a>
              ))}
            </div>
          </nav>
        </div>
      )}
    </header>
  )
}

function ArticleCard({ article, featured = false }) {
  const cardClass = featured 
    ? "bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-xl transition-shadow duration-300 md:col-span-2 lg:col-span-2" 
    : "bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow duration-300"
  
  return (
    <article className={cardClass}>
      <div className="relative">
        <img 
          src={article.featuredImage} 
          alt={article.title}
          className={`w-full object-cover ${featured ? 'h-80' : 'h-48'}`}
        />
        {article.isBreaking && (
          <span className="absolute top-4 left-4 bg-red-600 text-white px-3 py-1 text-xs font-semibold rounded">
            BREAKING
          </span>
        )}
        <div className="absolute top-4 right-4">
          <span className="bg-white/90 text-gray-900 px-2 py-1 text-xs font-medium rounded">
            {article.category}
          </span>
        </div>
      </div>
      
      <div className="p-6">
        <div className="mb-3">
          <span className="text-red-600 text-xs font-semibold uppercase tracking-wide">
            {article.category}
          </span>
        </div>
        
        <h2 className={`headline-primary font-semibold leading-tight mb-3 ${
          featured ? 'text-3xl lg:text-4xl' : 'text-xl md:text-2xl'
        }`}>
          <a href="#" className="hover:text-red-600 transition-colors duration-200">
            {article.title}
          </a>
        </h2>
        
        {article.subtitle && (
          <h3 className="headline-tertiary text-lg text-gray-600 mb-3 font-medium">
            {article.subtitle}
          </h3>
        )}
        
        <p className="body-text text-base leading-relaxed text-gray-600 mb-4 line-clamp-3">
          {article.excerpt}
        </p>
        
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span className="body-text-medium font-medium">{article.author}</span>
          <time className="caption-text" dateTime={article.publishedAt}>
            {new Date(article.publishedAt).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            })}
          </time>
        </div>
      </div>
    </article>
  )
}

function TrendingSection() {
  const trendingTopics = [
    "Global Supply Chains",
    "Climate Diplomacy", 
    "Digital Currency",
    "Urban Design",
    "Cultural Exchange"
  ]

  return (
    <aside className="bg-gray-50 rounded-lg p-6">
      <h3 className="headline-secondary text-xl md:text-2xl font-medium leading-snug mb-4">Trending</h3>
      <div className="space-y-3">
        {trendingTopics.map((topic, index) => (
          <div key={topic} className="flex items-center">
            <span className="text-red-600 font-bold text-sm mr-3 w-6">
              {String(index + 1).padStart(2, '0')}
            </span>
            <a href="#" className="body-text text-base leading-relaxed hover:text-red-600 transition-colors duration-200">
              {topic}
            </a>
          </div>
        ))}
      </div>
    </aside>
  )
}

function Newsletter() {
  return (
    <section className="bg-red-600 text-white rounded-lg p-8 text-center">
      <h3 className="headline-secondary text-xl md:text-2xl font-medium leading-snug mb-3">Stay Informed</h3>
      <p className="body-text text-base leading-relaxed mb-6 opacity-90">
        Get our weekly digest of global affairs and analysis delivered to your inbox.
      </p>
      <div className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
        <input 
          type="email" 
          placeholder="Enter your email"
          className="flex-1 px-4 py-2 rounded-md text-gray-900 bg-white border border-gray-200"
        />
        <Button variant="secondary" className="whitespace-nowrap">
          Subscribe
        </Button>
      </div>
    </section>
  )
}

function Footer() {
  return (
    <footer className="bg-gray-50 border-t border-gray-200 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2">
            <div className="flex items-center mb-4">
              <Globe className="h-6 w-6 text-red-600 mr-2" />
              <span className="headline-secondary text-xl font-bold">Global Affairs</span>
            </div>
            <p className="body-text text-base leading-relaxed text-gray-600 mb-4">
              Independent journalism for a connected world. We provide in-depth analysis 
              of global events, culture, and the forces shaping our future.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-500 hover:text-red-600">Twitter</a>
              <a href="#" className="text-gray-500 hover:text-red-600">LinkedIn</a>
              <a href="#" className="text-gray-500 hover:text-red-600">RSS</a>
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Sections</h4>
            <div className="space-y-2">
              {categories.map(category => (
                <a key={category} href="#" className="block text-gray-500 hover:text-red-600">
                  {category}
                </a>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">About</h4>
            <div className="space-y-2">
              <a href="#" className="block text-gray-500 hover:text-red-600">Our Team</a>
              <a href="#" className="block text-gray-500 hover:text-red-600">Editorial Standards</a>
              <a href="#" className="block text-gray-500 hover:text-red-600">Contact</a>
              <a href="#" className="block text-gray-500 hover:text-red-600">Careers</a>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-200 mt-8 pt-8 text-center">
          <p className="text-sm text-gray-500">
            © 2024 Global Affairs. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  )
}

function HomePage() {
  const [articles, setArticles] = useState(sampleArticles)
  const featuredArticle = articles.find(article => article.isFeatured)
  const regularArticles = articles.filter(article => !article.isFeatured)

  return (
    <main>
      {/* Featured Article Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            {featuredArticle && <ArticleCard article={featuredArticle} featured={true} />}
          </div>
          <div className="space-y-6">
            <TrendingSection />
            <Newsletter />
          </div>
        </div>
      </section>

      {/* Articles Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
          {regularArticles.map(article => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      </section>

      {/* Load More */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center">
        <Button variant="outline" size="lg">
          Load More Articles
        </Button>
      </section>
    </main>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-white">
        <Header />
        
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/cms" element={<CMS />} />
        </Routes>

        <Footer />
      </div>
    </Router>
  )
}

export default App

