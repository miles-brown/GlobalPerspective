# News Website Deployment Guide

## Overview

This guide provides multiple deployment options for your Global Affairs news website, from simple local development to production-ready cloud deployments.

## 🚀 Quick Start (Local Development)

### Prerequisites
- Node.js 18+ and npm/pnpm
- Python 3.8+ and pip
- Git

### 1. Setup Backend (Flask)
```bash
# Navigate to backend directory
cd news_website

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install flask flask-cors sqlalchemy werkzeug

# Start the Flask server
python src/main.py
```
The backend will run on `http://localhost:5000`

### 2. Setup Frontend (React)
```bash
# Navigate to frontend directory
cd news-frontend

# Install dependencies
npm install
# or
pnpm install

# Start development server
npm run dev
# or
pnpm run dev
```
The frontend will run on `http://localhost:5173`

### 3. Access the Website
- **Main Website**: http://localhost:5173
- **CMS Interface**: http://localhost:5173/cms
- **API Endpoints**: http://localhost:5000/api

## 📦 Deployment Options

### Option 1: Simple VPS Deployment (Recommended for Small Sites)

**Best for**: Personal blogs, small news sites, development/staging environments
**Cost**: $5-20/month
**Complexity**: Beginner-friendly

#### Providers
- DigitalOcean Droplets
- Linode
- Vultr
- AWS EC2 (t2.micro free tier)

#### Steps
1. **Prepare Production Build**
```bash
# Build React frontend
cd news-frontend
npm run build

# Copy build to Flask static directory
cp -r dist/* ../news_website/src/static/
```

2. **Deploy to VPS**
```bash
# Upload files to server
scp -r news_website/ user@your-server-ip:/var/www/

# SSH into server
ssh user@your-server-ip

# Setup Python environment
cd /var/www/news_website
python -m venv venv
source venv/bin/activate
pip install flask flask-cors sqlalchemy werkzeug gunicorn

# Install and configure Nginx
sudo apt update
sudo apt install nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/news-website
```

3. **Nginx Configuration**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /var/www/news_website/src/static;
    }
}
```

4. **Start Services**
```bash
# Enable Nginx site
sudo ln -s /etc/nginx/sites-available/news-website /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Start Flask with Gunicorn
cd /var/www/news_website
source venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:5000 src.main:app
```

### Option 2: Docker Deployment

**Best for**: Consistent environments, easy scaling, DevOps workflows
**Cost**: Variable (depends on hosting)
**Complexity**: Intermediate

#### Create Dockerfile for Backend
```dockerfile
# news_website/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY venv/ ./venv/

EXPOSE 5000
CMD ["python", "src/main.py"]
```

#### Create requirements.txt
```txt
Flask==2.3.3
Flask-CORS==4.0.0
SQLAlchemy==2.0.21
Werkzeug==2.3.7
gunicorn==21.2.0
```

#### Docker Compose Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./news_website
    ports:
      - "5000:5000"
    volumes:
      - ./news_website/src/database:/app/src/database
    environment:
      - FLASK_ENV=production

  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./news-frontend/dist:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
```

#### Deploy with Docker
```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 3: Cloud Platform Deployment

#### Heroku (Easiest Cloud Option)
```bash
# Install Heroku CLI
# Create Procfile in news_website/
echo "web: gunicorn src.main:app" > Procfile

# Deploy
heroku create your-news-website
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

#### Vercel (Frontend) + Railway (Backend)
```bash
# Deploy frontend to Vercel
cd news-frontend
npm install -g vercel
vercel --prod

# Deploy backend to Railway
# Connect GitHub repo to Railway dashboard
```

#### AWS (Advanced)
- **Frontend**: S3 + CloudFront
- **Backend**: Elastic Beanstalk or ECS
- **Database**: RDS (PostgreSQL/MySQL)
- **CDN**: CloudFront for static assets

### Option 4: Managed Hosting Platforms

#### Netlify + Heroku
- **Frontend**: Deploy to Netlify (automatic from Git)
- **Backend**: Deploy to Heroku
- **Database**: Heroku Postgres add-on

#### Vercel + PlanetScale
- **Frontend**: Vercel (automatic deployment)
- **Backend**: Vercel Serverless Functions
- **Database**: PlanetScale MySQL

## 🔧 Production Optimizations

### Database Migration (SQLite → PostgreSQL)
```python
# Update requirements.txt
psycopg2-binary==2.9.7

# Update database configuration
import os
from sqlalchemy import create_engine

if os.environ.get('DATABASE_URL'):
    # Production database
    engine = create_engine(os.environ.get('DATABASE_URL'))
else:
    # Development database
    engine = create_engine('sqlite:///database/app.db')
```

### Environment Variables
```bash
# .env file
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@host:port/dbname
UPLOAD_FOLDER=/var/www/uploads
MAX_CONTENT_LENGTH=16777216  # 16MB
```

### Security Enhancements
```python
# Add to Flask app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Add HTTPS redirect
from flask_talisman import Talisman
Talisman(app, force_https=True)
```

### Performance Optimizations
```python
# Add caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/articles')
@cache.cached(timeout=300)  # Cache for 5 minutes
def get_articles():
    return jsonify(articles)
```

## 📊 Monitoring & Analytics

### Basic Monitoring
```python
# Add logging
import logging
logging.basicConfig(level=logging.INFO)

# Add health check endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'timestamp': datetime.utcnow()}
```

### Analytics Integration
```html
<!-- Add to index.html -->
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 🔒 Security Checklist

- [ ] Use HTTPS (SSL certificate)
- [ ] Set up proper CORS policies
- [ ] Implement rate limiting
- [ ] Validate and sanitize user inputs
- [ ] Use environment variables for secrets
- [ ] Regular security updates
- [ ] Backup database regularly
- [ ] Monitor for suspicious activity

## 💰 Cost Estimates

### Small Site (< 1000 visitors/month)
- **VPS**: $5-10/month (DigitalOcean, Linode)
- **Domain**: $10-15/year
- **SSL**: Free (Let's Encrypt)
- **Total**: ~$70-135/year

### Medium Site (< 10,000 visitors/month)
- **VPS**: $20-40/month
- **CDN**: $5-10/month
- **Database**: $15-25/month
- **Total**: ~$480-900/year

### Large Site (> 50,000 visitors/month)
- **Cloud hosting**: $100-300/month
- **CDN**: $20-50/month
- **Database**: $50-100/month
- **Total**: ~$2000-5400/year

