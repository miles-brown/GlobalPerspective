import { useState, useEffect } from 'react'
import { X, ExternalLink, Star, Crown, Mail, CreditCard } from 'lucide-react'

// Banner Ad Component - Elegant and non-intrusive
export function BannerAd({ position = 'top', size = 'leaderboard' }) {
  const [isVisible, setIsVisible] = useState(true)
  const [adData, setAdData] = useState(null)

  useEffect(() => {
    // Simulate ad loading
    setTimeout(() => {
      setAdData({
        title: "Sustainable Investment Solutions",
        description: "Discover ESG-focused portfolios with competitive returns",
        image: "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=400&h=200&fit=crop",
        sponsor: "GreenCapital Partners",
        url: "#"
      })
    }, 1000)
  }, [])

  if (!isVisible || !adData) return null

  const sizeClasses = {
    leaderboard: 'h-24 max-w-4xl',
    rectangle: 'h-64 w-80',
    skyscraper: 'h-96 w-40'
  }

  return (
    <div className={`relative bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border border-gray-200 overflow-hidden ${sizeClasses[size]} mx-auto my-6`}>
      <div className="absolute top-2 left-2 text-xs text-gray-500 font-medium">
        SPONSORED
      </div>
      <button
        onClick={() => setIsVisible(false)}
        className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 transition-colors"
      >
        <X className="h-4 w-4" />
      </button>
      
      <div className="flex items-center h-full p-4">
        <img 
          src={adData.image} 
          alt={adData.title}
          className="w-16 h-16 rounded-lg object-cover mr-4"
        />
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900 text-sm mb-1">{adData.title}</h3>
          <p className="text-gray-600 text-xs mb-2">{adData.description}</p>
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">{adData.sponsor}</span>
            <ExternalLink className="h-3 w-3 text-gray-400" />
          </div>
        </div>
      </div>
    </div>
  )
}

// Native Ad Component - Blends seamlessly with content
export function NativeAd({ articles }) {
  const sponsoredContent = {
    id: 'sponsored-1',
    title: "The Future of Renewable Energy Investment",
    subtitle: "Expert insights on emerging market opportunities",
    excerpt: "Leading analysts share their perspectives on the most promising renewable energy sectors for 2024 and beyond.",
    category: "Sponsored Content",
    author: "Investment Research Team",
    publishedAt: "2024-01-15",
    featuredImage: "https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=600&h=400&fit=crop",
    isSponsored: true,
    sponsor: "EcoInvest Global"
  }

  return (
    <article className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow">
      <div className="relative">
        <img 
          src={sponsoredContent.featuredImage} 
          alt={sponsoredContent.title}
          className="w-full h-48 object-cover"
        />
        <div className="absolute top-3 left-3 bg-blue-600 text-white px-2 py-1 rounded text-xs font-medium">
          SPONSORED
        </div>
      </div>
      
      <div className="p-6">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-medium text-blue-600">{sponsoredContent.category}</span>
          <span className="text-xs text-gray-500">by {sponsoredContent.sponsor}</span>
        </div>
        
        <h2 className="text-xl font-bold text-gray-900 mb-2 hover:text-blue-600 transition-colors cursor-pointer">
          {sponsoredContent.title}
        </h2>
        
        {sponsoredContent.subtitle && (
          <h3 className="text-lg text-gray-600 mb-3">{sponsoredContent.subtitle}</h3>
        )}
        
        <p className="text-gray-700 mb-4 leading-relaxed">{sponsoredContent.excerpt}</p>
        
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>{sponsoredContent.author}</span>
          <span>{sponsoredContent.publishedAt}</span>
        </div>
      </div>
    </article>
  )
}

