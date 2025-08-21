#!/usr/bin/env python3
"""
High Priestess Bot - Test Suite
Test all bot functionality before production deployment
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import bot components
try:
    from bot import HighPriestessBot
    from production_bot import HighPriestessBot as ProductionBot
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're in the correct directory and have installed requirements")
    sys.exit(1)

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotTester:
    """Test suite for High Priestess Bot"""
    
    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': []
        }
    
    def test_result(self, test_name: str, success: bool, message: str = ""):
        """Record test result"""
        if success:
            self.results['passed'] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.results['failed'] += 1
            self.results['errors'].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED {message}")
    
    def test_environment_variables(self):
        """Test that all required environment variables are set"""
        print("\n🔍 Testing Environment Variables...")
        
        required_vars = [
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET', 
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_SECRET',
            'TWITTER_BEARER_TOKEN',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            value = os.getenv(var)
            if not value or value == 'your_api_key_here':
                missing_vars.append(var)
        
        if missing_vars:
            self.test_result("Environment Variables", False, 
                           f"Missing or placeholder values: {', '.join(missing_vars)}")
        else:
            self.test_result("Environment Variables", True, "All required variables set")
    
    def test_file_structure(self):
        """Test that all required files exist"""
        print("\n📁 Testing File Structure...")
        
        required_files = [
            'system_prompt.md',
            'tarot_crypto_mapping.json',
            'requirements.txt',
            'bot.py',
            'production_bot.py'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            self.test_result("File Structure", False, 
                           f"Missing files: {', '.join(missing_files)}")
        else:
            self.test_result("File Structure", True, "All required files present")
    
    def test_tarot_data_loading(self):
        """Test tarot data can be loaded"""
        print("\n🃏 Testing Tarot Data Loading...")
        
        try:
            with open('tarot_crypto_mapping.json', 'r') as f:
                tarot_data = json.load(f)
            
            # Check structure
            required_keys = ['major_arcana', 'suits', 'reading_contexts']
            missing_keys = [key for key in required_keys if key not in tarot_data]
            
            if missing_keys:
                self.test_result("Tarot Data Loading", False, 
                               f"Missing keys: {', '.join(missing_keys)}")
            else:
                # Check if we have all 22 major arcana
                major_count = len(tarot_data['major_arcana'])
                if major_count == 22:
                    self.test_result("Tarot Data Loading", True, 
                                   f"Complete deck: {major_count} major arcana cards")
                else:
                    self.test_result("Tarot Data Loading", False, 
                                   f"Incomplete deck: only {major_count} major arcana cards")
                    
        except Exception as e:
            self.test_result("Tarot Data Loading", False, str(e))
    
    def test_bot_initialization(self):
        """Test bot can be initialized"""
        print("\n🤖 Testing Bot Initialization...")
        
        try:
            bot = HighPriestessBot()
            self.test_result("Bot Initialization", True, "Bot created successfully")
            
            # Test card drawing
            cards = bot.draw_cards(3)
            if len(cards) == 3:
                self.test_result("Card Drawing", True, f"Drew 3 cards: {[c.get('name', c.get('key', 'Unknown')) for c in cards]}")
            else:
                self.test_result("Card Drawing", False, f"Expected 3 cards, got {len(cards)}")
                
        except Exception as e:
            self.test_result("Bot Initialization", False, str(e))
    
    def test_twitter_connection(self):
        """Test Twitter API connection"""
        print("\n🐦 Testing Twitter API Connection...")
        
        try:
            bot = HighPriestessBot()
            
            # Test getting user info
            user = bot.twitter_client.get_me()
            if user and user.data:
                self.test_result("Twitter Connection", True, 
                               f"Connected as @{user.data.username}")
            else:
                self.test_result("Twitter Connection", False, "No user data returned")
                
        except Exception as e:
            self.test_result("Twitter Connection", False, str(e))
    
    def test_openai_connection(self):
        """Test OpenAI API connection"""
        print("\n🧠 Testing OpenAI API Connection...")
        
        try:
            bot = HighPriestessBot()
            
            # Test simple generation
            cards = [{"name": "The Fool", "crypto_metaphor": "New investor entering crypto"}]
            context = {"type": "test", "question": "Test reading"}
            
            reading = bot.generate_reading(cards, context)
            
            if reading and len(reading) > 10:
                self.test_result("OpenAI Connection", True, 
                               f"Generated reading: {reading[:50]}...")
            else:
                self.test_result("OpenAI Connection", False, "No reading generated")
                
        except Exception as e:
            self.test_result("OpenAI Connection", False, str(e))
    
    def test_production_bot(self):
        """Test production bot features"""
        print("\n🏭 Testing Production Bot...")
        
        try:
            prod_bot = ProductionBot()
            self.test_result("Production Bot Init", True, "Production bot initialized")
            
            # Test health check
            health = asyncio.run(prod_bot.health_check())
            if health.get('status') == 'healthy':
                self.test_result("Health Check", True, "Health check passed")
            else:
                self.test_result("Health Check", False, f"Health status: {health.get('status')}")
                
        except Exception as e:
            self.test_result("Production Bot", False, str(e))
    
    def test_docker_setup(self):
        """Test Docker configuration"""
        print("\n🐳 Testing Docker Setup...")
        
        docker_files = ['Dockerfile', 'docker-compose.yml']
        missing_docker_files = [f for f in docker_files if not os.path.exists(f)]
        
        if missing_docker_files:
            self.test_result("Docker Setup", False, 
                           f"Missing Docker files: {', '.join(missing_docker_files)}")
        else:
            self.test_result("Docker Setup", True, "Docker files present")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🌙 High Priestess Bot - Test Suite")
        print("=" * 50)
        
        # Run tests
        self.test_environment_variables()
        self.test_file_structure()
        self.test_tarot_data_loading()
        self.test_bot_initialization()
        self.test_twitter_connection()
        self.test_openai_connection()
        self.test_production_bot()
        self.test_docker_setup()
        
        # Print results
        print("\n" + "=" * 50)
        print("🔮 Test Results Summary")
        print("=" * 50)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['errors']:
            print("\n🚨 Errors to fix:")
            for error in self.results['errors']:
                print(f"  • {error}")
        
        if self.results['failed'] == 0:
            print("\n🎉 All tests passed! Your High Priestess is ready for production! 🌙")
            print("\nNext steps:")
            print("1. Run: ./deploy.sh")
            print("2. Monitor logs: docker-compose logs -f high-priestess-bot")
            print("3. Check health: curl http://localhost:8000/health")
            return True
        else:
            print("\n⚠️  Please fix the errors above before deploying to production.")
            return False

if __name__ == "__main__":
    tester = BotTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
