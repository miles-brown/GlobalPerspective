import os
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from werkzeug.utils import secure_filename
from PIL import Image
from src.models.user import db
from src.models.article import MediaItem

media_bp = Blueprint('media', __name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'aac', 'm4a'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def allowed_file(filename, file_type=None):
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if file_type == 'image':
        return extension in ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'video':
        return extension in ALLOWED_VIDEO_EXTENSIONS
    elif file_type == 'audio':
        return extension in ALLOWED_AUDIO_EXTENSIONS
    elif file_type == 'document':
        return extension in ALLOWED_DOCUMENT_EXTENSIONS
    else:
        # Allow all supported types
        return extension in (ALLOWED_IMAGE_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS | 
                           ALLOWED_AUDIO_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS)

def get_file_type(filename):
    """Determine file type based on extension"""
    if '.' not in filename:
        return 'unknown'
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    if extension in ALLOWED_IMAGE_EXTENSIONS:
        return 'image'
    elif extension in ALLOWED_VIDEO_EXTENSIONS:
        return 'video'
    elif extension in ALLOWED_AUDIO_EXTENSIONS:
        return 'audio'
    elif extension in ALLOWED_DOCUMENT_EXTENSIONS:
        return 'document'
    else:
        return 'unknown'

def create_upload_folder():
    """Create upload folder if it doesn't exist"""
    upload_path = os.path.join(current_app.static_folder, UPLOAD_FOLDER)
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    return upload_path

def get_image_dimensions(file_path):
    """Get image dimensions"""
    try:
        with Image.open(file_path) as img:
            return img.size  # Returns (width, height)
    except Exception:
        return None, None

@media_bp.route('/media/upload', methods=['POST'])
def upload_file():
    """Upload a file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({'error': 'File too large'}), 400
    
    # Create upload folder
    upload_path = create_upload_folder()
    
    # Generate unique filename
    original_filename = secure_filename(file.filename)
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(upload_path, unique_filename)
    
    try:
        # Save file
        file.save(file_path)
        
        # Get file info
        file_type = get_file_type(original_filename)
        mime_type = file.mimetype or 'application/octet-stream'
        
        # Get additional metadata for images
        width, height = None, None
        if file_type == 'image':
            width, height = get_image_dimensions(file_path)
        
        # Create database record
        media_item = MediaItem(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=f"{UPLOAD_FOLDER}/{unique_filename}",
            file_type=file_type,
            mime_type=mime_type,
            file_size=file_size,
            width=width,
            height=height,
            title=request.form.get('title', original_filename),
            caption=request.form.get('caption'),
            alt_text=request.form.get('alt_text'),
            uploaded_by=request.form.get('user_id', 1)  # Default to first user for now
        )
        
        db.session.add(media_item)
        db.session.commit()
        
        return jsonify(media_item.to_dict()), 201
        
    except Exception as e:
        # Clean up file if database operation fails
        if os.path.exists(file_path):
            os.remove(file_path)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@media_bp.route('/media', methods=['GET'])
def get_media():
    """Get media items with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    file_type = request.args.get('type')
    
    query = MediaItem.query
    
    if file_type:
        query = query.filter(MediaItem.file_type == file_type)
    
    media_items = query.order_by(MediaItem.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'media': [item.to_dict() for item in media_items.items],
        'total': media_items.total,
        'pages': media_items.pages,
        'current_page': page,
        'per_page': per_page,
        'has_next': media_items.has_next,
        'has_prev': media_items.has_prev
    })

@media_bp.route('/media/<int:media_id>', methods=['GET'])
def get_media_item(media_id):
    """Get single media item"""
    media_item = MediaItem.query.get_or_404(media_id)
    return jsonify(media_item.to_dict())

@media_bp.route('/media/<int:media_id>', methods=['PUT'])
def update_media_item(media_id):
    """Update media item metadata"""
    media_item = MediaItem.query.get_or_404(media_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Update metadata fields
    if 'title' in data:
        media_item.title = data['title']
    if 'caption' in data:
        media_item.caption = data['caption']
    if 'alt_text' in data:
        media_item.alt_text = data['alt_text']
    
    try:
        db.session.commit()
        return jsonify(media_item.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@media_bp.route('/media/<int:media_id>', methods=['DELETE'])
def delete_media_item(media_id):
    """Delete media item"""
    media_item = MediaItem.query.get_or_404(media_id)
    
    # Delete file from filesystem
    file_path = os.path.join(current_app.static_folder, media_item.file_path)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500
    
    try:
        db.session.delete(media_item)
        db.session.commit()
        return jsonify({'message': 'Media item deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@media_bp.route('/uploads/<path:filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    upload_path = os.path.join(current_app.static_folder, UPLOAD_FOLDER)
    return send_from_directory(upload_path, filename)

@media_bp.route('/media/types', methods=['GET'])
def get_media_types():
    """Get available media types and their counts"""
    from sqlalchemy import func
    
    type_counts = db.session.query(
        MediaItem.file_type,
        func.count(MediaItem.id).label('count')
    ).group_by(MediaItem.file_type).all()
    
    return jsonify([
        {'type': type_name, 'count': count}
        for type_name, count in type_counts
    ])

