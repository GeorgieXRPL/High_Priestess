#!/usr/bin/env python3
"""
Quick test script to verify the fixes work
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_openai_fix():
    """Test if OpenAI API works with new syntax"""
    print("🧠 Testing OpenAI API fix...")
    
    try:
        from bot import HighPriestessBot
        
        bot = HighPriestessBot()
        
        # Test card drawing
        cards = bot.draw_cards(1, "general")
        print(f"✅ Cards drawn: {cards[0].get('name', cards[0].get('key', 'Unknown'))}")
        
        # Test reading generation
        context = {'type': 'test', 'question': 'Test reading'}
        reading = bot.generate_reading(cards, context)
        
        if reading and len(reading) > 10:
            print(f"✅ OpenAI API working: {reading[:50]}...")
            return True
        else:
            print("❌ OpenAI API failed - no reading generated")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False

def test_twitter_fix():
    """Test if Twitter API connection works"""
    print("\n🐦 Testing Twitter API fix...")
    
    try:
        from bot import HighPriestessBot
        
        bot = HighPriestessBot()
        user = bot.twitter_client.get_me(user_fields=['public_metrics'])
        
        if user and user.data:
            print(f"✅ Twitter connected: @{user.data.username}")
            return True
        else:
            print("❌ Twitter connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Twitter test failed: {e}")
        return False

def test_permissions():
    """Check Twitter app permissions"""
    print("\n🔐 Checking Twitter permissions...")
    
    try:
        from bot import HighPriestessBot
        
        bot = HighPriestessBot()
        
        # Try to get user info (read permission)
        user = bot.twitter_client.get_me()
        if user and user.data:
            print("✅ Read permissions: OK")
            
            # Note: We won't actually post, just check if we can create the request
            print("ℹ️  Write permissions: Need to be configured in Twitter Developer Portal")
            print("   Go to: https://developer.twitter.com/en/portal/dashboard")
            print("   Edit your app → App permissions → Read and Write")
            
            return True
        else:
            print("❌ No permissions to read user data")
            return False
            
    except Exception as e:
        print(f"❌ Permission test failed: {e}")
        return False

if __name__ == "__main__":
    print("🌙 Testing High Priestess Bot Fixes")
    print("=" * 40)
    
    success_count = 0
    total_tests = 3
    
    if test_openai_fix():
        success_count += 1
    
    if test_twitter_fix():
        success_count += 1
        
    if test_permissions():
        success_count += 1
    
    print("\n" + "=" * 40)
    print(f"🔮 Test Results: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("🎉 All fixes working! Your High Priestess is ready!")
    elif success_count >= 2:
        print("⚠️  Most fixes working. Check the failed test above.")
    else:
        print("❌ Multiple issues remain. Please check the errors above.")
    
    print("\n🌙 Ready to test with: python test_fixes.py")
