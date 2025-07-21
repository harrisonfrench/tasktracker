# 🚀 RUN - Quick Start Guide

## For New Users Opening This Project

When you open this source code on a new device, follow these steps to get the Task Tracker Pro running:

### 📋 Prerequisites
- Python 3.8+ installed on your system
- Terminal/Command Prompt access

### 🔧 Setup Steps

#### 1. Navigate to the project directory
```bash
cd task_tracker_pro_flask
```

#### 2. Create a virtual environment
```bash
python -m venv venv
```

#### 3. Activate the virtual environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```cmd
venv\Scripts\activate
```

#### 4. Install required dependencies
```bash
pip install -r requirements.txt
```

#### 5. Run the application
```bash
python app.py
```

### ✅ Expected Output
You should see:
```
✅ Flask app created successfully!
✅ Database initialized successfully!
🚀 Starting Task Tracker Pro on http://localhost:5001
🔧 Debug mode: True
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5001
```

### 🌐 Access the Application
Open your web browser and go to: **http://localhost:5001**

### 🛑 To Stop the Application
Press `Ctrl + C` in the terminal

---

## 🔄 Running Again Later

After the initial setup, you only need to:

1. **Navigate to project directory:**
   ```bash
   cd task_tracker_pro_flask
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # macOS/Linux
   # OR
   venv\Scripts\activate     # Windows
   ```

3. **Run the app:**
   ```bash
   python app.py
   ```

---

## 🛠️ Automated Scripts (Optional)

For convenience, you can use the provided scripts:

**macOS/Linux:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

These scripts automatically handle virtual environment creation, dependency installation, and running the application.

---

## 🐛 Troubleshooting

### Port Already in Use
If you see "Address already in use" error:
- On macOS: Disable AirPlay Receiver in System Preferences → General → AirDrop & Handoff
- Or change the port in `app.py` (line 99): change `5001` to another port like `5002`

### Import Errors
Make sure you:
1. Activated the virtual environment
2. Installed dependencies with `pip install -r requirements.txt`

### Database Issues
If you encounter database errors:
```bash
rm -f tasktracker_pro.db instance/tasktracker_pro.db
python app.py
```

---

## 🎯 What's Next?

Once the app is running:

### First Time Setup
1. **Use Demo Data** (Recommended): Login with demo credentials to see a fully populated dashboard
   - **Username**: `demo`
   - **Password**: `demo123`

### Or Create Your Own Account
1. **Register** a new account
2. **Create projects** to organize your tasks
3. **Add tasks** with priorities and due dates
4. **Track your progress** on the dashboard

### ✨ Features to Explore
- **Modern Dashboard**: Beautiful analytics and activity feeds
- **Dark Mode**: Toggle between light and dark themes
- **Project Management**: Color-coded projects with progress tracking
- **Task Priorities**: Four-level priority system with visual indicators
- **Achievements**: Gamification system with points and badges
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile

---

**Made with ❤️ using Flask**
