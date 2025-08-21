#!/usr/bin/env python3
"""
High Priestess Bot - Simple Production Version
Optimized for cloud hosting without PostgreSQL dependency
"""

import os
import json
import random
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

import tweepy
from tweepy import StreamingClient, StreamRule
from openai import OpenAI
from dotenv import load_dotenv
import ephem
from fastapi import FastAPI
import redis
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use SQLite for simple deployment
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///high_priestess.db')
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis setup (optional - will work without it)
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        password=os.getenv('REDIS_PASSWORD'),
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    redis_client = None
    REDIS_AVAILABLE = False
    logger.warning("Redis not available, using in-memory rate limiting")

class Reading(Base):
    """Simple reading model"""
    __tablename__ = "readings"
    
    id = Column(Integer, primary_key=True)
    tweet_id = Column(String, unique=True)
    user_id = Column(String)
    username = Column(String)
    cards_drawn = Column(Text)
    reading_text = Column(Text)
    reading_type = Column(String)
    engagement_score = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class HighPriestessBot:
    """Simple High Priestess Bot for cloud deployment"""
    
    def __init__(self):
        self.load_config()
        self.setup_twitter()
        self.load_tarot_data()
        self.setup_ai()
        self.load_system_prompt()
        
        # Simple rate limiting without Redis
        self.rate_limits = {}
        self.last_cleanup = datetime.utcnow()
        
        # Heaven.xyz counter
        self.heaven_counter = 0
        self.heaven_frequency = 15
        
        logger.info("High Priestess Bot initialized for cloud deployment 🌙")
    
    def load_config(self):
        """Load configuration with validation"""
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
            'bot_username': os.getenv('BOT_USERNAME', 'HP_Selene')
        }
    
    def setup_twitter(self):
        """Initialize Twitter clients"""
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
            
            # Test connection
            self.twitter_client.get_me()
            logger.info("Twitter API connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API: {e}")
            raise
    
    def setup_ai(self):
        """Initialize AI client"""
        self.openai_client = OpenAI(api_key=self.config['openai_api_key'])
        self.ai_model = "gpt-3.5-turbo"  # Cost-effective model
        logger.info(f"AI model configured: {self.ai_model}")
    
    def load_tarot_data(self):
        """Load tarot mappings"""
        try:
            with open('tarot_crypto_mapping.json', 'r') as f:
                self.tarot_data = json.load(f)
            
            self.major_arcana = self.tarot_data['major_arcana']
            self.suits = self.tarot_data['suits']
            self.reading_contexts = self.tarot_data['reading_contexts']
            self.minor_arcana = self._build_minor_arcana()
            
            logger.info("Tarot data loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load tarot data: {e}")
            raise
    
    def _build_minor_arcana(self) -> Dict:
        """Build minor arcana cards"""
        minor = {}
        court_cards = ['Page', 'Knight', 'Queen', 'King']
        
        for suit_name, suit_data in self.suits.items():
            # Number cards
            for num in range(1, 11):
                card_name = f"{self._number_to_name(num)} of {suit_name.capitalize()}"
                minor[card_name] = {
                    'suit': suit_name,
                    'number': num,
                    'element': suit_data['element'],
                    'crypto_aspect': suit_data['crypto_aspect']
                }
            
            # Court cards
            for court in court_cards:
                card_name = f"{court} of {suit_name.capitalize()}"
                minor[card_name] = {
                    'suit': suit_name,
                    'court': court,
                    'element': suit_data['element'],
                    'crypto_aspect': suit_data['crypto_aspect']
                }
                
        return minor
    
    def _number_to_name(self, num: int) -> str:
        """Convert number to card name"""
        names = {
            1: 'Ace', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five',
            6: 'Six', 7: 'Seven', 8: 'Eight', 9: 'Nine', 10: 'Ten'
        }
        return names.get(num, str(num))
    
    def load_system_prompt(self):
        """Load system prompt"""
        try:
            with open('system_prompt.md', 'r') as f:
                self.system_prompt = f.read()
            logger.info("System prompt loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            raise
    
    def get_moon_phase(self) -> Tuple[str, str]:
        """Get current moon phase"""
        observer = ephem.Observer()
        observer.date = ephem.now()
        moon = ephem.Moon()
        moon.compute(observer)
        
        phase = moon.phase
        
        if phase < 1:
            return "New Moon", "🌑"
        elif phase < 25:
            return "Waxing Crescent", "🌒"
        elif phase < 50:
            return "First Quarter", "🌓"
        elif phase < 75:
            return "Waxing Gibbous", "🌔"
        elif phase < 99:
            return "Full Moon", "🌕"
        elif phase < 125:
            return "Waning Gibbous", "🌖"
        elif phase < 150:
            return "Last Quarter", "🌗"
        else:
            return "Waning Crescent", "🌘"
    
    def draw_cards(self, count: int = 1, context: str = "general") -> List[Dict]:
        """Draw tarot cards"""
        all_cards = list(self.major_arcana.keys()) + list(self.minor_arcana.keys())
        selected = random.sample(all_cards, min(count, len(all_cards)))
        
        cards = []
        for card_key in selected:
            reversed = random.random() < 0.3
            
            if card_key in self.major_arcana:
                card_data = self.major_arcana[card_key].copy()
            else:
                card_data = self.minor_arcana.get(card_key, {}).copy()
            
            card_data['reversed'] = reversed
            card_data['key'] = card_key
            cards.append(card_data)
            
        return cards
    
    def generate_reading(self, cards: List[Dict], context: Dict) -> str:
        """Generate mystical reading"""
        card_descriptions = []
        for card in cards:
            desc = f"{card.get('name', card['key'])}"
            if card.get('reversed'):
                desc += " (Reversed)"
            if 'crypto_metaphor' in card:
                desc += f" - {card['crypto_metaphor']}"
            card_descriptions.append(desc)
        
        # Check Heaven.xyz mention
        self.heaven_counter += 1
        include_heaven = self.heaven_counter >= self.heaven_frequency
        if include_heaven:
            self.heaven_counter = 0
        
        moon_phase, moon_emoji = self.get_moon_phase()
        
        prompt = f"""Generate a mystical tweet as the High Priestess Oracle.

Cards drawn: {', '.join(card_descriptions)}
Context: {context.get('type', 'general reading')}
Moon phase: {moon_phase}
Include Heaven.xyz reference: {include_heaven}

Create a short, cryptic, engaging tweet that:
1. Interprets these cards mysteriously
2. Weaves in subtle crypto themes naturally
3. Ends with a hook or call to action
4. Uses 1-2 emojis maximum
5. Stays under 250 characters
6. Maintains the High Priestess mystical voice

Remember: Be cryptic yet clear, wise yet playful."""

        try:
            response = self.openai_client.chat.completions.create(
                model=self.ai_model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return self.generate_fallback_reading(cards)
    
    def generate_fallback_reading(self, cards: List[Dict]) -> str:
        """Fallback reading generation"""
        templates = [
            "The {card} whispers of {metaphor}... Are you listening? 🌙",
            "{card} reveals what you already know... {metaphor} ✨",
            "In the shadow of {card}, {metaphor} emerges 🔮",
            "The veil parts... {card} speaks of {metaphor} 🕊️"
        ]
        
        template = random.choice(templates)
        card = cards[0]
        
        reading = template.format(
            card=card.get('name', card['key']),
            metaphor=card.get('crypto_metaphor', 'hidden truths')[:50]
        )
        
        return reading[:280]
    
    def is_rate_limited(self, user_id: str) -> bool:
        """Check if user is rate limited"""
        now = datetime.utcnow()
        
        # Cleanup old entries every hour
        if now - self.last_cleanup > timedelta(hours=1):
            cutoff = now - timedelta(hours=1)
            self.rate_limits = {k: v for k, v in self.rate_limits.items() if v > cutoff}
            self.last_cleanup = now
        
        if REDIS_AVAILABLE:
            return bool(redis_client.get(f"rate_limit:{user_id}"))
        else:
            return user_id in self.rate_limits and self.rate_limits[user_id] > now - timedelta(hours=1)
    
    def set_rate_limit(self, user_id: str):
        """Set rate limit for user"""
        if REDIS_AVAILABLE:
            redis_client.setex(f"rate_limit:{user_id}", 3600, "1")
        else:
            self.rate_limits[user_id] = datetime.utcnow()
    
    async def post_scheduled_reading(self, reading_type: str = "daily"):
        """Post scheduled reading"""
        try:
            if reading_type == "dawn":
                count = 1
                context = {"type": "morning", "focus": "day ahead"}
            elif reading_type == "twilight":
                count = 1
                context = {"type": "evening", "focus": "reflection"}
            elif reading_type == "witching":
                count = 2
                context = {"type": "mystery", "focus": "deep wisdom"}
            else:
                count = random.choice([1, 2, 3])
                context = {"type": "general"}
            
            cards = self.draw_cards(count, context.get('type', 'general'))
            reading = self.generate_reading(cards, context)
            
            # Post to Twitter
            response = self.twitter_client.create_tweet(text=reading)
            logger.info(f"Posted scheduled {reading_type} reading: {response.data['id']}")
            
            # Store in database
            self.store_reading(
                tweet_id=response.data['id'],
                cards=cards,
                reading_text=reading,
                reading_type=reading_type
            )
            
        except Exception as e:
            logger.error(f"Error posting scheduled reading: {e}")
    
    def store_reading(self, tweet_id: str, cards: List[Dict], 
                     reading_text: str, reading_type: str, 
                     user_id: str = None, username: str = None):
        """Store reading in database"""
        try:
            db = SessionLocal()
            reading = Reading(
                tweet_id=tweet_id,
                user_id=user_id or "scheduled",
                username=username or "scheduled",
                cards_drawn=json.dumps(cards),
                reading_text=reading_text,
                reading_type=reading_type
            )
            db.add(reading)
            db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Database error: {e}")
    
    async def run(self):
        """Main bot loop"""
        logger.info("🌙 High Priestess Bot awakening...")
        
        # Create database tables
        Base.metadata.create_all(bind=engine)
        
        while True:
            try:
                current_hour = datetime.now().hour
                
                # Dawn reading (6 AM UTC)
                if current_hour == 6:
                    await self.post_scheduled_reading("dawn")
                    
                # Twilight reading (6 PM UTC)
                elif current_hour == 18:
                    await self.post_scheduled_reading("twilight")
                    
                # Witching hour (Midnight UTC)
                elif current_hour == 0:
                    await self.post_scheduled_reading("witching")
                
                # Check for moon events
                moon_phase = self.get_moon_phase()[0]
                if moon_phase in ["New Moon", "Full Moon"]:
                    await self.post_scheduled_reading("moon")
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
            
            # Sleep for an hour
            await asyncio.sleep(3600)

# FastAPI app for health checks
app = FastAPI(title="High Priestess Oracle")

bot = None

@app.on_event("startup")
async def startup_event():
    global bot
    bot = HighPriestessBot()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "moon_phase": bot.get_moon_phase()[0] if bot else "unknown"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "🌙 High Priestess Oracle is awakened"}

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "web":
        # Run FastAPI server
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    else:
        # Run the bot
        bot = HighPriestessBot()
        asyncio.run(bot.run())
