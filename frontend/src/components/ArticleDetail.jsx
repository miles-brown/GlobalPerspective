import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Share2, Bookmark, Heart, MessageCircle, Clock, User, Calendar, Tag } from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { BannerAd, SidebarAd, NewsletterSubscription, PremiumMembership } from './AdSystem.jsx'

// Sample article data - in production this would come from API
const sampleArticleContent = {
  1: {
    title: "The Future of Global Trade in an Uncertain World",
    subtitle: "How emerging markets are reshaping international commerce",
    content: `
      <p>As geopolitical tensions rise and supply chains evolve, a new paradigm of global trade is emerging that challenges traditional economic models. The interconnected world of commerce is experiencing unprecedented shifts that require careful analysis and strategic adaptation.</p>
      
      <h2>The Changing Landscape</h2>
      <p>The global trade environment has undergone significant transformation in recent years. Traditional trade routes are being reimagined, new economic partnerships are forming, and emerging markets are asserting their influence on the international stage.</p>
      
      <p>Supply chain resilience has become a critical factor in international business strategy. Companies are diversifying their supplier networks and investing in regional production capabilities to reduce dependency on single-source suppliers.</p>
      
      <h2>Emerging Market Influence</h2>
      <p>Countries in Asia, Africa, and Latin America are no longer just participants in global trade—they are becoming key drivers of economic policy and innovation. Their growing middle classes represent massive consumer markets that multinational corporations cannot ignore.</p>
      
      <p>Digital transformation is accelerating trade facilitation, with blockchain technology, AI-powered logistics, and digital payment systems revolutionizing how international commerce operates.</p>
      
      <h2>Future Implications</h2>
      <p>The future of global trade will likely be characterized by greater regionalization, increased focus on sustainability, and the continued rise of digital commerce platforms. Organizations that adapt to these changes will thrive in the new economic landscape.</p>
      
      <p>Environmental considerations are becoming integral to trade policy, with carbon footprint assessments and sustainable sourcing requirements influencing international business decisions.</p>
    `,
    author: "Sarah Chen",
    publishedAt: "2024-01-15",
    readTime: "8 min read",
    category: "World Affairs",
    tags: ["Global Trade", "Economics", "Emerging Markets", "Supply Chain"],
    featuredImage: "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&h=600&fit=crop",
    likes: 234,
    comments: 45,
    shares: 67
  }
}

