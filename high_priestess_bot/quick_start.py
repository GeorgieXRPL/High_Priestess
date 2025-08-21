#!/usr/bin/env python3
"""
High Priestess Bot - Quick Start Script
Simple way to test the bot without full Docker setup
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Simple logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_requirements():
    """Check if basic requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check environment variables
    required_vars = [
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET', 
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_SECRET',
        'TWITTER_BEARER_TOKEN',
        'OPENAI_API_KEY'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value in ['your_api_key_here', 'your_access_token_here']:
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("Please update your .env file with real API keys")
        return False
    
    print("✅ Environment variables configured")
    
    # Check required files
    required_files = ['system_prompt.md', 'tarot_crypto_mapping.json']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("✅ Required files present")
    return True

async def test_single_reading():
    """Generate and display a single reading"""
    print("\n🔮 Testing single reading generation...")
    
    try:
        # Import here to avoid issues if requirements not met
        from bot import HighPriestessBot
        
        bot = HighPriestessBot()
        
        # Draw cards
        cards = bot.draw_cards(3, "general")
        print(f"📇 Cards drawn: {[c.get('name', c.get('key', 'Unknown')) for c in cards]}")
        
        # Generate reading
        context = {
            'type': 'test',
            'question': 'What does the future hold for this bot?'
        }
        
        reading = bot.generate_reading(cards, context)
        print(f"\n🌙 Generated reading:")
        print(f"'{reading}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Reading generation failed: {e}")
        return False

async def test_twitter_connection():
    """Test Twitter API connection"""
    print("\n🐦 Testing Twitter API connection...")
    
    try:
        from bot import HighPriestessBot
        
        bot = HighPriestessBot()
        user = bot.twitter_client.get_me(user_fields=['public_metrics'])
        
        if user and user.data:
            print(f"✅ Connected to Twitter as @{user.data.username}")
            if hasattr(user.data, 'public_metrics') and user.data.public_metrics:
                print(f"   Followers: {user.data.public_metrics.get('followers_count', 'Unknown')}")
            else:
                print(f"   Account verified and accessible")
            return True
        else:
            print("❌ Twitter connection failed - no user data")
            return False
            
    except Exception as e:
        print(f"❌ Twitter connection failed: {e}")
        return False

async def post_test_reading():
    """Post a test reading to Twitter"""
    print("\n📤 Posting test reading...")
    
    try:
        from bot import HighPriestessBot
        
        bot = HighPriestessBot()
        
        # Generate test reading
        cards = bot.draw_cards(1, "general")
        context = {
            'type': 'test',
            'question': 'Testing the High Priestess bot'
        }
        
        reading = bot.generate_reading(cards, context)
        
        # Add test prefix
        test_reading = f"🧪 [TEST] {reading}"
        
        print(f"Posting: {test_reading}")
        
        # Confirm with user
        confirm = input("\nDo you want to post this test reading? (y/N): ").lower()
        if confirm != 'y':
            print("Test post cancelled")
            return False
        
        # Post tweet
        response = bot.twitter_client.create_tweet(text=test_reading)
        
        if response and response.data:
            tweet_id = response.data['id']
            print(f"✅ Test reading posted successfully!")
            print(f"   Tweet ID: {tweet_id}")
            print(f"   URL: https://twitter.com/user/status/{tweet_id}")
            return True
        else:
            print("❌ Failed to post tweet")
            return False
            
    except Exception as e:
        print(f"❌ Test post failed: {e}")
        return False

def show_menu():
    """Show interactive menu"""
    print("\n🌙 HIGH PRIESTESS BOT - QUICK START MENU")
    print("=" * 45)
    print("1. Check requirements")
    print("2. Test reading generation")
    print("3. Test Twitter connection")
    print("4. Post test reading")
    print("5. Run full test suite")
    print("6. Start bot (basic mode)")
    print("0. Exit")
    print("=" * 45)

async def run_basic_bot():
    """Run bot in basic mode (SQLite, no Docker)"""
    print("\n🚀 Starting High Priestess Bot in basic mode...")
    print("Press Ctrl+C to stop")
    
    try:
        from bot import HighPriestessBot
        
        # Override database URL for local testing
        os.environ['DATABASE_URL'] = 'sqlite:///high_priestess.db'
        
        bot = HighPriestessBot()
        
        print("✅ Bot initialized successfully")
        print("🔮 The High Priestess is now listening for mentions...")
        print("📊 Monitoring at: http://localhost:8000 (if FastAPI is running)")
        
        # Run the bot
        await bot.run()
        
    except KeyboardInterrupt:
        print("\n🌙 High Priestess bot stopped gracefully")
    except Exception as e:
        print(f"❌ Bot error: {e}")

async def main():
    """Main interactive menu"""
    print("🌙 Welcome to the High Priestess Bot Quick Start!")
    print("This tool helps you test and run the bot without Docker")
    
    while True:
        show_menu()
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '0':
            print("🌙 May your code be blessed and your APIs forever stable!")
            break
            
        elif choice == '1':
            check_requirements()
            
        elif choice == '2':
            await test_single_reading()
            
        elif choice == '3':
            await test_twitter_connection()
            
        elif choice == '4':
            await post_test_reading()
            
        elif choice == '5':
            print("\n🧪 Running full test suite...")
            os.system('python test_bot.py')
            
        elif choice == '6':
            if check_requirements():
                await run_basic_bot()
            else:
                print("❌ Requirements not met. Please fix issues first.")
                
        else:
            print("❌ Invalid choice. Please try again.")
        
        if choice != '0':
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🌙 Goodbye, seeker of digital wisdom!")
