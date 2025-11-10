import React, { useState, useEffect, useRef } from 'react';
import { Search, Filter, Calendar, Tag, User, Globe, X, ChevronDown, SlidersHorizontal } from 'lucide-react';

const AdvancedSearchSystem = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const searchInputRef = useRef(null);

  // Filter states
  const [filters, setFilters] = useState({
    category: '',
    author: '',
    dateRange: '',
    tags: [],
    language: '',
    sortBy: 'relevance'
  });

  // Categories and other filter options
  const categories = [
    { id: 1, name: 'World Affairs', slug: 'world-affairs' },
    { id: 2, name: 'Business', slug: 'business' },
    { id: 3, name: 'Technology', slug: 'technology' },
    { id: 4, name: 'Culture', slug: 'culture' },
    { id: 5, name: 'Politics', slug: 'politics' }
  ];

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ar', name: 'Arabic' }
  ];

  const sortOptions = [
    { value: 'relevance', label: 'Most Relevant' },
    { value: 'newest', label: 'Newest First' },
    { value: 'oldest', label: 'Oldest First' },
    { value: 'most_viewed', label: 'Most Viewed' },
    { value: 'most_commented', label: 'Most Discussed' }
  ];

  // Search function
  const performSearch = async (query = searchQuery, currentFilters = filters) => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const params = new URLSearchParams({
        q: query,
        ...currentFilters,
        tags: currentFilters.tags.join(',')
      });

      const response = await fetch(`/api/search?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setSearchResults(data.data.results);
      }
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Get search suggestions
  const getSuggestions = async (query) => {
    if (query.length < 2) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      
      if (data.success) {
        setSuggestions(data.data.suggestions);
      }
    } catch (error) {
      console.error('Suggestions error:', error);
    }
  };

  // Handle search input change
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    getSuggestions(value);
    setShowSuggestions(true);
  };

  // Handle search submit
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setShowSuggestions(false);
    performSearch();
  };

  // Handle filter change
  const handleFilterChange = (filterName, value) => {
    const newFilters = { ...filters, [filterName]: value };
    setFilters(newFilters);
    
    if (searchQuery.trim()) {
      performSearch(searchQuery, newFilters);
    }
  };

  // Add tag filter
  const addTagFilter = (tag) => {
    if (!filters.tags.includes(tag)) {
      const newTags = [...filters.tags, tag];
      handleFilterChange('tags', newTags);
    }
  };

  // Remove tag filter
  const removeTagFilter = (tag) => {
    const newTags = filters.tags.filter(t => t !== tag);
    handleFilterChange('tags', newTags);
  };

  // Clear all filters
  const clearFilters = () => {
    const clearedFilters = {
      category: '',
      author: '',
      dateRange: '',
      tags: [],
      language: '',
      sortBy: 'relevance'
    };
    setFilters(clearedFilters);
    
    if (searchQuery.trim()) {
      performSearch(searchQuery, clearedFilters);
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  // Highlight search terms in text
  const highlightText = (text, query) => {
    if (!query.trim()) return text;
    
    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark class="bg-yellow-200">$1</mark>');
  };

  return (
    <div className="search-system max-w-6xl mx-auto px-4 py-6">
      {/* Search Header */}
      <div className="search-header mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Search GlobalPerspective</h1>
        <p className="text-gray-600">Discover articles, insights, and perspectives from around the world</p>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearchSubmit} className="search-form mb-6">
        <div className="relative">
          <div className="flex">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                ref={searchInputRef}
                type="text"
                value={searchQuery}
                onChange={handleSearchChange}
                onFocus={() => setShowSuggestions(true)}
                placeholder="Search articles, topics, authors..."
                className="w-full pl-12 pr-4 py-4 text-lg border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              
              {/* Search Suggestions */}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 bg-white border border-gray-200 rounded-lg shadow-lg z-10 mt-1">
                  {suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => {
                        setSearchQuery(suggestion);
                        setShowSuggestions(false);
                        performSearch(suggestion);
                      }}
                      className="w-full text-left px-4 py-3 hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                    >
                      <Search className="inline w-4 h-4 text-gray-400 mr-3" />
                      {suggestion}
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-4 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>
      </form>

      {/* Filter Toggle (Mobile) */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="lg:hidden flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          <SlidersHorizontal className="w-4 h-4" />
          <span>Filters</span>
          <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
        </button>
        
        {/* Active Filters Count */}
        {Object.values(filters).some(v => v && (Array.isArray(v) ? v.length > 0 : true)) && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">
              {Object.values(filters).filter(v => v && (Array.isArray(v) ? v.length > 0 : true)).length} filters active
            </span>
            <button
              onClick={clearFilters}
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Clear all
            </button>
          </div>
        )}
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Filters Sidebar */}
        <div className={`lg:w-80 ${showFilters ? 'block' : 'hidden lg:block'}`}>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 sticky top-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Filter className="w-5 h-5 mr-2" />
              Filters
            </h3>

            {/* Category Filter */}
            <div className="filter-group mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category.id} value={category.slug}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Date Range Filter */}
            <div className="filter-group mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Calendar className="inline w-4 h-4 mr-1" />
                Date Range
              </label>
              <select
                value={filters.dateRange}
                onChange={(e) => handleFilterChange('dateRange', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Any Time</option>
                <option value="today">Today</option>
                <option value="week">Past Week</option>
                <option value="month">Past Month</option>
                <option value="year">Past Year</option>
              </select>
            </div>

            {/* Language Filter */}
            <div className="filter-group mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Globe className="inline w-4 h-4 mr-1" />
                Language
              </label>
              <select
                value={filters.language}
                onChange={(e) => handleFilterChange('language', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Languages</option>
                {languages.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Tags Filter */}
            <div className="filter-group mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                <Tag className="inline w-4 h-4 mr-1" />
                Tags
              </label>
              {filters.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-3">
                  {filters.tags.map(tag => (
                    <span
                      key={tag}
                      className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                    >
                      {tag}
                      <button
                        onClick={() => removeTagFilter(tag)}
                        className="ml-2 text-blue-600 hover:text-blue-800"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
              <input
                type="text"
                placeholder="Add tag..."
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    const tag = e.target.value.trim();
                    if (tag) {
                      addTagFilter(tag);
                      e.target.value = '';
                    }
                  }
                }}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Sort By */}
            <div className="filter-group">
              <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select
                value={filters.sortBy}
                onChange={(e) => handleFilterChange('sortBy', e.target.value)}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {sortOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Search Results */}
        <div className="flex-1">
          {searchQuery && (
            <div className="results-header mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Search results for "{searchQuery}"
              </h2>
              {searchResults.length > 0 && (
                <p className="text-gray-600 mt-1">
                  Found {searchResults.length} articles
                </p>
              )}
            </div>
          )}

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-4">Searching...</p>
            </div>
          ) : searchResults.length > 0 ? (
            <div className="search-results space-y-6">
              {searchResults.map(article => (
                <div key={article.id} className="result-item bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                  <div className="flex flex-col md:flex-row gap-4">
                    {article.featured_image && (
                      <div className="md:w-48 flex-shrink-0">
                        <img
                          src={article.featured_image}
                          alt={article.title}
                          className="w-full h-32 md:h-24 object-cover rounded-lg"
                        />
                      </div>
                    )}
                    
                    <div className="flex-1">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition-colors">
                          <a href={`/articles/${article.slug}`}>
                            <span dangerouslySetInnerHTML={{ 
                              __html: highlightText(article.title, searchQuery) 
                            }} />
                          </a>
                        </h3>
                        
                        <span className="text-sm text-gray-500 ml-4 flex-shrink-0">
                          {formatDate(article.published_at)}
                        </span>
                      </div>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                        <span className="flex items-center">
                          <User className="w-4 h-4 mr-1" />
                          {article.author.name}
                        </span>
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                          {article.category.name}
                        </span>
                        <span>{article.view_count} views</span>
                        <span>{article.comment_count} comments</span>
                      </div>
                      
                      <p className="text-gray-700 leading-relaxed">
                        <span dangerouslySetInnerHTML={{ 
                          __html: highlightText(article.excerpt, searchQuery) 
                        }} />
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : searchQuery ? (
            <div className="no-results text-center py-12">
              <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-gray-600 mb-2">No results found</h3>
              <p className="text-gray-500 mb-4">
                Try adjusting your search terms or filters
              </p>
              <button
                onClick={clearFilters}
                className="px-4 py-2 text-blue-600 hover:text-blue-800 transition-colors"
              >
                Clear all filters
              </button>
            </div>
          ) : (
            <div className="search-placeholder text-center py-12">
              <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-medium text-gray-600 mb-2">Start your search</h3>
              <p className="text-gray-500">
                Enter keywords to find articles, topics, and insights
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdvancedSearchSystem;

