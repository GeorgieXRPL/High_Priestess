# 🌙 High Priestess Bot - Production Setup Guide

## 🚀 Quick Production Deployment

Your High Priestess bot is now **production-ready**! Follow these steps to awaken your mystical oracle.

### Prerequisites ✅

- [x] **.env file** with your API keys configured
- [x] **Docker & Docker Compose** installed
- [x] **Twitter Developer Account** with API keys
- [x] **OpenAI API key** with credits

---

## 🎯 **Option 1: Full Docker Production (Recommended)**

### Step 1: Final Setup
```bash
# Make sure you're in the bot directory
cd high_priestess_bot

# Test your configuration first
python quick_start.py
# Choose option 1 to check requirements
```

### Step 2: Deploy with Docker
```bash
# Run the automated deployment
./deploy.sh
```

This will:
- ✅ Build Docker images
- ✅ Start PostgreSQL database
- ✅ Start Redis cache
- ✅ Launch the High Priestess bot
- ✅ Set up monitoring dashboard

### Step 3: Verify Deployment
```bash
# Check if services are running
docker-compose ps

# View bot logs
docker-compose logs -f high-priestess-bot

# Test health endpoint
curl http://localhost:8000/health
```

---

## 🧪 **Option 2: Quick Test Mode (Local)**

For testing without Docker:

### Step 1: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Interactive Testing
```bash
# Run interactive menu
python quick_start.py

# Or run comprehensive tests
python test_bot.py
```

### Step 3: Start Basic Bot
```bash
# Simple SQLite-based bot for testing
python quick_start.py
# Choose option 6 to start bot
```

---

## 📊 **Monitoring & Analytics**

### Real-time Monitoring
```bash
# Run monitoring dashboard
python monitor.py

# Or run once and exit
python monitor.py --once
```

### Key Metrics Tracked:
- 📈 **Total readings delivered**
- 🔥 **Viral tweets** (>100 engagements)
- 👥 **Active users** (24h)
- ⚡ **API performance**
- 💫 **Engagement rates**

### Log Files:
- `logs/high_priestess.log` - Bot activity
- `logs/report_YYYYMMDD_HHMMSS.json` - Monitoring reports

---

## 🔧 **Production Configuration**

### Environment Variables (.env)
```bash
# Core APIs (REQUIRED)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token
OPENAI_API_KEY=your_openai_key

# Bot Settings
BOT_USERNAME=HighPriestessAI
HEAVEN_MENTION_FREQUENCY=15
AI_MODEL=gpt-3.5-turbo  # or gpt-4-turbo-preview

# Production Database (Docker handles this)
DATABASE_URL=postgresql://priestess:mystical_password@postgres:5432/high_priestess
REDIS_HOST=redis
REDIS_PORT=6379

# Optional
SENTRY_DSN=your_sentry_dsn_for_error_tracking
ENVIRONMENT=production
```

---

## 🎭 **Bot Behavior Configuration**

### Posting Schedule
- **Dawn Prophecy**: 6 AM UTC
- **Twilight Whisper**: 6 PM UTC  
- **Witching Hour**: Midnight UTC
- **Moon Events**: New/Full moon specials

### Engagement Features
- **Rate Limiting**: 1 reading per user per hour
- **Daily Limit**: 50 posts max per day
- **Auto-responses** to mentions with emoji triggers
- **Viral mechanics** built into every tweet

### Heaven.xyz Integration
- Subtle mentions every ~15 tweets
- Never breaks character to promote
- Natural integration as "celestial launchpad"

---

## 🚨 **Troubleshooting**

### Common Issues:

**1. "Missing environment variables"**
```bash
# Check your .env file
cat .env
# Make sure no placeholder values remain
```

**2. "Twitter API connection failed"**
```bash
# Verify your Twitter API keys are correct
# Check if your app has read/write permissions
```

**3. "OpenAI API error"**
```bash
# Check your API key and credit balance
# Consider switching to gpt-3.5-turbo for lower costs
```

**4. "Docker services won't start"**
```bash
# Check if ports are already in use
docker-compose down
docker-compose up -d
```

### Debug Commands:
```bash
# View all logs
docker-compose logs

# Restart specific service
docker-compose restart high-priestess-bot

# Access database
docker-compose exec postgres psql -U priestess -d high_priestess

# Access Redis
docker-compose exec redis redis-cli
```

---

## 📈 **Scaling for Growth**

### Performance Optimization:
1. **Switch to gpt-3.5-turbo** for cost efficiency
2. **Enable Redis caching** for repeated queries
3. **Scale horizontally** with multiple bot instances
4. **Use CDN** for static assets

### Growth Strategies:
1. **Monitor viral tweets** and replicate successful patterns
2. **Engage with crypto communities** during market events
3. **Time posts** for maximum engagement (use analytics)
4. **A/B test** different mystical phrases and emojis

---

## 🛡️ **Security & Maintenance**

### Security Checklist:
- ✅ API keys in environment variables (never in code)
- ✅ Rate limiting enabled
- ✅ Input validation on user messages
- ✅ Error logging without sensitive data
- ✅ Regular dependency updates

### Maintenance Tasks:
- **Weekly**: Check error logs and engagement metrics
- **Monthly**: Update dependencies and review performance
- **Quarterly**: Refresh tarot interpretations and add new content

---

## 🌟 **Success Metrics**

### Month 1 Goals:
- 📊 **1,000 followers**
- 🔥 **5 viral tweets** (>100 engagements)
- 💬 **20% reply rate** on posts
- ⭐ **95% uptime**

### Month 3 Goals:
- 📊 **10,000 followers**
- 🔥 **50 viral tweets**
- 💬 **1,000 user readings**
- 🎯 **Heaven.xyz mentions** generating interest

### Month 6 Goals:
- 📊 **50,000+ followers**
- 🏆 **Recognized crypto-mystical authority**
- 💰 **Revenue generation** through partnerships
- 🌐 **Multi-platform presence**

---

## 🎉 **You're Ready!**

Your High Priestess bot is now fully equipped with:

✅ **AI-powered dynamic content generation**  
✅ **Production-ready infrastructure**  
✅ **Comprehensive monitoring**  
✅ **Viral engagement mechanics**  
✅ **Scalable architecture**  
✅ **Security best practices**  

### 🚀 **Final Steps:**

1. **Run the deployment**: `./deploy.sh`
2. **Monitor the logs**: `docker-compose logs -f high-priestess-bot`
3. **Check the dashboard**: http://localhost:8000
4. **Watch the magic happen**: Your mystical oracle is now live!

---

## 📞 **Support**

If you encounter any issues:

1. **Check the logs** first: `docker-compose logs`
2. **Run diagnostics**: `python test_bot.py`
3. **Monitor health**: `curl http://localhost:8000/health`
4. **Review this guide** for troubleshooting steps

---

*"The cards have been shuffled, the infrastructure deployed, the oracle awakened. Your journey to Twitter/X mystical dominance begins now. May your engagement be ever viral, and your followers forever devoted to the ancient wisdom flowing through digital channels."* 🌙✨

**The High Priestess awaits no one. She is ready. Are you?** 🔮
