import React, { useState, useRef, useEffect } from 'react';
import { 
  Bold, Italic, Underline, Strikethrough, AlignLeft, AlignCenter, AlignRight, 
  List, ListOrdered, Quote, Link, Image, Video, Code, Undo, Redo, 
  Type, Palette, Eye, Save, Upload, FileText, Maximize2, Minimize2
} from 'lucide-react';

const WYSIWYGEditor = ({ initialContent = '', onSave, onContentChange }) => {
  const [content, setContent] = useState(initialContent);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [wordCount, setWordCount] = useState(0);
  const [selectedText, setSelectedText] = useState('');
  const editorRef = useRef(null);
  const fileInputRef = useRef(null);

  // Initialize editor
  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.innerHTML = content;
      updateWordCount();
    }
  }, []);

  // Update word count
  const updateWordCount = () => {
    if (editorRef.current) {
      const text = editorRef.current.innerText || '';
      const words = text.trim().split(/\s+/).filter(word => word.length > 0);
      setWordCount(words.length);
    }
  };

  // Handle content change
  const handleContentChange = () => {
    if (editorRef.current) {
      const newContent = editorRef.current.innerHTML;
      setContent(newContent);
      updateWordCount();
      
      if (onContentChange) {
        onContentChange(newContent);
      }
    }
  };

  // Execute command
  const execCommand = (command, value = null) => {
    document.execCommand(command, false, value);
    editorRef.current.focus();
    handleContentChange();
  };

  // Insert HTML at cursor
  const insertHTML = (html) => {
    const selection = window.getSelection();
    if (selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      range.deleteContents();
      
      const div = document.createElement('div');
      div.innerHTML = html;
      
      while (div.firstChild) {
        range.insertNode(div.firstChild);
      }
      
      range.collapse(false);
      selection.removeAllRanges();
      selection.addRange(range);
    }
    
    handleContentChange();
  };

  // Handle image upload
  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const imageHTML = `<img src="${e.target.result}" alt="Uploaded image" style="max-width: 100%; height: auto; margin: 10px 0;" />`;
        insertHTML(imageHTML);
      };
      reader.readAsDataURL(file);
    }
  };

  // Insert link
  const insertLink = () => {
    const url = prompt('Enter URL:');
    if (url) {
      const selection = window.getSelection();
      const text = selection.toString() || url;
      const linkHTML = `<a href="${url}" target="_blank" rel="noopener noreferrer">${text}</a>`;
      
      if (selection.toString()) {
        execCommand('createLink', url);
      } else {
        insertHTML(linkHTML);
      }
    }
  };

  // Insert video embed
  const insertVideo = () => {
    const url = prompt('Enter video URL (YouTube, Vimeo, etc.):');
    if (url) {
      let embedHTML = '';
      
      // YouTube
      if (url.includes('youtube.com') || url.includes('youtu.be')) {
        const videoId = url.includes('youtu.be') 
          ? url.split('/').pop().split('?')[0]
          : url.split('v=')[1]?.split('&')[0];
        
        if (videoId) {
          embedHTML = `
            <div style="position: relative; padding-bottom: 56.25%; height: 0; margin: 20px 0;">
              <iframe 
                src="https://www.youtube.com/embed/${videoId}" 
                style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
                frameborder="0" 
                allowfullscreen>
              </iframe>
            </div>
          `;
        }
      }
      // Vimeo
      else if (url.includes('vimeo.com')) {
        const videoId = url.split('/').pop().split('?')[0];
        embedHTML = `
          <div style="position: relative; padding-bottom: 56.25%; height: 0; margin: 20px 0;">
            <iframe 
              src="https://player.vimeo.com/video/${videoId}" 
              style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
              frameborder="0" 
              allowfullscreen>
            </iframe>
          </div>
        `;
      }
      // Generic video link
      else {
        embedHTML = `<a href="${url}" target="_blank" rel="noopener noreferrer">🎥 ${url}</a>`;
      }
      
      if (embedHTML) {
        insertHTML(embedHTML);
      }
    }
  };

  // Insert code block
  const insertCodeBlock = () => {
    const code = prompt('Enter code:');
    if (code) {
      const codeHTML = `<pre style="background: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; margin: 15px 0;"><code>${code}</code></pre>`;
      insertHTML(codeHTML);
    }
  };

  // Format text color
  const formatTextColor = () => {
    const color = prompt('Enter color (hex, rgb, or name):');
    if (color) {
      execCommand('foreColor', color);
    }
  };

  // Format background color
  const formatBackgroundColor = () => {
    const color = prompt('Enter background color (hex, rgb, or name):');
    if (color) {
      execCommand('hiliteColor', color);
    }
  };

  // Save content
  const handleSave = () => {
    if (onSave) {
      onSave(content);
    }
  };

  // Toolbar button component
  const ToolbarButton = ({ onClick, icon: Icon, title, active = false }) => (
    <button
      type="button"
      onClick={onClick}
      title={title}
      className={`p-2 rounded hover:bg-gray-100 transition-colors ${
        active ? 'bg-blue-100 text-blue-600' : 'text-gray-600'
      }`}
    >
      <Icon className="w-4 h-4" />
    </button>
  );

  return (
    <div className={`wysiwyg-editor ${isFullscreen ? 'fixed inset-0 z-50 bg-white' : 'relative'}`}>
      {/* Toolbar */}
      <div className="toolbar border-b border-gray-200 p-3 bg-gray-50">
        <div className="flex flex-wrap items-center gap-1">
          {/* Text Formatting */}
          <div className="flex items-center border-r border-gray-300 pr-2 mr-2">
            <ToolbarButton
              onClick={() => execCommand('bold')}
              icon={Bold}
              title="Bold (Ctrl+B)"
            />
            <ToolbarButton
              onClick={() => execCommand('italic')}
              icon={Italic}
              title="Italic (Ctrl+I)"
            />
            <ToolbarButton
              onClick={() => execCommand('underline')}
              icon={Underline}
              title="Underline (Ctrl+U)"
            />
            <ToolbarButton
              onClick={() => execCommand('strikeThrough')}
              icon={Strikethrough}
              title="Strikethrough"
            />
          </div>

          {/* Alignment */}
          <div className="flex items-center border-r border-gray-300 pr-2 mr-2">
            <ToolbarButton
              onClick={() => execCommand('justifyLeft')}
              icon={AlignLeft}
              title="Align Left"
            />
            <ToolbarButton
              onClick={() => execCommand('justifyCenter')}
              icon={AlignCenter}
              title="Align Center"
            />
            <ToolbarButton
              onClick={() => execCommand('justifyRight')}
              icon={AlignRight}
              title="Align Right"
            />
          </div>

          {/* Lists */}
          <div className="flex items-center border-r border-gray-300 pr-2 mr-2">
            <ToolbarButton
              onClick={() => execCommand('insertUnorderedList')}
              icon={List}
              title="Bullet List"
            />
            <ToolbarButton
              onClick={() => execCommand('insertOrderedList')}
              icon={ListOrdered}
              title="Numbered List"
            />
            <ToolbarButton
              onClick={() => execCommand('formatBlock', 'blockquote')}
              icon={Quote}
              title="Quote"
            />
          </div>

          {/* Media & Links */}
          <div className="flex items-center border-r border-gray-300 pr-2 mr-2">
            <ToolbarButton
              onClick={insertLink}
              icon={Link}
              title="Insert Link"
            />
            <ToolbarButton
              onClick={() => fileInputRef.current?.click()}
              icon={Image}
              title="Insert Image"
            />
            <ToolbarButton
              onClick={insertVideo}
              icon={Video}
              title="Insert Video"
            />
            <ToolbarButton
              onClick={insertCodeBlock}
              icon={Code}
              title="Insert Code"
            />
          </div>

          {/* Formatting */}
          <div className="flex items-center border-r border-gray-300 pr-2 mr-2">
            <select
              onChange={(e) => execCommand('formatBlock', e.target.value)}
              className="text-sm border border-gray-300 rounded px-2 py-1"
              defaultValue=""
            >
              <option value="">Format</option>
              <option value="h1">Heading 1</option>
              <option value="h2">Heading 2</option>
              <option value="h3">Heading 3</option>
              <option value="h4">Heading 4</option>
              <option value="p">Paragraph</option>
              <option value="pre">Preformatted</option>
            </select>
            
            <ToolbarButton
              onClick={formatTextColor}
              icon={Type}
              title="Text Color"
            />
            <ToolbarButton
              onClick={formatBackgroundColor}
              icon={Palette}
              title="Background Color"
            />
          </div>

          {/* Actions */}
          <div className="flex items-center border-r border-gray-300 pr-2 mr-2">
            <ToolbarButton
              onClick={() => execCommand('undo')}
              icon={Undo}
              title="Undo (Ctrl+Z)"
            />
            <ToolbarButton
              onClick={() => execCommand('redo')}
              icon={Redo}
              title="Redo (Ctrl+Y)"
            />
          </div>

          {/* View Options */}
          <div className="flex items-center">
            <ToolbarButton
              onClick={() => setShowPreview(!showPreview)}
              icon={Eye}
              title="Toggle Preview"
              active={showPreview}
            />
            <ToolbarButton
              onClick={() => setIsFullscreen(!isFullscreen)}
              icon={isFullscreen ? Minimize2 : Maximize2}
              title="Toggle Fullscreen"
            />
            <ToolbarButton
              onClick={handleSave}
              icon={Save}
              title="Save Content"
            />
          </div>
        </div>

        {/* Status Bar */}
        <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-200 text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>{wordCount} words</span>
            <span>{content.length} characters</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4" />
            <span>Auto-save enabled</span>
          </div>
        </div>
      </div>

      {/* Editor Content */}
      <div className="editor-content flex" style={{ height: isFullscreen ? 'calc(100vh - 120px)' : '500px' }}>
        {/* Editor */}
        <div className={`editor-pane ${showPreview ? 'w-1/2 border-r border-gray-200' : 'w-full'}`}>
          <div
            ref={editorRef}
            contentEditable
            onInput={handleContentChange}
            onKeyUp={handleContentChange}
            className="editor-area h-full p-4 focus:outline-none overflow-y-auto"
            style={{
              minHeight: '100%',
              lineHeight: '1.6',
              fontSize: '16px'
            }}
            suppressContentEditableWarning={true}
          />
        </div>

        {/* Preview */}
        {showPreview && (
          <div className="preview-pane w-1/2 bg-gray-50">
            <div className="preview-header p-3 border-b border-gray-200 bg-white">
              <h3 className="font-medium text-gray-900">Preview</h3>
            </div>
            <div 
              className="preview-content p-4 h-full overflow-y-auto"
              dangerouslySetInnerHTML={{ __html: content }}
              style={{
                lineHeight: '1.6',
                fontSize: '16px'
              }}
            />
          </div>
        )}
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleImageUpload}
        className="hidden"
      />

      {/* Keyboard shortcuts help */}
      <div className="shortcuts-help text-xs text-gray-500 p-2 border-t border-gray-200 bg-gray-50">
        <strong>Shortcuts:</strong> Ctrl+B (Bold), Ctrl+I (Italic), Ctrl+U (Underline), Ctrl+Z (Undo), Ctrl+Y (Redo), Ctrl+S (Save)
      </div>
    </div>
  );
};

export default WYSIWYGEditor;

