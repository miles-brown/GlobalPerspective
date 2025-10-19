import { useState, useEffect } from 'react'
import { 
  Save, 
  Upload, 
  Image, 
  Video, 
  Map, 
  Link, 
  Bold, 
  Italic, 
  List, 
  Quote,
  Eye,
  X,
  Plus
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'

const API_BASE = 'http://localhost:5000/api'

function RichTextEditor({ content, onChange }) {
  const [editorContent, setEditorContent] = useState(content || '')

  const handleContentChange = (e) => {
    const newContent = e.target.value
    setEditorContent(newContent)
    onChange(newContent)
  }

  const insertAtCursor = (text) => {
    const textarea = document.getElementById('content-editor')
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const newContent = editorContent.substring(0, start) + text + editorContent.substring(end)
    setEditorContent(newContent)
    onChange(newContent)
    
    // Reset cursor position
    setTimeout(() => {
      textarea.focus()
      textarea.setSelectionRange(start + text.length, start + text.length)
    }, 0)
  }

  const formatText = (format) => {
    const textarea = document.getElementById('content-editor')
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = editorContent.substring(start, end)
    
    let formattedText = ''
    switch (format) {
      case 'bold':
        formattedText = `**${selectedText}**`
        break
      case 'italic':
        formattedText = `*${selectedText}*`
        break
      case 'quote':
        formattedText = `> ${selectedText}`
        break
      case 'list':
        formattedText = `- ${selectedText}`
        break
      default:
        formattedText = selectedText
    }
    
    const newContent = editorContent.substring(0, start) + formattedText + editorContent.substring(end)
    setEditorContent(newContent)
    onChange(newContent)
  }

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      {/* Toolbar */}
      <div className="bg-gray-50 border-b border-gray-200 p-3 flex items-center space-x-2">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => formatText('bold')}
          className="p-2"
        >
          <Bold className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => formatText('italic')}
          className="p-2"
        >
          <Italic className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => formatText('quote')}
          className="p-2"
        >
          <Quote className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => formatText('list')}
          className="p-2"
        >
          <List className="h-4 w-4" />
        </Button>
        <div className="w-px h-6 bg-gray-300 mx-2" />
        <Button
          variant="ghost"
          size="sm"
          onClick={() => insertAtCursor('![Image description](image-url)')}
          className="p-2"
        >
          <Image className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => insertAtCursor('[Video: Video title](video-url)')}
          className="p-2"
        >
          <Video className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => insertAtCursor('[Map: Location](map-embed-url)')}
          className="p-2"
        >
          <Map className="h-4 w-4" />
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => insertAtCursor('[Link text](url)')}
          className="p-2"
        >
          <Link className="h-4 w-4" />
        </Button>
      </div>
      
      {/* Editor */}
      <textarea
        id="content-editor"
        value={editorContent}
        onChange={handleContentChange}
        className="w-full h-96 p-4 resize-none focus:outline-none font-mono text-sm"
        placeholder="Write your article content here... Use Markdown syntax for formatting."
      />
    </div>
  )
}

