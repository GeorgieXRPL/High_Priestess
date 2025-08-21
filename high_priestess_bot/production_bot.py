"""
High Priestess Bot - Production Version
Enhanced with monitoring, error handling, and production features
"""

import os
import json
import random
import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from contextlib import asynccontextmanager

import tweepy
from tweepy import StreamingClient, StreamRule
import openai
from dotenv import load_dotenv
import ephem
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import redis
import psycopg2
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

# Load environment variables
load_dotenv()

# Initialize Sentry for error tracking
if os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[
            FastApiIntegration(auto_enabling=True),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        environment=os.getenv('ENVIRONMENT', 'development')
    )

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/high_priestess.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Database setup
Base = declarative_base()
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///high_priestess.db')
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis setup
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    password=os.getenv('REDIS_PASSWORD'),
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True
)

class Reading(Base):
    """Enhanced Reading model with production features"""
    __tablename__ = "readings"
    
    id = Column(Integer, primary_key=True)
    tweet_id = Column(String, unique=True)
    user_id = Column(String)
    username = Column(String)
    cards_drawn = Column(Text)
    reading_text = Column(Text)
    reading_type = Column(String)
    engagement_score = Column(Float, default=0)
    is_viral = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BotMetrics(Base):
    """Track bot performance metrics"""
    __tablename__ = "bot_metrics"
    
    id = Column(Integer, primary_key=True)
    metric_name = Column(String(50))
    metric_value = Column(Float)
    metric_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class HighPriestessBot:
    """Production-ready High Priestess Bot"""
    
    def __init__(self):
        self.load_config()
        self.setup_twitter()
        self.load_tarot_data()
        self.setup_ai()
        self.load_system_prompt()
        
        # Production features
        self.running = False
        self.health_status = "starting"
        self.last_heartbeat = datetime.utcnow()
        
        # Rate limiting
        self.user_rate_limit = int(os.getenv('USER_RATE_LIMIT_HOURS', 1)) * 3600
        self.daily_post_limit = int(os.getenv('DAILY_POST_LIMIT', 50))
        
        # Metrics tracking
        self.metrics = {
            'total_readings': 0,
            'successful_posts': 0,
            'failed_posts': 0,
            'api_errors': 0
        }
        
        logger.info("High Priestess Bot initialized for production 🌙")
    
    def load_config(self):
        """Load production configuration"""
        required_vars = [
            'TWITTER_API_KEY', 'TWITTER_API_SECRET',
            'TWITTER_ACCESS_TOKEN', 'TWITTER_ACCESS_SECRET',
            'TWITTER_BEARER_TOKEN', 'OPENAI_API_KEY'
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        self.config = {
            'twitter_api_key': os.getenv('TWITTER_API_KEY'),
            'twitter_api_secret': os.getenv('TWITTER_API_SECRET'),
            'twitter_access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
            'twitter_access_secret': os.getenv('TWITTER_ACCESS_SECRET'),
            'twitter_bearer_token': os.getenv('TWITTER_BEARER_TOKEN'),
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'bot_username': os.getenv('BOT_USERNAME', 'HighPriestessAI'),
            'environment': os.getenv('ENVIRONMENT', 'development'),
            'debug': os.getenv('DEBUG', 'false').lower() == 'true'
        }
    
    def setup_twitter(self):
        """Initialize Twitter clients with error handling"""
        try:
            auth = tweepy.OAuthHandler(
                self.config['twitter_api_key'],
                self.config['twitter_api_secret']
            )
            auth.set_access_token(
                self.config['twitter_access_token'],
                self.config['twitter_access_secret']
            )
            
            self.twitter_client = tweepy.Client(
                bearer_token=self.config['twitter_bearer_token'],
                consumer_key=self.config['twitter_api_key'],
                consumer_secret=self.config['twitter_api_secret'],
                access_token=self.config['twitter_access_token'],
                access_token_secret=self.config['twitter_access_secret'],
                wait_on_rate_limit=True
            )
            
            self.twitter_api = tweepy.API(auth, wait_on_rate_limit=True)
            
            # Test connection
            self.twitter_client.get_me()
            logger.info("Twitter API connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            raise
    
    def setup_ai(self):
        """Initialize AI client"""
        openai.api_key = self.config['openai_api_key']
        self.ai_model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')  # Default to cheaper model
        logger.info(f"AI model configured: {self.ai_model}")
    
    def load_tarot_data(self):
        """Load tarot mappings"""
        try:
            with open('tarot_crypto_mapping.json', 'r') as f:
                self.tarot_data = json.load(f)
            logger.info("Tarot data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load tarot data: {e}")
            raise
    
    def load_system_prompt(self):
        """Load system prompt"""
        try:
            with open('system_prompt.md', 'r') as f:
                self.system_prompt = f.read()
            logger.info("System prompt loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            raise
    
    async def health_check(self):
        """Health check endpoint"""
        try:
            # Check database
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            
            # Check Redis
            redis_client.ping()
            
            # Check Twitter API
            self.twitter_client.get_me()
            
            self.health_status = "healthy"
            self.last_heartbeat = datetime.utcnow()
            
            return {
                "status": "healthy",
                "timestamp": self.last_heartbeat,
                "metrics": self.metrics,
                "environment": self.config['environment']
            }
            
        except Exception as e:
            self.health_status = "unhealthy"
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow()
            }
    
    async def post_reading_with_retry(self, reading_text: str, reply_to: str = None, max_retries: int = 3):
        """Post tweet with retry logic"""
        for attempt in range(max_retries):
            try:
                if reply_to:
                    response = self.twitter_client.create_tweet(
                        text=reading_text,
                        in_reply_to_tweet_id=reply_to
                    )
                else:
                    response = self.twitter_client.create_tweet(text=reading_text)
                
                self.metrics['successful_posts'] += 1
                logger.info(f"Successfully posted tweet: {response.data['id']}")
                return response.data['id']
                
            except tweepy.TooManyRequests:
                wait_time = 15 * 60 * (attempt + 1)  # Exponential backoff
                logger.warning(f"Rate limited, waiting {wait_time} seconds")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                self.metrics['failed_posts'] += 1
                self.metrics['api_errors'] += 1
                logger.error(f"Tweet attempt {attempt + 1} failed: {e}")
                
                if attempt == max_retries - 1:
                    raise
                    
                await asyncio.sleep(5 * (attempt + 1))
        
        return None
    
    def track_metrics(self, metric_name: str, value: float):
        """Track performance metrics"""
        db = SessionLocal()
        try:
            metric = BotMetrics(
                metric_name=metric_name,
                metric_value=value
            )
            db.add(metric)
            db.commit()
            self.metrics[metric_name] = value
        except Exception as e:
            logger.error(f"Failed to track metric {metric_name}: {e}")
            db.rollback()
        finally:
            db.close()
    
    def graceful_shutdown(self, signum, frame):
        """Handle graceful shutdown"""
        logger.info("Received shutdown signal, stopping bot gracefully...")
        self.running = False
        
        # Save final metrics
        self.track_metrics('uptime_hours', 
                          (datetime.utcnow() - self.start_time).total_seconds() / 3600)
        
        sys.exit(0)
    
    async def run_production(self):
        """Main production run loop with enhanced error handling"""
        self.running = True
        self.start_time = datetime.utcnow()
        self.health_status = "running"
        
        # Set up signal handlers
        signal.signal(signal.SIGTERM, self.graceful_shutdown)
        signal.signal(signal.SIGINT, self.graceful_shutdown)
        
        logger.info("🌙 High Priestess Bot awakening in production mode...")
        
        # Start background tasks
        tasks = [
            asyncio.create_task(self.scheduled_posting_loop()),
            asyncio.create_task(self.metrics_reporting_loop()),
            asyncio.create_task(self.health_monitoring_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            self.health_status = "error"
            raise
    
    async def scheduled_posting_loop(self):
        """Enhanced scheduled posting with production features"""
        while self.running:
            try:
                current_hour = datetime.now().hour
                
                # Check daily post limit
                today_posts = redis_client.get(f"daily_posts:{datetime.now().date()}")
                if today_posts and int(today_posts) >= self.daily_post_limit:
                    logger.warning("Daily post limit reached")
                    await asyncio.sleep(3600)  # Wait an hour
                    continue
                
                # Dawn reading (6 AM UTC)
                if current_hour == 6:
                    await self.post_scheduled_reading("dawn")
                    
                # Twilight reading (6 PM UTC)
                elif current_hour == 18:
                    await self.post_scheduled_reading("twilight")
                    
                # Witching hour (Midnight UTC)
                elif current_hour == 0:
                    await self.post_scheduled_reading("witching")
                
                # Increment daily post counter
                redis_client.incr(f"daily_posts:{datetime.now().date()}")
                redis_client.expire(f"daily_posts:{datetime.now().date()}", 86400)
                
            except Exception as e:
                logger.error(f"Error in scheduled posting: {e}")
                self.metrics['api_errors'] += 1
            
            await asyncio.sleep(3600)  # Check every hour
    
    async def metrics_reporting_loop(self):
        """Report metrics periodically"""
        while self.running:
            try:
                # Report key metrics
                self.track_metrics('total_readings_hourly', self.metrics['total_readings'])
                self.track_metrics('success_rate', 
                                 self.metrics['successful_posts'] / 
                                 max(1, self.metrics['successful_posts'] + self.metrics['failed_posts']))
                
                logger.info(f"Metrics update: {self.metrics}")
                
            except Exception as e:
                logger.error(f"Error reporting metrics: {e}")
            
            await asyncio.sleep(3600)  # Report every hour
    
    async def health_monitoring_loop(self):
        """Monitor bot health"""
        while self.running:
            try:
                await self.health_check()
                
                # Check if we've been unhealthy too long
                if (self.health_status == "unhealthy" and 
                    datetime.utcnow() - self.last_heartbeat > timedelta(minutes=10)):
                    logger.critical("Bot has been unhealthy for too long, initiating restart")
                    # In production, this could trigger a container restart
                    
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
            
            await asyncio.sleep(300)  # Check every 5 minutes

# Enhanced FastAPI app with production features
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting High Priestess Bot API")
    yield
    # Shutdown
    logger.info("Shutting down High Priestess Bot API")

app = FastAPI(
    title="High Priestess Oracle API",
    description="Mystical tarot readings for the digital age",
    version="1.0.0",
    lifespan=lifespan
)

# Global bot instance
bot = HighPriestessBot()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return await bot.health_check()

@app.get("/metrics")
async def get_metrics():
    """Get bot metrics"""
    return {
        "metrics": bot.metrics,
        "status": bot.health_status,
        "uptime": (datetime.utcnow() - bot.start_time).total_seconds() if hasattr(bot, 'start_time') else 0
    }

@app.post("/reading")
async def generate_reading(background_tasks: BackgroundTasks):
    """Generate and post a reading"""
    try:
        cards = bot.draw_cards(random.choice([1, 2, 3]))
        reading = bot.generate_reading(cards, {"type": "api_request"})
        
        # Post in background
        background_tasks.add_task(bot.post_reading_with_retry, reading)
        
        return {
            "reading": reading,
            "cards": [card.get('name', card.get('key', 'Unknown')) for card in cards],
            "status": "posted"
        }
        
    except Exception as e:
        logger.error(f"API reading generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize database tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    import uvicorn
    
    # Check if running as web server or bot
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        # Run FastAPI server
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        # Run the bot
        bot = HighPriestessBot()
        asyncio.run(bot.run_production())
