from logger_config import setup_logger
import psycopg2
import os

logger = setup_logger()

def get_database_connection():
    try:
        logger.info("Attempting database connection")
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        logger.info("Database connection successful")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}\n{traceback.format_exc()}")
        raise

def init_db():
    logger.info("Initializing database")
    conn = get_database_connection()
    cur = conn.cursor()
    
    try:
        # Create users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(200) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL
            )
        ''')
        
        # Create music_videos table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS music_videos (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                artist VARCHAR(200) NOT NULL,
                url VARCHAR(500) NOT NULL,
                user_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}\n{traceback.format_exc()}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()