import React, { useState, useEffect } from 'react';
import { MessageCircle, Reply, ThumbsUp, Flag, MoreHorizontal, User, Clock, ChevronDown, ChevronUp } from 'lucide-react';

const EnhancedCommentSystem = ({ articleId, currentUser }) => {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [replyingTo, setReplyingTo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sortBy, setSortBy] = useState('newest');
  const [expandedComments, setExpandedComments] = useState(new Set());

  // Fetch comments
  useEffect(() => {
    fetchComments();
  }, [articleId, sortBy]);

  const fetchComments = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/articles/${articleId}/comments?sort=${sortBy}`);
      const data = await response.json();
      if (data.success) {
        setComments(buildCommentTree(data.data.comments));
      }
    } catch (error) {
      console.error('Error fetching comments:', error);
    } finally {
      setLoading(false);
    }
  };

  // Build threaded comment structure
  const buildCommentTree = (flatComments) => {
    const commentMap = {};
    const rootComments = [];

    // Create comment map
    flatComments.forEach(comment => {
      commentMap[comment.id] = { ...comment, replies: [] };
    });

    // Build tree structure
    flatComments.forEach(comment => {
      if (comment.parent_id) {
        if (commentMap[comment.parent_id]) {
          commentMap[comment.parent_id].replies.push(commentMap[comment.id]);
        }
      } else {
        rootComments.push(commentMap[comment.id]);
      }
    });

    return rootComments;
  };

  // Submit comment
  const submitComment = async (content, parentId = null) => {
    if (!content.trim()) return;

    try {
      const response = await fetch(`/api/articles/${articleId}/comments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          content: content.trim(),
          parent_id: parentId
        })
      });

      const data = await response.json();
      if (data.success) {
        setNewComment('');
        setReplyingTo(null);
        fetchComments(); // Refresh comments
      }
    } catch (error) {
      console.error('Error submitting comment:', error);
    }
  };

  // Like comment
  const likeComment = async (commentId) => {
    try {
      const response = await fetch(`/api/comments/${commentId}/like`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        fetchComments(); // Refresh to show updated like count
      }
    } catch (error) {
      console.error('Error liking comment:', error);
    }
  };

  // Report comment
  const reportComment = async (commentId, reason) => {
    try {
      const response = await fetch(`/api/comments/${commentId}/report`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ reason })
      });

      if (response.ok) {
        alert('Comment reported successfully');
      }
    } catch (error) {
      console.error('Error reporting comment:', error);
    }
  };

  // Toggle comment expansion
  const toggleExpanded = (commentId) => {
    const newExpanded = new Set(expandedComments);
    if (newExpanded.has(commentId)) {
      newExpanded.delete(commentId);
    } else {
      newExpanded.add(commentId);
    }
    setExpandedComments(newExpanded);
  };

  // Format time ago
  const timeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    return date.toLocaleDateString();
  };

  // Comment component
  const CommentItem = ({ comment, depth = 0 }) => {
    const [showReplyForm, setShowReplyForm] = useState(false);
    const [replyContent, setReplyContent] = useState('');
    const isExpanded = expandedComments.has(comment.id);
    const hasReplies = comment.replies && comment.replies.length > 0;

    return (
      <div className={`comment-item ${depth > 0 ? 'ml-4 md:ml-8 border-l-2 border-gray-200 pl-4' : ''}`}>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4">
          {/* Comment Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div>
                <div className="font-medium text-gray-900">
                  {comment.author_name || comment.user?.username || 'Anonymous'}
                </div>
                <div className="flex items-center text-sm text-gray-500 space-x-2">
                  <Clock className="w-3 h-3" />
                  <span>{timeAgo(comment.created_at)}</span>
                  {comment.status === 'pending' && (
                    <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs">
                      Pending Approval
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            {/* Comment Actions */}
            <div className="flex items-center space-x-2">
              <button
                onClick={() => likeComment(comment.id)}
                className="flex items-center space-x-1 text-gray-500 hover:text-blue-600 transition-colors"
              >
                <ThumbsUp className="w-4 h-4" />
                <span className="text-sm">{comment.like_count || 0}</span>
              </button>
              
              <button
                onClick={() => setShowReplyForm(!showReplyForm)}
                className="flex items-center space-x-1 text-gray-500 hover:text-blue-600 transition-colors"
              >
                <Reply className="w-4 h-4" />
                <span className="text-sm hidden sm:inline">Reply</span>
              </button>
              
              <button
                onClick={() => reportComment(comment.id, 'inappropriate')}
                className="text-gray-500 hover:text-red-600 transition-colors"
              >
                <Flag className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Comment Content */}
          <div className="text-gray-800 leading-relaxed mb-3">
            {comment.content}
          </div>

          {/* Reply Form */}
          {showReplyForm && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <textarea
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                placeholder="Write a reply..."
                className="w-full p-3 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="3"
              />
              <div className="flex justify-end space-x-2 mt-3">
                <button
                  onClick={() => {
                    setShowReplyForm(false);
                    setReplyContent('');
                  }}
                  className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    submitComment(replyContent, comment.id);
                    setShowReplyForm(false);
                    setReplyContent('');
                  }}
                  disabled={!replyContent.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Reply
                </button>
              </div>
            </div>
          )}

          {/* Replies Toggle */}
          {hasReplies && (
            <button
              onClick={() => toggleExpanded(comment.id)}
              className="flex items-center space-x-2 text-blue-600 hover:text-blue-800 transition-colors mt-3"
            >
              {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              <span className="text-sm">
                {isExpanded ? 'Hide' : 'Show'} {comment.replies.length} {comment.replies.length === 1 ? 'reply' : 'replies'}
              </span>
            </button>
          )}
        </div>

        {/* Nested Replies */}
        {hasReplies && isExpanded && (
          <div className="replies">
            {comment.replies.map(reply => (
              <CommentItem key={reply.id} comment={reply} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="comments-section max-w-4xl mx-auto px-4 py-8">
      {/* Comments Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <h3 className="text-2xl font-bold text-gray-900 mb-4 sm:mb-0">
          <MessageCircle className="inline w-6 h-6 mr-2" />
          Comments ({comments.length})
        </h3>
        
        {/* Sort Options */}
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-600">Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="newest">Newest</option>
            <option value="oldest">Oldest</option>
            <option value="most_liked">Most Liked</option>
          </select>
        </div>
      </div>

      {/* New Comment Form */}
      {currentUser ? (
        <div className="new-comment-form bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex items-start space-x-4">
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
              <User className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Share your thoughts..."
                className="w-full p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="4"
              />
              <div className="flex justify-between items-center mt-4">
                <div className="text-sm text-gray-500">
                  {newComment.length}/1000 characters
                </div>
                <button
                  onClick={() => submitComment(newComment)}
                  disabled={!newComment.trim() || loading}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Posting...' : 'Post Comment'}
                </button>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="login-prompt bg-gray-50 rounded-lg p-6 mb-8 text-center">
          <p className="text-gray-600 mb-4">Join the conversation! Sign in to leave a comment.</p>
          <button className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Sign In
          </button>
        </div>
      )}

      {/* Comments List */}
      {loading ? (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-gray-600 mt-2">Loading comments...</p>
        </div>
      ) : comments.length > 0 ? (
        <div className="comments-list">
          {comments.map(comment => (
            <CommentItem key={comment.id} comment={comment} />
          ))}
        </div>
      ) : (
        <div className="no-comments text-center py-12">
          <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h4 className="text-xl font-medium text-gray-600 mb-2">No comments yet</h4>
          <p className="text-gray-500">Be the first to share your thoughts on this article.</p>
        </div>
      )}

      {/* Load More Button */}
      {comments.length > 0 && (
        <div className="text-center mt-8">
          <button className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors">
            Load More Comments
          </button>
        </div>
      )}
    </div>
  );
};

export default EnhancedCommentSystem;