function MediaUploader({ onMediaAdd }) {
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)

  const handleFileUpload = async (files) => {
    setUploading(true)
    
    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)
      
      try {
        const response = await fetch(`${API_BASE}/media/upload`, {
          method: 'POST',
          body: formData
        })
        
        if (response.ok) {
          const result = await response.json()
          onMediaAdd({
            type: file.type.startsWith('image/') ? 'image' : 'video',
            url: result.url,
            filename: file.name
          })
        }
      } catch (error) {
        console.error('Upload failed:', error)
      }
    }
    
    setUploading(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const files = Array.from(e.dataTransfer.files)
    handleFileUpload(files)
  }

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files)
    handleFileUpload(files)
  }

  return (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
        dragOver ? 'border-red-400 bg-red-50' : 'border-gray-300'
      }`}
      onDragOver={(e) => {
        e.preventDefault()
        setDragOver(true)
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
    >
      <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <p className="text-gray-600 mb-4">
        Drag and drop images or videos here, or click to select files
      </p>
      <input
        type="file"
        multiple
        accept="image/*,video/*"
        onChange={handleFileSelect}
        className="hidden"
        id="file-upload"
      />
      <Button
        variant="outline"
        onClick={() => document.getElementById('file-upload').click()}
        disabled={uploading}
      >
        {uploading ? 'Uploading...' : 'Select Files'}
      </Button>
    </div>
  )
}

function ArticlePreview({ article, onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold">Article Preview</h3>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        <div className="p-6">
          {article.featuredImage && (
            <img
              src={article.featuredImage}
              alt={article.title}
              className="w-full h-64 object-cover rounded-lg mb-6"
            />
          )}
          
          <div className="mb-4">
            <span className="text-red-600 text-xs font-semibold uppercase tracking-wide">
              {article.category}
            </span>
          </div>
          
          <h1 className="font-serif text-3xl lg:text-4xl font-semibold leading-tight mb-3">
            {article.title}
          </h1>
          
          {article.subtitle && (
            <h2 className="text-lg text-gray-600 mb-6 font-medium">
              {article.subtitle}
            </h2>
          )}
          
          <div className="prose max-w-none">
            {article.content.split('\n').map((paragraph, index) => (
              <p key={index} className="mb-4 text-base leading-relaxed">
                {paragraph}
              </p>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function CMS() {
  const [article, setArticle] = useState({
    title: '',
    subtitle: '',
    content: '',
    excerpt: '',
    category: 'World Affairs',
    featuredImage: '',
    isBreaking: false,
    isFeatured: false
  })
  
  const [categories, setCategories] = useState([])
  const [mediaItems, setMediaItems] = useState([])
  const [showPreview, setShowPreview] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchCategories()
  }, [])

  const fetchCategories = async () => {
    try {
      const response = await fetch(`${API_BASE}/categories`)
      if (response.ok) {
        const data = await response.json()
        setCategories(data)
      }
    } catch (error) {
      console.error('Failed to fetch categories:', error)
      // Fallback categories
      setCategories([
        { id: 1, name: 'World Affairs' },
        { id: 2, name: 'Business' },
        { id: 3, name: 'Culture' },
        { id: 4, name: 'Design' },
        { id: 5, name: 'Technology' }
      ])
    }
  }

  const handleInputChange = (field, value) => {
    setArticle(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleMediaAdd = (media) => {
    setMediaItems(prev => [...prev, media])
    // Auto-insert image into content if it's an image
    if (media.type === 'image') {
      const imageMarkdown = `![${media.filename}](${media.url})\n\n`
      handleInputChange('content', article.content + imageMarkdown)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    
    try {
      const response = await fetch(`${API_BASE}/articles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...article,
          author_id: 1 // Default admin user
        })
      })
      
      if (response.ok) {
        alert('Article saved successfully!')
        // Reset form
        setArticle({
          title: '',
          subtitle: '',
          content: '',
          excerpt: '',
          category: 'World Affairs',
          featuredImage: '',
          isBreaking: false,
          isFeatured: false
        })
        setMediaItems([])
      } else {
        alert('Failed to save article')
      }
    } catch (error) {
      console.error('Save failed:', error)
      alert('Failed to save article')
    }
    
    setSaving(false)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Content Management System</h1>
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                onClick={() => setShowPreview(true)}
                disabled={!article.title}
              >
                <Eye className="h-4 w-4 mr-2" />
                Preview
              </Button>
              <Button
                onClick={handleSave}
                disabled={saving || !article.title || !article.content}
              >
                <Save className="h-4 w-4 mr-2" />
                {saving ? 'Saving...' : 'Save Article'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Article Details */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold mb-4">Article Details</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Title *
                  </label>
                  <input
                    type="text"
                    value={article.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Enter article title"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Subtitle
                  </label>
                  <input
                    type="text"
                    value={article.subtitle}
                    onChange={(e) => handleInputChange('subtitle', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Enter article subtitle"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Excerpt
                  </label>
                  <textarea
                    value={article.excerpt}
                    onChange={(e) => handleInputChange('excerpt', e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                    placeholder="Brief description of the article"
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category
                    </label>
                    <select
                      value={article.category}
                      onChange={(e) => handleInputChange('category', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                    >
                      {categories.map(category => (
                        <option key={category.id || category.name} value={category.name}>
                          {category.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Featured Image URL
                    </label>
                    <input
                      type="url"
                      value={article.featuredImage}
                      onChange={(e) => handleInputChange('featuredImage', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                      placeholder="https://example.com/image.jpg"
                    />
                  </div>
                </div>
                
                <div className="flex items-center space-x-6">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={article.isBreaking}
                      onChange={(e) => handleInputChange('isBreaking', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm font-medium text-gray-700">Breaking News</span>
                  </label>
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={article.isFeatured}
                      onChange={(e) => handleInputChange('isFeatured', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm font-medium text-gray-700">Featured Article</span>
                  </label>
                </div>
              </div>
            </div>

            {/* Content Editor */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold mb-4">Article Content</h2>
              <RichTextEditor
                content={article.content}
                onChange={(content) => handleInputChange('content', content)}
              />
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Media Upload */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold mb-4">Media Upload</h2>
              <MediaUploader onMediaAdd={handleMediaAdd} />
              
              {mediaItems.length > 0 && (
                <div className="mt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Uploaded Media</h3>
                  <div className="space-y-2">
                    {mediaItems.map((media, index) => (
                      <div key={index} className="flex items-center space-x-2 text-sm">
                        {media.type === 'image' ? (
                          <Image className="h-4 w-4 text-green-600" />
                        ) : (
                          <Video className="h-4 w-4 text-blue-600" />
                        )}
                        <span className="truncate">{media.filename}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Rich Content Plugins */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold mb-4">Rich Content</h2>
              <div className="space-y-3">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => {
                    const embedCode = prompt('Enter Google Maps embed URL:')
                    if (embedCode) {
                      handleInputChange('content', article.content + `\n\n[Map Embed](${embedCode})\n\n`)
                    }
                  }}
                >
                  <Map className="h-4 w-4 mr-2" />
                  Add Map
                </Button>
                
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => {
                    const videoUrl = prompt('Enter video URL (YouTube, Vimeo, etc.):')
                    if (videoUrl) {
                      handleInputChange('content', article.content + `\n\n[Video](${videoUrl})\n\n`)
                    }
                  }}
                >
                  <Video className="h-4 w-4 mr-2" />
                  Embed Video
                </Button>
                
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => {
                    const chartData = prompt('Enter chart data or embed code:')
                    if (chartData) {
                      handleInputChange('content', article.content + `\n\n[Chart/Infographic](${chartData})\n\n`)
                    }
                  }}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Chart
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && (
        <ArticlePreview
          article={article}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  )
}

