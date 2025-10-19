import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Globe, User, Settings, Bookmark, Heart, Bell, CreditCard, Download, Share2, Eye, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { BannerAd, PremiumMembership } from './AdSystem.jsx'

// Sample user data
const userData = {
  name: "Alex Johnson",
  email: "alex.johnson@email.com",
  memberSince: "January 2023",
  subscription: "Premium",
  avatar: null,
  preferences: {
    newsletter: true,
    pushNotifications: true,
    emailDigest: "weekly",
    categories: ["World Affairs", "Business", "Technology"]
  },
  stats: {
    articlesRead: 247,
    bookmarks: 23,
    likes: 156,
    commentsPosted: 12
  }
}

// Sample bookmarked articles
const bookmarkedArticles = [
  {
    id: 1,
    title: "The Future of Global Trade in an Uncertain World",
    category: "World Affairs",
    bookmarkedAt: "2024-01-15",
    readTime: "8 min read",
    image: "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=300&h=200&fit=crop"
  },
  {
    id: 4,
    title: "Sustainable Finance: Beyond ESG",
    category: "Business",
    bookmarkedAt: "2024-01-12",
    readTime: "7 min read",
    image: "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=300&h=200&fit=crop"
  }
]

// Sample reading history
const readingHistory = [
  {
    id: 3,
    title: "The Art of Slow Journalism",
    category: "Culture",
    readAt: "2024-01-14",
    readTime: "6 min read",
    progress: 100
  },
  {
    id: 2,
    title: "Design Renaissance in Post-Pandemic Cities",
    category: "Design",
    readAt: "2024-01-13",
    readTime: "7 min read",
    progress: 75
  }
]

