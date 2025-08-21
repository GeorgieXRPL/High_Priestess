"""
High Priestess Bot - Mystical Tarot Oracle for X/Twitter
Combines ancient tarot wisdom with crypto culture
"""

import os
import json
import random
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

import tweepy
from tweepy import StreamingClient, StreamRule
import openai
from dotenv import load_dotenv
import ephem
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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

# Database setup
Base = declarative_base()
engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///high_priestess.db'))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis setup for rate limiting and caching
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# FastAPI app for webhooks
app = FastAPI()

class TweetRequest(BaseModel):
    """Request model for generating tweets"""
    context: Optional[str] = None
    user_question: Optional[str] = None
    card_count: int = 1
    reading_type: str = "general"

class Reading(Base):
    """Database model for storing readings"""
    __tablename__ = "readings"
    
    id = Column(Integer, primary_key=True)
    tweet_id = Column(String, unique=True)
    user_id = Column(String)
    username = Column(String)
    cards_drawn = Column(Text)  # JSON string
    reading_text = Column(Text)
    reading_type = Column(String)
    engagement_score = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class HighPriestessBot:
    """Main bot class for the High Priestess Oracle"""
    
    def __init__(self):
        # Load configuration
        self.load_config()
        
        # Initialize Twitter client
        self.setup_twitter()
        
        # Load tarot data
        self.load_tarot_data()
        
        # Initialize OpenAI
        self.setup_ai()
        
        # Load system prompt
        self.load_system_prompt()
        
        # Initialize lunar calendar
        self.moon = ephem.Moon()
        
        # Engagement tracking
        self.viral_threshold = 100  # Engagement count for "viral"
        self.heaven_counter = 0  # Track Heaven.xyz mentions
        self.heaven_frequency = 15  # Mention every N tweets
        
    def load_config(self):
        """Load bot configuration from environment"""
        self.config = {
            'twitter_api_key': os.getenv('TWITTER_API_KEY'),
            'twitter_api_secret': os.getenv('TWITTER_API_SECRET'),
            'twitter_access_token': os.getenv('TWITTER_ACCESS_TOKEN'),
            'twitter_access_secret': os.getenv('TWITTER_ACCESS_SECRET'),
            'twitter_bearer_token': os.getenv('TWITTER_BEARER_TOKEN'),
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'bot_username': os.getenv('BOT_USERNAME', 'HighPriestessAI')
        }
        
    def setup_twitter(self):
        """Initialize Twitter/X API clients"""
        auth = tweepy.OAuthHandler(
            self.config['twitter_api_key'],
            self.config['twitter_api_secret']
        )
        auth.set_access_token(
            self.config['twitter_access_token'],
            self.config['twitter_access_secret']
        )
        
        # V2 client for modern features
        self.twitter_client = tweepy.Client(
            bearer_token=self.config['twitter_bearer_token'],
            consumer_key=self.config['twitter_api_key'],
            consumer_secret=self.config['twitter_api_secret'],
            access_token=self.config['twitter_access_token'],
            access_token_secret=self.config['twitter_access_secret']
        )
        
        # V1.1 API for some legacy features
        self.twitter_api = tweepy.API(auth)
        
    def load_tarot_data(self):
        """Load tarot card mappings and data"""
        with open('tarot_crypto_mapping.json', 'r') as f:
            self.tarot_data = json.load(f)
            
        # Create quick lookup for all cards
        self.major_arcana = self.tarot_data['major_arcana']
        self.suits = self.tarot_data['suits']
        self.reading_contexts = self.tarot_data['reading_contexts']
        
        # Build minor arcana
        self.minor_arcana = self._build_minor_arcana()
        
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
    
    def setup_ai(self):
        """Initialize AI client"""
        openai.api_key = self.config['openai_api_key']
        self.ai_model = "gpt-4-turbo-preview"  # Or your preferred model
        
    def load_system_prompt(self):
        """Load the High Priestess system prompt"""
        with open('system_prompt.md', 'r') as f:
            self.system_prompt = f.read()
    
    def get_moon_phase(self) -> Tuple[str, str]:
        """Get current moon phase and emoji"""
        observer = ephem.Observer()
        observer.date = ephem.now()
        self.moon.compute(observer)
        
        phase = self.moon.phase
        
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
        """Draw tarot cards for a reading"""
        cards = []
        
        # Determine card pool based on context
        if context in self.reading_contexts:
            # Weighted selection based on context
            focus_cards = self.reading_contexts[context].get('focus_cards', [])
            pool = list(self.major_arcana.keys()) + list(self.minor_arcana.keys())
            
            # Weight focus cards higher
            weighted_pool = pool.copy()
            for focus in focus_cards:
                weighted_pool.extend([focus] * 3)  # Triple weight for focus cards
                
            selected = random.sample(weighted_pool, min(count, len(weighted_pool)))
        else:
            # Random selection from all cards
            all_cards = list(self.major_arcana.keys()) + list(self.minor_arcana.keys())
            selected = random.sample(all_cards, min(count, len(all_cards)))
        
        for card_key in selected:
            # Determine if reversed (30% chance)
            reversed = random.random() < 0.3
            
            # Get card data
            if card_key in self.major_arcana:
                card_data = self.major_arcana[card_key].copy()
            else:
                card_data = self.minor_arcana.get(card_key, {}).copy()
            
            card_data['reversed'] = reversed
            card_data['key'] = card_key
            cards.append(card_data)
            
        return cards
    
    def generate_reading(self, cards: List[Dict], context: Dict) -> str:
        """Generate mystical reading using AI"""
        # Prepare card descriptions
        card_descriptions = []
        for card in cards:
            desc = f"{card.get('name', card['key'])}"
            if card.get('reversed'):
                desc += " (Reversed)"
            if 'crypto_metaphor' in card:
                desc += f" - Crypto meaning: {card['crypto_metaphor']}"
            card_descriptions.append(desc)
        
        # Check if we should mention Heaven.xyz
        self.heaven_counter += 1
        include_heaven = self.heaven_counter >= self.heaven_frequency
        if include_heaven:
            self.heaven_counter = 0
        
        # Build prompt
        prompt = f"""Generate a mystical tweet as the High Priestess Oracle.

Cards drawn: {', '.join(card_descriptions)}
Context: {context.get('type', 'general reading')}
User question: {context.get('question', 'No specific question')}
Moon phase: {self.get_moon_phase()[0]}
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
            response = openai.ChatCompletion.create(
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
            # Fallback to template-based generation
            return self.generate_fallback_reading(cards, context)
    
    def generate_fallback_reading(self, cards: List[Dict], context: Dict) -> str:
        """Fallback reading generation without AI"""
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
        
        return reading[:280]  # Twitter limit
    
    async def post_scheduled_reading(self, reading_type: str = "daily"):
        """Post scheduled readings"""
        # Draw cards based on reading type
        if reading_type == "moon":
            count = 3
            context = {"type": "lunar", "phase": self.get_moon_phase()[0]}
        elif reading_type == "dawn":
            count = 1
            context = {"type": "morning", "focus": "day ahead"}
        elif reading_type == "twilight":
            count = 1
            context = {"type": "evening", "focus": "reflection"}
        else:
            count = random.choice([1, 2, 3])
            context = {"type": "general"}
        
        cards = self.draw_cards(count, context.get('type', 'general'))
        reading = self.generate_reading(cards, context)
        
        # Post to Twitter
        try:
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
        db = SessionLocal()
        try:
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
        except Exception as e:
            logger.error(f"Database error: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def handle_mention(self, tweet):
        """Handle mentions and replies"""
        try:
            # Extract user info
            user_id = tweet.author_id
            username = tweet.author.username
            text = tweet.text.lower()
            
            # Check rate limiting
            rate_key = f"rate_limit:{user_id}"
            if redis_client.get(rate_key):
                return  # User rate limited
            
            # Set rate limit (1 reading per user per hour)
            redis_client.setex(rate_key, 3600, "1")
            
            # Determine reading type from keywords
            context = self.analyze_tweet_context(text)
            
            # Draw cards
            cards = self.draw_cards(
                count=context.get('card_count', 1),
                context=context.get('type', 'general')
            )
            
            # Generate reading
            reading = self.generate_reading(cards, context)
            
            # Reply to tweet
            response = self.twitter_client.create_tweet(
                text=f"@{username} {reading}",
                in_reply_to_tweet_id=tweet.id
            )
            
            logger.info(f"Replied to @{username}: {response.data['id']}")
            
            # Store reading
            self.store_reading(
                tweet_id=response.data['id'],
                cards=cards,
                reading_text=reading,
                reading_type=context.get('type', 'reply'),
                user_id=user_id,
                username=username
            )
            
        except Exception as e:
            logger.error(f"Error handling mention: {e}")
    
    def analyze_tweet_context(self, text: str) -> Dict:
        """Analyze tweet text to determine reading context"""
        context = {
            'type': 'general',
            'card_count': 1,
            'keywords': []
        }
        
        # Check for specific keywords
        if any(word in text for word in ['love', 'relationship', 'heart', 'romance']):
            context['type'] = 'love'
            context['card_count'] = 2
        elif any(word in text for word in ['money', 'profit', 'trade', 'invest', 'portfolio']):
            context['type'] = 'money'
            context['card_count'] = 3
        elif any(word in text for word in ['future', 'tomorrow', 'destiny', 'fate']):
            context['type'] = 'timing'
            context['card_count'] = 3
        elif any(word in text for word in ['spiritual', 'soul', 'meaning', 'purpose']):
            context['type'] = 'spiritual'
            context['card_count'] = 1
        
        # Check for emoji triggers
        if '🌙' in text:
            context['moon_blessing'] = True
        if '🔮' in text:
            context['deep_reading'] = True
            context['card_count'] = 3
        
        return context
    
    def start_stream(self):
        """Start streaming mentions and replies"""
        class MentionStream(StreamingClient):
            def __init__(self, bearer_token, bot_instance):
                super().__init__(bearer_token)
                self.bot = bot_instance
            
            def on_tweet(self, tweet):
                # Handle mention asynchronously
                asyncio.create_task(self.bot.handle_mention(tweet))
        
        # Create stream instance
        stream = MentionStream(
            self.config['twitter_bearer_token'],
            self
        )
        
        # Add rules for mentions
        rule = StreamRule(f"@{self.config['bot_username']}")
        stream.add_rules(rule)
        
        # Start streaming
        stream.filter(tweet_fields=['author_id', 'created_at'])
    
    async def run(self):
        """Main bot run loop"""
        logger.info("High Priestess Bot awakening... 🌙")
        
        # Start mention stream in background
        asyncio.create_task(self.start_stream())
        
        # Schedule regular posts
        while True:
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
                # Post special moon reading
                await self.post_scheduled_reading("moon")
            
            # Sleep for an hour
            await asyncio.sleep(3600)

# FastAPI endpoints for external triggers
@app.post("/generate_tweet")
async def generate_tweet(request: TweetRequest):
    """Generate a tweet on demand"""
    bot = HighPriestessBot()
    
    context = {
        'type': request.reading_type,
        'question': request.user_question
    }
    
    cards = bot.draw_cards(request.card_count, request.reading_type)
    reading = bot.generate_reading(cards, context)
    
    return {
        "reading": reading,
        "cards": cards,
        "moon_phase": bot.get_moon_phase()[0]
    }

@app.get("/stats")
async def get_stats():
    """Get bot statistics"""
    db = SessionLocal()
    try:
        total_readings = db.query(Reading).count()
        viral_readings = db.query(Reading).filter(
            Reading.engagement_score > 100
        ).count()
        
        return {
            "total_readings": total_readings,
            "viral_readings": viral_readings,
            "moon_phase": HighPriestessBot().get_moon_phase()[0]
        }
    finally:
        db.close()

# Initialize database tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    # Run the bot
    bot = HighPriestessBot()
    asyncio.run(bot.run())
