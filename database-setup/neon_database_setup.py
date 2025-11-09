#!/usr/bin/env python3
"""
Neon Database Setup Script for GlobalPerspective News Platform
This script sets up the complete database schema in Neon PostgreSQL
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from datetime import datetime

# Neon Database Connection Details
NEON_CONNECTION_STRING = "postgresql://neondb_owner:npg_De3IxqN5TFfG@ep-rough-river-afmryuc9-pooler.c-2.us-west-2.aws.neon.tech/neondb?channel_binding=require&sslmode=require"
PROJECT_ID = "mute-sea-09544963"
BRANCH_ID = "br-delicate-sunset-aftqtfnz"

def create_database_connection():
    """Create connection to Neon database"""
    try:
        conn = psycopg2.connect(NEON_CONNECTION_STRING)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_tables(conn):
    """Create all tables for the news platform"""
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(128),
            role VARCHAR(20) DEFAULT 'author',
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            bio TEXT,
            avatar_url VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );
    """)
    
    # Categories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            slug VARCHAR(100) UNIQUE NOT NULL,
            description TEXT,
            color VARCHAR(7) DEFAULT '#dc2626',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            slug VARCHAR(255) UNIQUE NOT NULL,
            subtitle VARCHAR(500),
            excerpt TEXT,
            content TEXT NOT NULL,
            featured_image VARCHAR(255),
            status VARCHAR(20) DEFAULT 'draft',
            is_featured BOOLEAN DEFAULT FALSE,
            is_breaking BOOLEAN DEFAULT FALSE,
            view_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            reading_time INTEGER DEFAULT 5,
            seo_title VARCHAR(255),
            seo_description TEXT,
            seo_keywords TEXT,
            published_at TIMESTAMP,
            scheduled_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            author_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL
        );
    """)
    
    # Comments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            author_name VARCHAR(100),
            author_email VARCHAR(120),
            author_website VARCHAR(255),
            ip_address VARCHAR(45),
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
            author_id INTEGER REFERENCES users(id) ON DELETE SET NULL
        );
    """)
    
    # Media items table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS media_items (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            original_filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500) NOT NULL,
            file_size INTEGER,
            mime_type VARCHAR(100),
            file_type VARCHAR(20),
            alt_text VARCHAR(255),
            caption TEXT,
            uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            article_id INTEGER REFERENCES articles(id) ON DELETE SET NULL
        );
    """)
    
    # Article revisions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_revisions (
            id SERIAL PRIMARY KEY,
            article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            excerpt TEXT,
            revision_number INTEGER DEFAULT 1,
            created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            change_summary TEXT
        );
    """)
    
    # Workflow steps table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflow_steps (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            "order" INTEGER DEFAULT 0,
            required_role VARCHAR(20),
            auto_advance BOOLEAN DEFAULT FALSE,
            notification_template TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Article workflow table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS article_workflows (
            id SERIAL PRIMARY KEY,
            article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
            step_id INTEGER REFERENCES workflow_steps(id) ON DELETE CASCADE,
            assigned_to INTEGER REFERENCES users(id) ON DELETE SET NULL,
            status VARCHAR(20) DEFAULT 'pending',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            notes TEXT
        );
    """)
    
    # Scheduled posts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id SERIAL PRIMARY KEY,
            article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
            scheduled_for TIMESTAMP NOT NULL,
            timezone VARCHAR(50) DEFAULT 'UTC',
            status VARCHAR(20) DEFAULT 'scheduled',
            created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published_at TIMESTAMP,
            error_message TEXT
        );
    """)
    
    # SEO analysis table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seo_analysis (
            id SERIAL PRIMARY KEY,
            article_id INTEGER REFERENCES articles(id) ON DELETE CASCADE,
            seo_score FLOAT DEFAULT 0.0,
            readability_score FLOAT DEFAULT 0.0,
            keyword_density JSONB,
            meta_analysis JSONB,
            suggestions JSONB,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Content templates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_templates (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            template_type VARCHAR(50),
            content_structure JSONB,
            default_values JSONB,
            created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
            is_active BOOLEAN DEFAULT TRUE,
            usage_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Bulk operations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bulk_operations (
            id SERIAL PRIMARY KEY,
            operation_type VARCHAR(50) NOT NULL,
            target_type VARCHAR(50) NOT NULL,
            target_ids JSONB,
            operation_data JSONB,
            status VARCHAR(20) DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            total_items INTEGER DEFAULT 0,
            success_count INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            error_log JSONB,
            created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
    """)
    
    # System settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            id SERIAL PRIMARY KEY,
            setting_key VARCHAR(100) UNIQUE NOT NULL,
            setting_value JSONB,
            setting_type VARCHAR(20) DEFAULT 'string',
            description TEXT,
            is_public BOOLEAN DEFAULT FALSE,
            updated_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Analytics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            page_views INTEGER DEFAULT 0,
            unique_visitors INTEGER DEFAULT 0,
            bounce_rate FLOAT DEFAULT 0.0,
            avg_session_duration INTEGER DEFAULT 0,
            top_articles JSONB,
            top_categories JSONB,
            traffic_sources JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    print("✅ All tables created successfully!")
    cursor.close()

def create_indexes(conn):
    """Create database indexes for performance"""
    cursor = conn.cursor()
    
    # Articles indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_author_id ON articles(author_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_category_id ON articles(category_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);")
    
    # Comments indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_article_id ON comments(article_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_status ON comments(status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments(created_at);")
    
    # Users indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);")
    
    # Media items indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_items_article_id ON media_items(article_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_media_items_file_type ON media_items(file_type);")
    
    # Analytics indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics(date);")
    
    print("✅ All indexes created successfully!")
    cursor.close()

def insert_default_data(conn):
    """Insert default data for the news platform"""
    cursor = conn.cursor()
    
    # Insert default admin user
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, role, first_name, last_name, is_active)
        VALUES ('admin', 'admin@globalperspective.com', '$2b$12$LQv3c1yqBwVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3QJflLxQjm', 'admin', 'Admin', 'User', TRUE)
        ON CONFLICT (username) DO NOTHING;
    """)
    
    # Insert default categories
    categories = [
        ('World Affairs', 'world-affairs', 'International news and global politics', '#dc2626'),
        ('Business', 'business', 'Business news and economic analysis', '#059669'),
        ('Technology', 'technology', 'Technology and innovation', '#2563eb'),
        ('Culture', 'culture', 'Arts, culture, and lifestyle', '#7c3aed'),
        ('Design', 'design', 'Design and architecture', '#ea580c')
    ]
    
    for name, slug, description, color in categories:
        cursor.execute("""
            INSERT INTO categories (name, slug, description, color)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name) DO NOTHING;
        """, (name, slug, description, color))
    
    # Insert default workflow steps
    workflow_steps = [
        ('Draft Creation', 'Initial article creation by author', 1, 'author', True),
        ('Editorial Review', 'Review by editorial team', 2, 'editor', False),
        ('Final Approval', 'Final approval by admin', 3, 'admin', False),
        ('Publication', 'Article publication', 4, 'admin', True)
    ]
    
    for name, description, order, role, auto_advance in workflow_steps:
        cursor.execute("""
            INSERT INTO workflow_steps (name, description, "order", required_role, auto_advance)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
        """, (name, description, order, role, auto_advance))
    
    # Insert default system settings
    settings = [
        ('site_name', '"GlobalPerspective"', 'string', 'Site name', True),
        ('site_description', '"International News and Analysis"', 'string', 'Site description', True),
        ('articles_per_page', '20', 'integer', 'Articles per page', False),
        ('enable_comments', 'true', 'boolean', 'Enable comments', False),
        ('auto_publish_scheduled', 'true', 'boolean', 'Auto-publish scheduled posts', False),
        ('seo_analysis_enabled', 'true', 'boolean', 'Enable SEO analysis', False),
        ('email_notifications', 'true', 'boolean', 'Enable email notifications', False)
    ]
    
    for key, value, setting_type, description, is_public in settings:
        cursor.execute("""
            INSERT INTO system_settings (setting_key, setting_value, setting_type, description, is_public)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (setting_key) DO NOTHING;
        """, (key, value, setting_type, description, is_public))
    
    # Insert sample article
    cursor.execute("""
        INSERT INTO articles (
            title, slug, subtitle, excerpt, content, status, is_featured, 
            author_id, category_id, reading_time, seo_title, seo_description
        )
        SELECT 
            'Welcome to GlobalPerspective',
            'welcome-to-globalperspective',
            'Your premier source for international news and analysis',
            'Discover in-depth coverage of global affairs, business insights, and cultural perspectives from around the world.',
            'Welcome to GlobalPerspective, where we bring you comprehensive coverage of international news, business developments, and cultural insights from around the globe. Our mission is to provide thoughtful analysis and diverse perspectives on the events shaping our world today.',
            'published',
            TRUE,
            u.id,
            c.id,
            3,
            'Welcome to GlobalPerspective - International News Platform',
            'Discover comprehensive international news coverage and analysis on GlobalPerspective, your premier source for global affairs and business insights.'
        FROM users u, categories c 
        WHERE u.username = 'admin' AND c.slug = 'world-affairs'
        AND NOT EXISTS (SELECT 1 FROM articles WHERE slug = 'welcome-to-globalperspective');
    """)
    
    conn.commit()
    print("✅ Default data inserted successfully!")
    cursor.close()

def create_database_functions(conn):
    """Create useful database functions"""
    cursor = conn.cursor()
    
    # Function to update article updated_at timestamp
    cursor.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)
    
    # Trigger to automatically update updated_at
    cursor.execute("""
        DROP TRIGGER IF EXISTS update_articles_updated_at ON articles;
        CREATE TRIGGER update_articles_updated_at
            BEFORE UPDATE ON articles
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)
    
    # Function to update comment count
    cursor.execute("""
        CREATE OR REPLACE FUNCTION update_article_comment_count()
        RETURNS TRIGGER AS $$
        BEGIN
            IF TG_OP = 'INSERT' THEN
                UPDATE articles SET comment_count = comment_count + 1 WHERE id = NEW.article_id;
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                UPDATE articles SET comment_count = comment_count - 1 WHERE id = OLD.article_id;
                RETURN OLD;
            END IF;
            RETURN NULL;
        END;
        $$ language 'plpgsql';
    """)
    
    # Triggers for comment count
    cursor.execute("""
        DROP TRIGGER IF EXISTS update_comment_count_insert ON comments;
        CREATE TRIGGER update_comment_count_insert
            AFTER INSERT ON comments
            FOR EACH ROW
            EXECUTE FUNCTION update_article_comment_count();
    """)
    
    cursor.execute("""
        DROP TRIGGER IF EXISTS update_comment_count_delete ON comments;
        CREATE TRIGGER update_comment_count_delete
            AFTER DELETE ON comments
            FOR EACH ROW
            EXECUTE FUNCTION update_article_comment_count();
    """)
    
    print("✅ Database functions and triggers created successfully!")
    cursor.close()

def setup_database():
    """Main function to set up the complete database"""
    print("🚀 Setting up GlobalPerspective database on Neon...")
    print(f"📍 Project ID: {PROJECT_ID}")
    print(f"🌿 Branch ID: {BRANCH_ID}")
    
    conn = create_database_connection()
    if not conn:
        print("❌ Failed to connect to database")
        return False
    
    try:
        print("\n📋 Creating tables...")
        create_tables(conn)
        
        print("\n⚡ Creating indexes...")
        create_indexes(conn)
        
        print("\n🔧 Creating database functions...")
        create_database_functions(conn)
        
        print("\n📊 Inserting default data...")
        insert_default_data(conn)
        
        print("\n✅ Database setup completed successfully!")
        print("\n🔗 Connection details:")
        print(f"   Host: ep-rough-river-afmryuc9-pooler.c-2.us-west-2.aws.neon.tech")
        print(f"   Database: neondb")
        print(f"   User: neondb_owner")
        print(f"   SSL: Required")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    finally:
        conn.close()

def test_database_connection():
    """Test the database connection and basic queries"""
    print("\n🧪 Testing database connection...")
    
    conn = create_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"   👥 Users in database: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM categories;")
        category_count = cursor.fetchone()[0]
        print(f"   📁 Categories in database: {category_count}")
        
        cursor.execute("SELECT COUNT(*) FROM articles;")
        article_count = cursor.fetchone()[0]
        print(f"   📰 Articles in database: {article_count}")
        
        print("✅ Database connection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🌍 GLOBALPERSPECTIVE NEWS PLATFORM")
    print("🗄️  NEON DATABASE SETUP")
    print("=" * 60)
    
    success = setup_database()
    
    if success:
        test_database_connection()
        print("\n🎉 Setup complete! Your GlobalPerspective database is ready.")
        print("\n📝 Next steps:")
        print("   1. Update your Flask app to use the Neon connection string")
        print("   2. Install psycopg2-binary: pip install psycopg2-binary")
        print("   3. Test your application with the new database")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