export default function ArticleDetail() {
  const { id } = useParams()
  const [article, setArticle] = useState(null)
  const [isLiked, setIsLiked] = useState(false)
  const [isBookmarked, setIsBookmarked] = useState(false)
  const [showShareMenu, setShowShareMenu] = useState(false)

  useEffect(() => {
    // In production, fetch article from API
    const articleData = sampleArticleContent[id]
    if (articleData) {
      setArticle(articleData)
    }
  }, [id])

  if (!article) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Article Not Found</h2>
          <Link to="/" className="text-red-600 hover:text-red-700">
            Return to Homepage
          </Link>
        </div>
      </div>
    )
  }

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

      {/* Article Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Article */}
          <div className="lg:col-span-3">
            {/* Back Navigation */}
            <div className="mb-6">
              <Link 
                to="/" 
                className="inline-flex items-center text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Homepage
              </Link>
            </div>

            {/* Article Header */}
            <article className="bg-white">
              <div className="mb-6">
                <div className="flex items-center space-x-4 mb-4">
                  <span className="bg-red-600 text-white px-3 py-1 rounded text-sm font-medium">
                    {article.category}
                  </span>
                  <div className="flex items-center text-sm text-gray-500 space-x-4">
                    <div className="flex items-center">
                      <Clock className="h-4 w-4 mr-1" />
                      {article.readTime}
                    </div>
                    <div className="flex items-center">
                      <Calendar className="h-4 w-4 mr-1" />
                      {article.publishedAt}
                    </div>
                  </div>
                </div>

                <h1 className="text-4xl font-bold text-gray-900 mb-4 leading-tight">
                  {article.title}
                </h1>
                
                {article.subtitle && (
                  <h2 className="text-xl text-gray-600 mb-6 leading-relaxed">
                    {article.subtitle}
                  </h2>
                )}

                {/* Author and Social Actions */}
                <div className="flex items-center justify-between py-4 border-y border-gray-200">
                  <div className="flex items-center">
                    <div className="w-12 h-12 bg-gray-300 rounded-full flex items-center justify-center mr-4">
                      <User className="h-6 w-6 text-gray-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">{article.author}</p>
                      <p className="text-sm text-gray-500">Senior International Correspondent</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => setIsLiked(!isLiked)}
                      className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors ${
                        isLiked ? 'bg-red-50 text-red-600' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <Heart className={`h-4 w-4 ${isLiked ? 'fill-current' : ''}`} />
                      <span className="text-sm">{article.likes + (isLiked ? 1 : 0)}</span>
                    </button>

                    <button
                      onClick={() => setIsBookmarked(!isBookmarked)}
                      className={`p-2 rounded-md transition-colors ${
                        isBookmarked ? 'bg-blue-50 text-blue-600' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'
                      }`}
                    >
                      <Bookmark className={`h-4 w-4 ${isBookmarked ? 'fill-current' : ''}`} />
                    </button>

                    <div className="relative">
                      <button
                        onClick={() => setShowShareMenu(!showShareMenu)}
                        className="p-2 rounded-md bg-gray-50 text-gray-600 hover:bg-gray-100 transition-colors"
                      >
                        <Share2 className="h-4 w-4" />
                      </button>
                      
                      {showShareMenu && (
                        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10">
                          <div className="py-1">
                            <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                              Share on Twitter
                            </button>
                            <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                              Share on LinkedIn
                            </button>
                            <button className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                              Copy Link
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Featured Image */}
              <div className="mb-8">
                <img 
                  src={article.featuredImage} 
                  alt={article.title}
                  className="w-full h-96 object-cover rounded-lg"
                />
              </div>

              {/* Article Content */}
              <div 
                className="prose prose-lg max-w-none mb-8"
                dangerouslySetInnerHTML={{ __html: article.content }}
              />

              {/* Tags */}
              <div className="mb-8">
                <div className="flex items-center space-x-2 mb-4">
                  <Tag className="h-4 w-4 text-gray-500" />
                  <span className="text-sm font-medium text-gray-700">Tags:</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {article.tags.map((tag, index) => (
                    <span 
                      key={index}
                      className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm hover:bg-gray-200 cursor-pointer transition-colors"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Comments Section */}
              <div className="border-t border-gray-200 pt-8">
                <div className="flex items-center space-x-2 mb-6">
                  <MessageCircle className="h-5 w-5 text-gray-500" />
                  <h3 className="text-lg font-semibold text-gray-900">
                    Comments ({article.comments})
                  </h3>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-6 text-center">
                  <p className="text-gray-600 mb-4">Join the conversation</p>
                  <Button className="bg-red-600 hover:bg-red-700">
                    Sign in to Comment
                  </Button>
                </div>
              </div>
            </article>

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

              {/* Premium Membership */}
              <PremiumMembership />

              {/* Related Articles */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Related Articles</h3>
                <div className="space-y-4">
                  <div className="flex space-x-3">
                    <img 
                      src="https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=80&h=80&fit=crop" 
                      alt="Related" 
                      className="w-16 h-16 object-cover rounded-md flex-shrink-0"
                    />
                    <div>
                      <h4 className="font-medium text-gray-900 text-sm leading-tight hover:text-red-600 cursor-pointer">
                        Design Renaissance in Post-Pandemic Cities
                      </h4>
                      <p className="text-xs text-gray-500 mt-1">Design • 5 min read</p>
                    </div>
                  </div>
                  
                  <div className="flex space-x-3">
                    <img 
                      src="https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=80&h=80&fit=crop" 
                      alt="Related" 
                      className="w-16 h-16 object-cover rounded-md flex-shrink-0"
                    />
                    <div>
                      <h4 className="font-medium text-gray-900 text-sm leading-tight hover:text-red-600 cursor-pointer">
                        Sustainable Finance: Beyond ESG
                      </h4>
                      <p className="text-xs text-gray-500 mt-1">Business • 7 min read</p>
                    </div>
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

