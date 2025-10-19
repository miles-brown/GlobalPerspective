import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.ai_content import ai_content_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(ai_content_bp, url_prefix='/api/ai')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database (use single db instance)
db.init_app(app)

with app.app_context():
    db.create_all()
    
    # Initialize default AI providers
    from src.models.content import AIProvider
    
    default_providers = [
        {
            'name': 'openai',
            'model_name': 'gpt-4-turbo',
            'is_active': True,
            'cost_per_token': 0.00003,
            'max_tokens': 4000,
            'temperature': 0.7,
            'preferred_for_news': True,
            'preferred_for_analysis': True,
            'preferred_for_opinion': False
        },
        {
            'name': 'claude',
            'model_name': 'claude-3-sonnet',
            'is_active': True,
            'cost_per_token': 0.000015,
            'max_tokens': 4000,
            'temperature': 0.7,
            'preferred_for_news': False,
            'preferred_for_analysis': True,
            'preferred_for_opinion': True
        },
        {
            'name': 'deepseek',
            'model_name': 'deepseek-chat',
            'is_active': True,
            'cost_per_token': 0.000002,
            'max_tokens': 4000,
            'temperature': 0.7,
            'preferred_for_news': True,
            'preferred_for_analysis': False,
            'preferred_for_opinion': False
        },
        {
            'name': 'manus',
            'model_name': 'manus-journalist',
            'is_active': True,
            'cost_per_token': 0.00001,
            'max_tokens': 4000,
            'temperature': 0.7,
            'preferred_for_news': True,
            'preferred_for_analysis': True,
            'preferred_for_opinion': True
        }
    ]
    
    for provider_data in default_providers:
        existing = AIProvider.query.filter_by(name=provider_data['name']).first()
        if not existing:
            provider = AIProvider(**provider_data)
            db.session.add(provider)
    
    db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
