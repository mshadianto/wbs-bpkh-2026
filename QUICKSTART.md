# ⚡ Quick Start Guide

Get WBS BPKH up and running in 5 minutes!

---

## 🚀 The Fastest Way

### For Windows:

1. **Extract ZIP file**
   ```
   Right-click wbs-bpkh-ai.zip → Extract All
   ```

2. **Double-click** `run.bat`

3. **Done!** Browser akan terbuka otomatis di `http://localhost:8501`

### For Mac/Linux:

1. **Extract ZIP file**
   ```bash
   unzip wbs-bpkh-ai.zip
   cd wbs-bpkh-ai
   ```

2. **Run launcher**
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

3. **Done!** Buka browser di `http://localhost:8501`

---

## 📝 Manual Installation

If launcher scripts don't work, follow these steps:

### Step 1: Install Python

Download Python 3.10+ from: https://www.python.org/downloads/

**Verify installation:**
```bash
python --version  # Should show Python 3.10 or higher
```

### Step 2: Install Dependencies

```bash
# Navigate to project directory
cd wbs-bpkh-ai

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure (Optional)

**For AI Features (Recommended):**

1. Get free Groq API key: https://console.groq.com
2. Copy `.env.example` to `.env`
3. Edit `.env` and add your API key:
   ```
   GROQ_API_KEY=gsk_your_actual_key_here
   ```

**Without API key:** System akan tetap berfungsi dengan rule-based processing (tanpa AI)

### Step 4: Run Application

```bash
streamlit run app.py
```

Browser akan terbuka otomatis. Jika tidak, buka: http://localhost:8501

---

## 🎯 First Steps

### 1. Submit Your First Report

1. Click **"Submit Report"** di sidebar
2. Fill in the form:
   - **What**: Judul dan deskripsi kejadian
   - **Who**: Nama terlapor
   - **When**: Tanggal kejadian
   - **Where**: Lokasi
   - **How**: Evidence/bukti
3. Click **"Submit Report"**
4. See AI processing in real-time!

### 2. View Results

After submission, you'll see:
- ✅ Executive summary
- 🏷️ Violation classification
- 🎯 Unit routing
- 🔍 Investigation plan
- ✅ Compliance score

### 3. Explore Dashboard

Click **"Dashboard & Analytics"** to see:
- Total reports
- Performance metrics
- Violation distribution
- Compliance trends

### 4. Search Reports

Click **"Report Database"** to:
- Search by keyword
- Filter by severity
- View all reports
- Export to CSV

---

## ❓ Troubleshooting

### Problem: Python not found

**Solution:**
```bash
# Make sure Python is in PATH
# Windows: Add Python to PATH during installation
# Mac: brew install python3
# Linux: sudo apt install python3
```

### Problem: Module not found error

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Problem: Port 8501 already in use

**Solution:**
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Problem: Database error

**Solution:**
```bash
# Delete old database and restart
rm wbs_database.db
streamlit run app.py
```

---

## 🆘 Need Help?

### Common Questions

**Q: Do I need Groq API key?**  
A: No, it's optional. System works without it using rule-based processing. With API key, you get full AI capabilities.

**Q: Is my data safe?**  
A: Yes! All data is stored locally in SQLite database. Whistleblower identity is protected.

**Q: Can I use this for production?**  
A: Yes! See DEPLOYMENT.md for production setup guide.

**Q: How to add more users?**  
A: Currently single-user. For multi-user setup, see DEPLOYMENT.md for authentication options.

---

## 📚 Next Steps

1. ✅ Read [README.md](README.md) for detailed documentation
2. ✅ See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
3. ✅ Check [CHANGELOG.md](CHANGELOG.md) for version history
4. ✅ Review [LICENSE](LICENSE) for usage terms

---

## 📞 Support

**Email**: it@bpkh.go.id  
**WhatsApp**: 085319000230 / 085319000140  
**Web**: portal.bpkh.go.id/wbs

---

## 🎉 You're Ready!

Start protecting BPKH with AI-powered whistleblowing system!

**🛡️ Protecting the Trust of Indonesian Pilgrims**

---

*Last Updated: December 29, 2025*