export default function UserProfile() {
  const [activeTab, setActiveTab] = useState('overview')
  const [user, setUser] = useState(userData)
  const [isEditing, setIsEditing] = useState(false)

  const tabs = [
    { id: 'overview', label: 'Overview', icon: User },
    { id: 'bookmarks', label: 'Bookmarks', icon: Bookmark },
    { id: 'history', label: 'Reading History', icon: Clock },
    { id: 'preferences', label: 'Preferences', icon: Settings },
    { id: 'subscription', label: 'Subscription', icon: CreditCard }
  ]

  const handlePreferenceChange = (key, value) => {
    setUser(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        [key]: value
      }
    }))
  }

  return (
    <div className="min-h-screen bg-gray-50">
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
              <Link to="/">
                <Button variant="outline" size="sm">
                  Back to Home
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Profile Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center space-x-6">
            <div className="w-24 h-24 bg-gray-300 rounded-full flex items-center justify-center">
              {user.avatar ? (
                <img src={user.avatar} alt={user.name} className="w-24 h-24 rounded-full object-cover" />
              ) : (
                <User className="h-12 w-12 text-gray-600" />
              )}
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900">{user.name}</h1>
              <p className="text-gray-600">{user.email}</p>
              <p className="text-sm text-gray-500">Member since {user.memberSince}</p>
              <div className="flex items-center space-x-4 mt-2">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  user.subscription === 'Premium' 
                    ? 'bg-gold-100 text-gold-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {user.subscription} Member
                </span>
              </div>
            </div>
            <div className="text-right">
              <Button 
                onClick={() => setIsEditing(!isEditing)}
                variant="outline"
              >
                {isEditing ? 'Save Changes' : 'Edit Profile'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <nav className="space-y-1">
                {tabs.map((tab) => {
                  const Icon = tab.icon
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center px-4 py-3 text-left transition-colors ${
                        activeTab === tab.id
                          ? 'bg-red-50 text-red-600 border-r-2 border-red-600'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <Icon className="h-5 w-5 mr-3" />
                      {tab.label}
                    </button>
                  )
                })}
              </nav>
            </div>

            {/* Stats Card */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mt-6">
              <h3 className="text-lg font-bold text-gray-900 mb-4">Your Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Articles Read</span>
                  <span className="font-semibold">{user.stats.articlesRead}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Bookmarks</span>
                  <span className="font-semibold">{user.stats.bookmarks}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Likes Given</span>
                  <span className="font-semibold">{user.stats.likes}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Comments</span>
                  <span className="font-semibold">{user.stats.commentsPosted}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Account Overview</h2>
                  
                  {/* Recent Activity */}
                  <div className="mb-8">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
                    <div className="space-y-4">
                      <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <Bookmark className="h-5 w-5 text-blue-600" />
                        </div>
                        <div className="flex-1">
                          <p className="text-gray-900">Bookmarked "The Future of Global Trade"</p>
                          <p className="text-sm text-gray-500">2 hours ago</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                        <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                          <Heart className="h-5 w-5 text-red-600" />
                        </div>
                        <div className="flex-1">
                          <p className="text-gray-900">Liked "Sustainable Finance: Beyond ESG"</p>
                          <p className="text-sm text-gray-500">1 day ago</p>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Preferred Categories */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Interests</h3>
                    <div className="flex flex-wrap gap-2">
                      {user.preferences.categories.map((category, index) => (
                        <span 
                          key={index}
                          className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm"
                        >
                          {category}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Bookmarks Tab */}
              {activeTab === 'bookmarks' && (
                <div className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Bookmarked Articles</h2>
                    <span className="text-sm text-gray-500">{bookmarkedArticles.length} articles</span>
                  </div>
                  
                  <div className="space-y-4">
                    {bookmarkedArticles.map((article) => (
                      <div key={article.id} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                        <img 
                          src={article.image} 
                          alt={article.title}
                          className="w-20 h-20 object-cover rounded-md flex-shrink-0"
                        />
                        <div className="flex-1">
                          <Link to={`/article/${article.id}`}>
                            <h3 className="font-semibold text-gray-900 hover:text-red-600 transition-colors">
                              {article.title}
                            </h3>
                          </Link>
                          <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                            <span className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">
                              {article.category}
                            </span>
                            <span>{article.readTime}</span>
                            <span>Saved {article.bookmarkedAt}</span>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button variant="outline" size="sm">
                            <Share2 className="h-4 w-4" />
                          </Button>
                          <Button variant="outline" size="sm">
                            <Bookmark className="h-4 w-4 fill-current text-blue-600" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Reading History Tab */}
              {activeTab === 'history' && (
                <div className="p-6">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold text-gray-900">Reading History</h2>
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4 mr-2" />
                      Export
                    </Button>
                  </div>
                  
                  <div className="space-y-4">
                    {readingHistory.map((article) => (
                      <div key={article.id} className="p-4 border border-gray-200 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <Link to={`/article/${article.id}`}>
                            <h3 className="font-semibold text-gray-900 hover:text-red-600 transition-colors">
                              {article.title}
                            </h3>
                          </Link>
                          <span className="text-sm text-gray-500">{article.readAt}</span>
                        </div>
                        
                        <div className="flex items-center space-x-4 mb-3">
                          <span className="bg-gray-100 text-gray-800 px-2 py-1 rounded text-xs">
                            {article.category}
                          </span>
                          <span className="text-sm text-gray-500">{article.readTime}</span>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <div className="flex-1 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-red-600 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${article.progress}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-500">{article.progress}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Preferences Tab */}
              {activeTab === 'preferences' && (
                <div className="p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Preferences</h2>
                  
                  <div className="space-y-6">
                    {/* Notifications */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Notifications</h3>
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium text-gray-900">Newsletter</p>
                            <p className="text-sm text-gray-500">Receive our daily newsletter</p>
                          </div>
                          <input
                            type="checkbox"
                            checked={user.preferences.newsletter}
                            onChange={(e) => handlePreferenceChange('newsletter', e.target.checked)}
                            className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                          />
                        </div>
                        
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-medium text-gray-900">Push Notifications</p>
                            <p className="text-sm text-gray-500">Breaking news and updates</p>
                          </div>
                          <input
                            type="checkbox"
                            checked={user.preferences.pushNotifications}
                            onChange={(e) => handlePreferenceChange('pushNotifications', e.target.checked)}
                            className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Email Digest */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Email Digest</h3>
                      <select 
                        value={user.preferences.emailDigest}
                        onChange={(e) => handlePreferenceChange('emailDigest', e.target.value)}
                        className="border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500"
                      >
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                        <option value="never">Never</option>
                      </select>
                    </div>

                    {/* Categories */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Preferred Categories</h3>
                      <div className="grid grid-cols-2 gap-3">
                        {['World Affairs', 'Business', 'Technology', 'Culture', 'Design'].map((category) => (
                          <label key={category} className="flex items-center space-x-2">
                            <input
                              type="checkbox"
                              checked={user.preferences.categories.includes(category)}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  handlePreferenceChange('categories', [...user.preferences.categories, category])
                                } else {
                                  handlePreferenceChange('categories', user.preferences.categories.filter(c => c !== category))
                                }
                              }}
                              className="h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
                            />
                            <span className="text-gray-900">{category}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Subscription Tab */}
              {activeTab === 'subscription' && (
                <div className="p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">Subscription</h2>
                  
                  {user.subscription === 'Premium' ? (
                    <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 border border-yellow-200 rounded-lg p-6 mb-6">
                      <div className="flex items-center space-x-3 mb-4">
                        <div className="w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center">
                          <span className="text-white text-xl">👑</span>
                        </div>
                        <div>
                          <h3 className="text-xl font-bold text-gray-900">Premium Member</h3>
                          <p className="text-gray-600">Unlimited access to all content</p>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                        <div className="text-center">
                          <p className="text-2xl font-bold text-gray-900">∞</p>
                          <p className="text-sm text-gray-600">Articles per month</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-gray-900">0</p>
                          <p className="text-sm text-gray-600">Ads shown</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-gray-900">✓</p>
                          <p className="text-sm text-gray-600">Exclusive content</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-gray-900">Next billing: February 15, 2024</p>
                          <p className="text-sm text-gray-600">$9.99/month</p>
                        </div>
                        <Button variant="outline">Manage Subscription</Button>
                      </div>
                    </div>
                  ) : (
                    <PremiumMembership />
                  )}
                  
                  {/* Billing History */}
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Billing History</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">Premium Subscription</p>
                          <p className="text-sm text-gray-500">January 15, 2024</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-gray-900">$9.99</p>
                          <Button variant="outline" size="sm">Download</Button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