// Premium Membership Component
export function PremiumMembership() {
  const [isVisible, setIsVisible] = useState(true)

  if (!isVisible) return null

  return (
    <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200 rounded-lg p-6 my-8">
      <button
        onClick={() => setIsVisible(false)}
        className="float-right text-amber-400 hover:text-amber-600"
      >
        <X className="h-4 w-4" />
      </button>
      
      <div className="flex items-start space-x-4">
        <div className="bg-amber-100 p-3 rounded-full">
          <Crown className="h-6 w-6 text-amber-600" />
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900 mb-2">
            Unlock Premium Content
          </h3>
          <p className="text-gray-700 mb-4">
            Get unlimited access to in-depth analysis, exclusive interviews, and ad-free reading experience.
          </p>
          
          <div className="flex items-center space-x-6 mb-4">
            <div className="flex items-center text-sm text-gray-600">
              <Star className="h-4 w-4 text-amber-500 mr-1" />
              Unlimited articles
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <Star className="h-4 w-4 text-amber-500 mr-1" />
              Exclusive content
            </div>
            <div className="flex items-center text-sm text-gray-600">
              <Star className="h-4 w-4 text-amber-500 mr-1" />
              Ad-free experience
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <button className="bg-amber-600 text-white px-6 py-2 rounded-md hover:bg-amber-700 transition-colors font-medium">
              Start Free Trial
            </button>
            <span className="text-sm text-gray-600">$9.99/month after trial</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Newsletter Subscription Component
export function NewsletterSubscription() {
  const [email, setEmail] = useState('')
  const [isSubscribed, setIsSubscribed] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (email) {
      setIsSubscribed(true)
      setEmail('')
    }
  }

  if (isSubscribed) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
        <div className="bg-green-100 w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3">
          <Mail className="h-6 w-6 text-green-600" />
        </div>
        <h3 className="text-lg font-semibold text-green-900 mb-2">Thank you for subscribing!</h3>
        <p className="text-green-700">You'll receive our daily briefing in your inbox.</p>
      </div>
    )
  }

  return (
    <div className="bg-gray-900 text-white rounded-lg p-6 my-8">
      <div className="text-center mb-6">
        <h3 className="text-xl font-bold mb-2">Stay Informed</h3>
        <p className="text-gray-300">
          Get our daily briefing with the most important global affairs stories delivered to your inbox.
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email address"
          className="flex-1 px-4 py-2 rounded-md text-gray-900 border border-gray-300 focus:outline-none focus:ring-2 focus:ring-red-500"
          required
        />
        <button
          type="submit"
          className="bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700 transition-colors font-medium"
        >
          Subscribe
        </button>
      </form>
      
      <p className="text-xs text-gray-400 mt-3 text-center">
        Free newsletter • No spam • Unsubscribe anytime
      </p>
    </div>
  )
}

// Sidebar Ad Component
export function SidebarAd() {
  const ads = [
    {
      title: "Global Economics Summit 2024",
      description: "Join world leaders in Davos",
      image: "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=300&h=200&fit=crop",
      sponsor: "World Economic Forum",
      cta: "Register Now"
    },
    {
      title: "Sustainable Tech Innovations",
      description: "Discover breakthrough technologies",
      image: "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=300&h=200&fit=crop",
      sponsor: "TechGreen Solutions",
      cta: "Learn More"
    }
  ]

  const [currentAd, setCurrentAd] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentAd((prev) => (prev + 1) % ads.length)
    }, 10000) // Rotate every 10 seconds

    return () => clearInterval(interval)
  }, [ads.length])

  const ad = ads[currentAd]

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div className="text-xs text-gray-500 font-medium p-2 bg-gray-50 border-b">
        ADVERTISEMENT
      </div>
      
      <div className="p-4">
        <img 
          src={ad.image} 
          alt={ad.title}
          className="w-full h-32 object-cover rounded-md mb-3"
        />
        
        <h4 className="font-semibold text-gray-900 text-sm mb-2">{ad.title}</h4>
        <p className="text-gray-600 text-xs mb-3">{ad.description}</p>
        
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">{ad.sponsor}</span>
          <button className="bg-blue-600 text-white px-3 py-1 rounded text-xs hover:bg-blue-700 transition-colors">
            {ad.cta}
          </button>
        </div>
      </div>
      
      {/* Ad rotation indicators */}
      <div className="flex justify-center space-x-1 p-2 bg-gray-50">
        {ads.map((_, index) => (
          <div
            key={index}
            className={`w-2 h-2 rounded-full transition-colors ${
              index === currentAd ? 'bg-blue-600' : 'bg-gray-300'
            }`}
          />
        ))}
      </div>
    </div>
  )
}

// Sponsored Content Marker
export function SponsoredMarker({ sponsor, className = "" }) {
  return (
    <div className={`inline-flex items-center space-x-2 ${className}`}>
      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium">
        SPONSORED
      </span>
      <span className="text-xs text-gray-500">by {sponsor}</span>
    </div>
  )
}

// Revenue Analytics Component (for admin use)
export function RevenueAnalytics() {
  const revenueData = {
    totalRevenue: 12450,
    adRevenue: 8200,
    subscriptionRevenue: 3800,
    sponsoredContentRevenue: 450,
    growth: 15.3
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Overview</h3>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">${revenueData.totalRevenue.toLocaleString()}</div>
          <div className="text-sm text-gray-500">Total Revenue</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">${revenueData.adRevenue.toLocaleString()}</div>
          <div className="text-sm text-gray-500">Ad Revenue</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">${revenueData.subscriptionRevenue.toLocaleString()}</div>
          <div className="text-sm text-gray-500">Subscriptions</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600">${revenueData.sponsoredContentRevenue.toLocaleString()}</div>
          <div className="text-sm text-gray-500">Sponsored</div>
        </div>
      </div>
      
      <div className="flex items-center justify-center text-sm">
        <span className="text-green-600 font-medium">↗ {revenueData.growth}%</span>
        <span className="text-gray-500 ml-1">vs last month</span>
      </div>
    </div>
  )
}

