-- High Priestess Bot Database Initialization

-- Create database extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_readings_tweet_id ON readings(tweet_id);
CREATE INDEX IF NOT EXISTS idx_readings_user_id ON readings(user_id);
CREATE INDEX IF NOT EXISTS idx_readings_created_at ON readings(created_at);
CREATE INDEX IF NOT EXISTS idx_readings_engagement_score ON readings(engagement_score);
CREATE INDEX IF NOT EXISTS idx_readings_reading_type ON readings(reading_type);

-- Create additional tables for analytics
CREATE TABLE IF NOT EXISTS user_interactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    username VARCHAR(50),
    interaction_type VARCHAR(20) NOT NULL, -- 'mention', 'reply', 'like', 'retweet'
    tweet_id VARCHAR(50),
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS bot_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(50) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS viral_tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(50) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    engagement_count INTEGER DEFAULT 0,
    retweet_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    went_viral_at TIMESTAMP
);

-- Create indexes for new tables
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_created_at ON user_interactions(created_at);
CREATE INDEX IF NOT EXISTS idx_bot_metrics_date ON bot_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_viral_tweets_engagement ON viral_tweets(engagement_count);

-- Insert initial bot metrics
INSERT INTO bot_metrics (metric_name, metric_value) VALUES 
('total_readings', 0),
('viral_tweets', 0),
('active_users', 0),
('engagement_rate', 0.0)
ON CONFLICT DO NOTHING;
