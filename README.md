# 🚀 Task Tracker Pro

A comprehensive task management application built with Flask, featuring project management, task tracking, and user authentication.

## ✨ Features

### 🎯 Core Task Management
- ✅ Full CRUD operations for tasks and projects
- 📅 Due dates with overdue highlighting
- 🎚️ Priority levels (Low, Medium, High, Urgent)
- � Task descriptions and notes
- 🏷️ Task categories and organization
- � Project progress tracking

### 👥 User Management & Authentication
- 🔐 User registration and login
- 👤 User profiles and authentication
- 🔒 Session management with Flask-Login

### 📊 Dashboard & Analytics
- 📈 Project completion progress
- 📊 Task analytics and insights
- 📅 Calendar views

## 🚀 Local Development Setup

### Prerequisites
- Python 3.8+ 
- pip (Python package manager)

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <your-repo-url>
   cd task_tracker_pro_flask
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

5. **Initialize the database**:
   ```bash
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```

6. **Run the application**:
   ```bash
   python app.py
   ```

7. **Access the application**:
   Open your browser and go to `http://localhost:5000`

### Development Commands

- **Run in development mode**:
  ```bash
  export FLASK_ENV=development  # On Windows: set FLASK_ENV=development
  python app.py
  ```

- **Reset database** (if needed):
  ```bash
  rm -f tasktracker_pro.db instance/tasktracker_pro.db
  python -c "from app import app, db; app.app_context().push(); db.create_all()"
  ```

## 📁 Project Structure

```
task_tracker_pro_flask/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── models/              # Database models
├── routes/              # Flask blueprints/routes
├── templates/           # Jinja2 templates
├── static/             # CSS, JS, images
└── utils/              # Utility modules
```

## 🛠️ Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: Bootstrap, JavaScript
- **Database**: SQLite (for local development)
- **Authentication**: Flask-Login with sessions

## 🎯 Usage

1. **Register a new account** or login with existing credentials
2. **Create projects** to organize your tasks
3. **Add tasks** with priorities, due dates, and descriptions
4. **Track progress** through the dashboard
5. **Manage your profile** and preferences

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you've activated your virtual environment and installed dependencies
2. **Database Issues**: Try deleting the database file and recreating it:
   ```bash
   rm -f tasktracker_pro.db instance/tasktracker_pro.db
   python -c "from app import app, db; app.app_context().push(); db.create_all()"
   ```
3. **Port Already in Use**: Change the port in `app.py` or stop other applications using port 5000

### Getting Help

- Check the [Issues](https://github.com/yourusername/task-tracker-pro/issues) page
- Create a new issue with detailed information about your problem

## 🚀 Quick Start for New Users

If you're opening this project for the first time, here's exactly what to run in your terminal:

### Option 1: Use the automated script (Recommended)

**For macOS/Linux:**
```bash
cd task_tracker_pro_flask
./run.sh
```

**For Windows:**
```cmd
cd task_tracker_pro_flask
run.bat
```

This script will automatically:
- Create a virtual environment if needed
- Install dependencies
- Start the application
- Open it at `http://localhost:5001`

### Option 2: Manual setup

### Step 1: Navigate to the project directory
```bash
cd task_tracker_pro_flask
```

### Step 2: Create and activate a virtual environment
```bash
# Create virtual environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Or on Windows
# venv\Scripts\activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the application
```bash
python app.py
```

### Step 5: Open in browser
Visit: `http://localhost:5001`

That's it! The app should now be running locally.

## 🎯 What to Expect

When you first run the application:

1. **Homepage**: You'll see a landing page for Task Tracker Pro
2. **Register**: Click "Register" to create your first account
3. **Login**: Use your new credentials to log in
4. **Dashboard**: After login, you'll see your personal dashboard
5. **Create Projects**: Start by creating your first project
6. **Add Tasks**: Add tasks to your projects with due dates and priorities

## ⚡ Development Workflow

### To stop the application:
Press `Ctrl + C` in the terminal where the app is running.

### To run again later:
```bash
# Navigate to project and activate virtual environment
cd task_tracker_pro_flask
source venv/bin/activate  # (or venv\Scripts\activate on Windows)

# Run the app
python app.py
```

---

Made with ❤️ using Flask
