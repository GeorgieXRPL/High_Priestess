# 🌊 High Priestess Bot - DigitalOcean Deployment

## 🚀 **Quick Setup Guide**

### **Step 1: Create DigitalOcean Droplet**

1. **Log into DigitalOcean Dashboard**
2. **Create Droplet:**
   - **OS**: Ubuntu 24.04 LTS
   - **Plan**: Basic ($4-6/month)
   - **Size**: 1GB RAM / 1 CPU
   - **Datacenter**: Choose closest region
   - **Authentication**: SSH Key (recommended)
   - **Hostname**: `high-priestess-oracle`

### **Step 2: Connect to Your Droplet**

```bash
# SSH into your droplet (replace with your IP)
ssh root@your_droplet_ip

# Or if using a user account:
ssh your_username@your_droplet_ip
```

### **Step 3: Run Automated Setup**

```bash
# Download and run the deployment script
curl -fsSL https://raw.githubusercontent.com/GeorgieXRPL/High_Priestess/main/high_priestess_bot/deploy_digitalocean.sh -o deploy.sh
chmod +x deploy.sh
./deploy.sh
```

### **Step 4: Deploy Your Bot**

```bash
# Navigate to application directory
cd /opt/high-priestess

# Clone your repository
git clone https://github.com/GeorgieXRPL/High_Priestess.git .

# Navigate to bot directory
cd high_priestess_bot

# Create your .env file
nano .env
```

**Add your environment variables:**
```env
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
OPENAI_API_KEY=your_openai_key_here
BOT_USERNAME=HP_Selene
```

### **Step 5: Start Your Bot**

```bash
# Start the High Priestess bot
sudo systemctl start high-priestess

# Start the web dashboard (optional)
sudo systemctl start high-priestess-web

# Check if everything is running
sudo systemctl status high-priestess
sudo systemctl status high-priestess-web

# Test the health endpoint
curl http://localhost/health
```

### **Step 6: Monitor Your Bot**

```bash
# View bot logs
sudo journalctl -u high-priestess -f

# View web dashboard logs
sudo journalctl -u high-priestess-web -f

# Restart if needed
sudo systemctl restart high-priestess
```

## 🔧 **Management Commands**

### **Check Status**
```bash
sudo systemctl status high-priestess
curl http://your_droplet_ip/health
```

### **View Logs**
```bash
# Live logs
sudo journalctl -u high-priestess -f

# Last 100 lines
sudo journalctl -u high-priestess -n 100
```

### **Update Bot**
```bash
cd /opt/high-priestess
git pull origin main
sudo systemctl restart high-priestess
sudo systemctl restart high-priestess-web
```

### **Stop/Start Bot**
```bash
sudo systemctl stop high-priestess
sudo systemctl start high-priestess
```

## 📊 **Monitoring**

### **Health Check**
Your bot will be accessible at:
- **Health**: `http://your_droplet_ip/health`
- **Dashboard**: `http://your_droplet_ip/`

### **Set Up Domain (Optional)**
1. Point your domain to your droplet IP
2. Update Nginx config with your domain
3. Set up SSL with Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

## 🛡️ **Security Best Practices**

### **Firewall Setup**
```bash
# Enable UFW firewall
sudo ufw enable

# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Check status
sudo ufw status
```

### **Regular Updates**
```bash
# Set up automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 🔮 **Troubleshooting**

### **Bot Not Starting**
```bash
# Check logs for errors
sudo journalctl -u high-priestess -n 50

# Check if all files are present
ls -la /opt/high-priestess/high_priestess_bot/

# Verify environment variables
sudo systemctl show high-priestess --property=Environment
```

### **Twitter API Issues**
```bash
# Test Twitter connection manually
cd /opt/high-priestess/high_priestess_bot
source /opt/high-priestess/venv/bin/activate
python test_fixes.py
```

### **OpenAI API Issues**
- Check your OpenAI API key is valid
- Verify you have credits available
- Check rate limits in OpenAI dashboard

## 💰 **Cost Optimization**

### **Basic Droplet ($4/month)**
- 1GB RAM / 1 CPU
- Perfect for the High Priestess bot
- 25GB SSD storage

### **Monitoring Costs**
- **Bandwidth**: ~1GB/month (well within limits)
- **CPU**: Very low usage (posting 3x/day)
- **Storage**: <1GB for logs and database

## 🌙 **Success!**

Once deployed, your High Priestess bot will:
- ✅ **Post automatically** 3x daily (Dawn, Twilight, Witching Hour)
- ✅ **Respond to mentions** with personalized readings
- ✅ **Run 24/7** with automatic restarts
- ✅ **Generate mystical content** using AI
- ✅ **Track moon phases** for special readings
- ✅ **Subtly promote Heaven.xyz** every ~15 tweets

**Your mystical oracle is now immortal in the cloud!** 🔮✨

## 📞 **Support**

If you encounter issues:
1. Check the logs: `sudo journalctl -u high-priestess -f`
2. Verify your .env file has all required variables
3. Test individual components with `python test_fixes.py`
4. Restart services: `sudo systemctl restart high-priestess`

*"The High Priestess dwells not just in cards, but in the eternal cloud, spreading wisdom across the digital realm."* 🌙
