#!/usr/bin/env python3
"""
High Priestess Bot - Monitoring and Analytics Dashboard
Real-time monitoring of bot performance and engagement
"""

import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List
import logging
from dataclasses import dataclass

import redis
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import tweepy
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotMetrics:
    total_readings: int = 0
    successful_posts: int = 0
    failed_posts: int = 0
    api_errors: int = 0
    engagement_rate: float = 0.0
    viral_tweets: int = 0
    active_users: int = 0
    uptime_hours: float = 0.0

class HighPriestessMonitor:
    """Real-time monitoring for High Priestess Bot"""
    
    def __init__(self):
        self.setup_connections()
        self.metrics = BotMetrics()
        
    def setup_connections(self):
        """Setup database and API connections"""
        # Database
        self.engine = create_engine(os.getenv('DATABASE_URL', 'sqlite:///high_priestess.db'))
        SessionLocal = sessionmaker(bind=self.engine)
        self.db_session = SessionLocal()
        
        # Redis
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            decode_responses=True
        )
        
        # Twitter API (for engagement tracking)
        self.twitter_client = tweepy.Client(
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
            consumer_key=os.getenv('TWITTER_API_KEY'),
            consumer_secret=os.getenv('TWITTER_API_SECRET'),
            access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
            access_token_secret=os.getenv('TWITTER_ACCESS_SECRET'),
            wait_on_rate_limit=True
        )
    
    def get_database_metrics(self) -> Dict:
        """Get metrics from database"""
        try:
            # Total readings
            result = self.db_session.execute(text("SELECT COUNT(*) FROM readings"))
            total_readings = result.scalar()
            
            # Viral tweets (engagement > 100)
            result = self.db_session.execute(
                text("SELECT COUNT(*) FROM readings WHERE engagement_score > 100")
            )
            viral_tweets = result.scalar()
            
            # Active users (last 24 hours)
            result = self.db_session.execute(
                text("""
                    SELECT COUNT(DISTINCT user_id) 
                    FROM readings 
                    WHERE created_at > NOW() - INTERVAL '24 hours'
                """)
            )
            active_users = result.scalar() or 0
            
            # Average engagement
            result = self.db_session.execute(
                text("SELECT AVG(engagement_score) FROM readings WHERE engagement_score > 0")
            )
            avg_engagement = result.scalar() or 0.0
            
            return {
                'total_readings': total_readings,
                'viral_tweets': viral_tweets,
                'active_users_24h': active_users,
                'average_engagement': round(avg_engagement, 2)
            }
            
        except Exception as e:
            logging.error(f"Database metrics error: {e}")
            return {}
    
    def get_redis_metrics(self) -> Dict:
        """Get metrics from Redis"""
        try:
            # Rate limiting stats
            rate_limited_users = len(self.redis_client.keys("rate_limit:*"))
            
            # Daily posts
            today = datetime.now().date()
            daily_posts = self.redis_client.get(f"daily_posts:{today}") or 0
            
            # Cache hit rate (if implemented)
            cache_keys = len(self.redis_client.keys("cache:*"))
            
            return {
                'rate_limited_users': rate_limited_users,
                'daily_posts': int(daily_posts),
                'cached_items': cache_keys
            }
            
        except Exception as e:
            logging.error(f"Redis metrics error: {e}")
            return {}
    
    async def check_recent_tweets_engagement(self) -> Dict:
        """Check engagement on recent tweets"""
        try:
            # Get recent tweet IDs from database
            result = self.db_session.execute(
                text("""
                    SELECT tweet_id 
                    FROM readings 
                    WHERE created_at > NOW() - INTERVAL '24 hours' 
                    AND tweet_id IS NOT NULL 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """)
            )
            
            tweet_ids = [row[0] for row in result.fetchall()]
            
            if not tweet_ids:
                return {'message': 'No recent tweets found'}
            
            engagement_data = []
            
            for tweet_id in tweet_ids:
                try:
                    tweet = self.twitter_client.get_tweet(
                        tweet_id,
                        tweet_fields=['public_metrics', 'created_at']
                    )
                    
                    if tweet.data:
                        metrics = tweet.data.public_metrics
                        engagement_data.append({
                            'tweet_id': tweet_id,
                            'likes': metrics['like_count'],
                            'retweets': metrics['retweet_count'],
                            'replies': metrics['reply_count'],
                            'total_engagement': (
                                metrics['like_count'] + 
                                metrics['retweet_count'] + 
                                metrics['reply_count']
                            )
                        })
                        
                        # Update database with engagement
                        self.db_session.execute(
                            text("""
                                UPDATE readings 
                                SET engagement_score = :score 
                                WHERE tweet_id = :tweet_id
                            """),
                            {
                                'score': metrics['like_count'] + metrics['retweet_count'] + metrics['reply_count'],
                                'tweet_id': tweet_id
                            }
                        )
                        
                except Exception as tweet_error:
                    logging.warning(f"Could not fetch engagement for tweet {tweet_id}: {tweet_error}")
            
            self.db_session.commit()
            
            return {
                'tweets_checked': len(engagement_data),
                'engagement_data': engagement_data,
                'total_engagement': sum(t['total_engagement'] for t in engagement_data)
            }
            
        except Exception as e:
            logging.error(f"Engagement check error: {e}")
            return {'error': str(e)}
    
    def get_top_performing_content(self) -> List[Dict]:
        """Get top performing tweets"""
        try:
            result = self.db_session.execute(
                text("""
                    SELECT reading_text, engagement_score, created_at, reading_type
                    FROM readings 
                    WHERE engagement_score > 0 
                    ORDER BY engagement_score DESC 
                    LIMIT 5
                """)
            )
            
            return [
                {
                    'content': row[0][:100] + '...' if len(row[0]) > 100 else row[0],
                    'engagement': row[1],
                    'date': row[2].strftime('%Y-%m-%d %H:%M'),
                    'type': row[3]
                }
                for row in result.fetchall()
            ]
            
        except Exception as e:
            logging.error(f"Top content error: {e}")
            return []
    
    def get_user_engagement_patterns(self) -> Dict:
        """Analyze user engagement patterns"""
        try:
            # Most active users
            result = self.db_session.execute(
                text("""
                    SELECT username, COUNT(*) as interaction_count
                    FROM readings 
                    WHERE username IS NOT NULL 
                    GROUP BY username 
                    ORDER BY interaction_count DESC 
                    LIMIT 5
                """)
            )
            
            top_users = [{'username': row[0], 'interactions': row[1]} for row in result.fetchall()]
            
            # Engagement by time of day
            result = self.db_session.execute(
                text("""
                    SELECT EXTRACT(hour FROM created_at) as hour, 
                           AVG(engagement_score) as avg_engagement
                    FROM readings 
                    WHERE engagement_score > 0 
                    GROUP BY EXTRACT(hour FROM created_at) 
                    ORDER BY hour
                """)
            )
            
            hourly_engagement = [
                {'hour': int(row[0]), 'avg_engagement': round(row[1], 2)} 
                for row in result.fetchall()
            ]
            
            return {
                'top_users': top_users,
                'hourly_engagement': hourly_engagement
            }
            
        except Exception as e:
            logging.error(f"User patterns error: {e}")
            return {}
    
    async def generate_report(self) -> Dict:
        """Generate comprehensive monitoring report"""
        print("🔮 Generating High Priestess Bot Report...")
        
        # Collect all metrics
        db_metrics = self.get_database_metrics()
        redis_metrics = self.get_redis_metrics()
        engagement_data = await self.check_recent_tweets_engagement()
        top_content = self.get_top_performing_content()
        user_patterns = self.get_user_engagement_patterns()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'database_metrics': db_metrics,
            'redis_metrics': redis_metrics,
            'recent_engagement': engagement_data,
            'top_performing_content': top_content,
            'user_patterns': user_patterns,
            'health_status': 'healthy' if db_metrics and redis_metrics else 'warning'
        }
        
        return report
    
    def print_dashboard(self, report: Dict):
        """Print a beautiful dashboard to console"""
        print("\n" + "="*60)
        print("🌙 HIGH PRIESTESS BOT - MONITORING DASHBOARD 🌙")
        print("="*60)
        print(f"📅 Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🏥 Health Status: {report['health_status'].upper()}")
        
        # Database metrics
        if report['database_metrics']:
            db = report['database_metrics']
            print(f"\n📊 DATABASE METRICS:")
            print(f"  📖 Total Readings: {db.get('total_readings', 0)}")
            print(f"  🔥 Viral Tweets: {db.get('viral_tweets', 0)}")
            print(f"  👥 Active Users (24h): {db.get('active_users_24h', 0)}")
            print(f"  📈 Avg Engagement: {db.get('average_engagement', 0)}")
        
        # Redis metrics
        if report['redis_metrics']:
            redis_data = report['redis_metrics']
            print(f"\n⚡ REDIS METRICS:")
            print(f"  🚫 Rate Limited Users: {redis_data.get('rate_limited_users', 0)}")
            print(f"  📝 Daily Posts: {redis_data.get('daily_posts', 0)}")
            print(f"  💾 Cached Items: {redis_data.get('cached_items', 0)}")
        
        # Recent engagement
        if report['recent_engagement'] and 'tweets_checked' in report['recent_engagement']:
            eng = report['recent_engagement']
            print(f"\n💫 RECENT ENGAGEMENT:")
            print(f"  🐦 Tweets Checked: {eng.get('tweets_checked', 0)}")
            print(f"  ❤️  Total Engagement: {eng.get('total_engagement', 0)}")
        
        # Top content
        if report['top_performing_content']:
            print(f"\n🏆 TOP PERFORMING CONTENT:")
            for i, content in enumerate(report['top_performing_content'][:3], 1):
                print(f"  {i}. [{content['engagement']} eng] {content['content']}")
        
        # User patterns
        if report['user_patterns'] and report['user_patterns'].get('top_users'):
            print(f"\n👑 TOP USERS:")
            for user in report['user_patterns']['top_users'][:3]:
                print(f"  @{user['username']}: {user['interactions']} interactions")
        
        print("\n" + "="*60)
        print("✨ May your metrics be ever in your favor ✨")
        print("="*60)
    
    async def run_monitoring_loop(self, interval: int = 300):
        """Run continuous monitoring"""
        print("🌙 Starting High Priestess Bot monitoring...")
        
        while True:
            try:
                report = await self.generate_report()
                self.print_dashboard(report)
                
                # Save report to file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                with open(f'logs/report_{timestamp}.json', 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                
                print(f"\n💾 Report saved to logs/report_{timestamp}.json")
                
            except Exception as e:
                logging.error(f"Monitoring error: {e}")
                print(f"❌ Monitoring error: {e}")
            
            print(f"\n⏰ Next check in {interval//60} minutes...")
            await asyncio.sleep(interval)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='High Priestess Bot Monitor')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--interval', type=int, default=300, help='Monitoring interval in seconds')
    
    args = parser.parse_args()
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    monitor = HighPriestessMonitor()
    
    if args.once:
        # Run once
        report = asyncio.run(monitor.generate_report())
        monitor.print_dashboard(report)
    else:
        # Run continuously
        asyncio.run(monitor.run_monitoring_loop(args.interval))
