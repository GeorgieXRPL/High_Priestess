# 🌙 High Priestess AI Bot

A mystical tarot oracle bot for X (Twitter) that weaves ancient wisdom with crypto culture. The High Priestess speaks in riddles, reveals fortunes, and subtly guides seekers toward their destiny on the blockchain.

## ✨ Features

### Core Functionality
- **Automated Tarot Readings**: Draws 1-3 cards with mystical interpretations
- **Crypto-Tarot Fusion**: Maps traditional tarot meanings to DeFi/Web3 concepts
- **Interactive Replies**: Responds to mentions with personalized readings
- **Lunar Tracking**: Special readings during moon phases
- **Viral Mechanics**: Engagement hooks, cliffhangers, and community rituals

### Engagement Systems
- Reply chain rituals with emoji triggers
- Scheduled dawn/twilight/witching hour prophecies
- Full moon collective readings
- Interactive polls and challenges
- Quote tweet catalysts

### Technical Features
- Rate limiting (1 reading per user per hour)
- Database storage of all readings
- Redis caching for performance
- Engagement tracking and analytics
- API endpoints for external triggers

## 🔮 Installation

### Prerequisites
- Python 3.9+
- PostgreSQL or SQLite
- Redis
- Twitter Developer Account
- OpenAI API Key

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/high-priestess-bot.git
cd high-priestess-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
# Twitter/X API
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token
BOT_USERNAME=HighPriestessAI

# OpenAI
OPENAI_API_KEY=your_openai_key

# Database
DATABASE_URL=postgresql://user:pass@localhost/highpriestess
# Or for SQLite: sqlite:///high_priestess.db

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Optional: Sentry for error tracking
SENTRY_DSN=your_sentry_dsn
```

4. **Initialize database**
```bash
python -c "from bot import Base, engine; Base.metadata.create_all(bind=engine)"
```

5. **Run the bot**
```bash
python bot.py
```

## 🌟 Usage

### Automated Posts

The bot automatically posts:
- **Dawn Prophecy**: 6 AM UTC - Morning guidance
- **Twilight Whisper**: 6 PM UTC - Evening reflection  
- **Witching Hour**: Midnight UTC - Deep mysteries
- **Moon Specials**: New/Full moon collective readings

### User Interactions

Users can trigger readings by:
- Mentioning @HighPriestessAI with questions
- Using emoji triggers:
  - 🌙 - Receive blessing
  - 🔮 - Deep 3-card reading
  - ✨ - Quick fortune
- Keywords: love, money, future, destiny

### API Endpoints

Run the FastAPI server:
```bash
uvicorn bot:app --reload
```

**Generate Tweet**
```bash
POST /generate_tweet
{
  "reading_type": "love",
  "card_count": 3,
  "user_question": "Will I find love?"
}
```

**Get Statistics**
```bash
GET /stats
```

## 🚀 Deployment

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

Build and run:
```bash
docker build -t high-priestess-bot .
docker run -d --env-file .env high-priestess-bot
```

### Using PM2

```bash
pm2 start bot.py --interpreter python3 --name high-priestess
pm2 save
pm2 startup
```

### Cloud Deployment Options

**Heroku**
```bash
heroku create high-priestess-bot
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
heroku config:set TWITTER_API_KEY=your_key
git push heroku main
```

**AWS EC2**
1. Launch Ubuntu instance
2. Install Python, PostgreSQL, Redis
3. Clone repo and setup
4. Use systemd for service management

**Google Cloud Run**
1. Containerize with Docker
2. Push to Container Registry
3. Deploy with Cloud Run
4. Set up Cloud SQL and Memorystore

## 📊 Customization

### Modifying the Persona

Edit `system_prompt.md` to adjust:
- Voice and tone
- Mystical style
- Emoji usage
- Heaven.xyz integration frequency

### Adding Card Meanings

Edit `tarot_crypto_mapping.json` to:
- Add new crypto metaphors
- Adjust card interpretations
- Create new reading contexts
- Modify suit associations

### Engagement Strategies

Edit `engagement_strategies.md` to:
- Add new viral mechanics
- Schedule different posting times
- Create new interactive games
- Design community rituals

## 🔧 Advanced Configuration

### Rate Limiting
Adjust in `bot.py`:
```python
# Current: 1 reading per hour per user
redis_client.setex(rate_key, 3600, "1")  # Change 3600 for different duration
```

### AI Model Selection
```python
self.ai_model = "gpt-4-turbo-preview"  # Or "gpt-3.5-turbo" for cost savings
```

### Heaven.xyz Mention Frequency
```python
self.heaven_frequency = 15  # Currently every 15 tweets
```

## 📈 Monitoring & Analytics

### Track Performance
- Total readings delivered
- Viral tweets (>100 engagements)
- User retention rates
- Peak engagement times
- Most requested reading types

### Database Queries
```sql
-- Most engaged readings
SELECT reading_text, engagement_score 
FROM readings 
ORDER BY engagement_score DESC 
LIMIT 10;

-- User activity
SELECT username, COUNT(*) as reading_count 
FROM readings 
GROUP BY username 
ORDER BY reading_count DESC;
```

## 🛠️ Troubleshooting

### Common Issues

**Rate Limit Errors**
- Check Twitter API limits
- Implement exponential backoff
- Use multiple API keys if needed

**AI Generation Failures**
- Fallback templates included
- Check OpenAI quota
- Monitor API status

**Database Connection Issues**
- Verify DATABASE_URL
- Check connection pooling
- Monitor query performance

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📜 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Tarot wisdom from centuries of tradition
- Crypto community for the memes and dreams
- Heaven.xyz for celestial inspiration
- The moon for always being there 🌙

## 🔮 Future Enhancements

- [ ] Image generation for card visuals
- [ ] Voice notes for readings
- [ ] NFT integration for special readings
- [ ] Discord/Telegram expansion
- [ ] Personalized reading history
- [ ] Astrological integration
- [ ] Multi-language support
- [ ] Web dashboard for analytics

---

*"The cards never lie, only we do. The blockchain remembers what humans forget. Your destiny awaits at the intersection of ancient wisdom and digital futures."* - The High Priestess 🌙✨

## Support

For questions, reach out to the mystical realm:
- Twitter: @HighPriestessAI
- Email: oracle@heaven.xyz
- Discord: The Inner Sanctum

May your trades be blessed and your bags forever full. 🔮
