# 🚀 WBS BPKH - Deployment Guide

Panduan deployment untuk production environment.

---

## 📋 Pre-Deployment Checklist

### System Requirements

- [ ] Server dengan Python 3.10+
- [ ] Minimum 2GB RAM
- [ ] 10GB storage space
- [ ] Internet connection untuk AI API
- [ ] SSL certificate untuk HTTPS

### Dependencies

- [ ] Python 3.10+
- [ ] pip
- [ ] Virtual environment support
- [ ] Groq API Key (production tier)

### Security

- [ ] Firewall configured
- [ ] SSL/TLS enabled
- [ ] Database encrypted
- [ ] API keys secured
- [ ] Access control configured

---

## 🐳 Docker Deployment (Recommended)

### 1. Create Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  wbs-bpkh:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./data:/app/data
      - ./wbs_database.db:/app/wbs_database.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 3. Build and Run

```bash
# Build image
docker build -t wbs-bpkh:latest .

# Run container
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop container
docker-compose down
```

---

## 🖥️ VM Deployment (Ubuntu/Debian)

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# Install nginx (reverse proxy)
sudo apt install nginx -y

# Install certbot (SSL)
sudo apt install certbot python3-certbot-nginx -y
```

### 2. Application Setup

```bash
# Create app directory
sudo mkdir -p /opt/wbs-bpkh
cd /opt/wbs-bpkh

# Clone/copy application files
sudo cp -r /path/to/wbs-bpkh-ai/* .

# Create virtual environment
sudo python3 -m venv venv

# Activate and install dependencies
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
sudo cp .env.example .env
sudo nano .env  # Edit dan tambahkan GROQ_API_KEY
```

### 3. Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/wbs-bpkh.service
```

Add:

```ini
[Unit]
Description=WBS BPKH AI Whistleblowing System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/wbs-bpkh
Environment="PATH=/opt/wbs-bpkh/venv/bin"
ExecStart=/opt/wbs-bpkh/venv/bin/streamlit run app.py --server.port=8501 --server.address=127.0.0.1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wbs-bpkh
sudo systemctl start wbs-bpkh
sudo systemctl status wbs-bpkh
```

### 4. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/wbs-bpkh
```

Add:

```nginx
server {
    listen 80;
    server_name wbs.bpkh.go.id;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/wbs-bpkh /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL Certificate

```bash
sudo certbot --nginx -d wbs.bpkh.go.id
```

---

## ☁️ Cloud Deployment

### AWS EC2

1. **Launch EC2 Instance**
   - Instance type: t3.medium (2 vCPU, 4GB RAM)
   - OS: Ubuntu 22.04 LTS
   - Security Group: Allow ports 80, 443, 22

2. **Connect and Setup**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   # Follow VM Deployment steps above
   ```

### Google Cloud Platform

1. **Create Compute Engine Instance**
   - Machine type: e2-medium
   - OS: Ubuntu 22.04 LTS
   - Firewall: Allow HTTP, HTTPS

2. **Deploy**
   ```bash
   gcloud compute ssh your-instance-name
   # Follow VM Deployment steps above
   ```

### Heroku

```bash
# Create Procfile
echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Create runtime.txt
echo "python-3.10.12" > runtime.txt

# Deploy
heroku create wbs-bpkh
git push heroku main
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Use environment variables for sensitive data
export GROQ_API_KEY="your-key"
export DB_PASSWORD="your-password"
```

### 2. Database Security

```bash
# Encrypt database file
sudo apt install sqlcipher

# Set permissions
chmod 600 wbs_database.db
chown www-data:www-data wbs_database.db
```

### 3. API Rate Limiting

Configure in `config.py`:

```python
RATE_LIMIT = {
    "max_requests_per_hour": 1000,
    "max_requests_per_day": 10000
}
```

### 4. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

---

## 📊 Monitoring

### 1. Application Logs

```bash
# View systemd logs
sudo journalctl -u wbs-bpkh -f

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Performance Monitoring

Install monitoring tools:

```bash
# htop for system monitoring
sudo apt install htop

# Prometheus + Grafana (advanced)
# Follow: https://prometheus.io/docs/introduction/first_steps/
```

### 3. Health Checks

Create monitoring script:

```bash
#!/bin/bash
# health_check.sh

curl -f http://localhost:8501/_stcore/health || \
    sudo systemctl restart wbs-bpkh
```

Add to crontab:

```bash
crontab -e
# Add:
*/5 * * * * /opt/wbs-bpkh/health_check.sh
```

---

## 🔄 Backup Strategy

### 1. Database Backup

```bash
# Create backup script
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/wbs-bpkh"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /opt/wbs-bpkh/wbs_database.db $BACKUP_DIR/wbs_db_$DATE.db

# Keep only last 30 days
find $BACKUP_DIR -name "wbs_db_*.db" -mtime +30 -delete
```

Schedule with cron:

```bash
0 2 * * * /opt/wbs-bpkh/backup.sh
```

### 2. Cloud Backup

```bash
# AWS S3
aws s3 sync /backup/wbs-bpkh s3://your-bucket/wbs-backups/

# Google Cloud Storage
gsutil -m rsync -r /backup/wbs-bpkh gs://your-bucket/wbs-backups/
```

---

## 🚨 Troubleshooting

### Application won't start

```bash
# Check service status
sudo systemctl status wbs-bpkh

# Check logs
sudo journalctl -u wbs-bpkh -n 50

# Restart service
sudo systemctl restart wbs-bpkh
```

### Database locked

```bash
# Check database integrity
sqlite3 wbs_database.db "PRAGMA integrity_check;"

# Fix if needed
sqlite3 wbs_database.db "VACUUM;"
```

### High memory usage

```bash
# Monitor memory
free -h
htop

# Restart application
sudo systemctl restart wbs-bpkh
```

---

## 📞 Support

For deployment issues, contact:

- **IT Support**: it@bpkh.go.id
- **Developer**: Audit Committee Members BPKH

---

## ✅ Post-Deployment Checklist

- [ ] Application accessible via HTTPS
- [ ] SSL certificate valid
- [ ] Database backups configured
- [ ] Monitoring setup
- [ ] Logs rotation configured
- [ ] Firewall rules applied
- [ ] Health checks running
- [ ] API keys secured
- [ ] Documentation updated
- [ ] Team trained on system

---

*Last Updated: December 2025*  
*WBS BPKH v2.0 - Production Ready*
