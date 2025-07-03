# 🚀 Task Tracker Pro X

A comprehensive, feature-rich task management application built with Flask, featuring real-time collaboration, gamification, and enterprise-ready deployment.

## ✨ Features

### 🎯 Core Task Management
- ✅ Full CRUD operations for tasks and projects
- 📅 Due dates with overdue highlighting
- 🎚️ Priority levels (Low, Medium, High, Urgent)
- 🔄 Recurring tasks (Daily, Weekly, Monthly, Yearly)
- 📝 Subtasks and task hierarchies
- 💬 Comments and collaboration
- 📎 File attachments

### 👥 User Management & Authentication
- 🔐 User registration and login
- 👤 User profiles and avatars
- 🔒 Session management with Flask-Login
- ✉️ Email verification
- 🎨 Dark/Light theme toggle

### 📊 Dashboard & Analytics
- 📈 Project completion progress bars
- 📊 Task analytics and insights
- 🏆 Gamification system with points and achievements
- 🔥 Activity streaks
- 📅 Calendar integration

### 🎮 Gamification
- 🎯 Points system for task completion
- 🏅 Achievements and badges
- 📈 User levels and progress tracking
- 🔥 Streak counters
- 🏆 Leaderboards

### 🔗 Integrations
- 📅 Google Calendar sync
- 💬 Slack notifications
- 📧 Email notifications
- 🔌 Plugin architecture

### 🚀 Real-time Features
- ⚡ Live updates with WebSockets
- 👥 Real-time collaboration
- 🔔 Instant notifications

### 🎨 Modern UI/UX
- 📱 Fully responsive design
- 🎨 Bootstrap 5 with custom themes
- 🌙 Dark mode support
- 🎯 Intuitive modal-based forms
- 📊 Interactive charts and visualizations

## 🛠️ Technology Stack

- **Backend**: Flask, SQLAlchemy, Flask-SocketIO
- **Frontend**: Bootstrap 5, JavaScript ES6, Socket.IO
- **Database**: PostgreSQL (production), SQLite (development)
- **Cache**: Redis
- **Task Queue**: Celery
- **Deployment**: Docker, Docker Compose
- **CI/CD**: GitHub Actions

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for production)
- Redis (for real-time features)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/task-tracker-pro-x.git
   cd task-tracker-pro-x
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

   Visit `http://localhost:8082` to access the application.

### Production Deployment with Docker

1. **Clone and configure**
   ```bash
   git clone https://github.com/yourusername/task-tracker-pro-x.git
   cd task-tracker-pro-x
   cp .env.example .env
   # Configure production settings in .env
   ```

2. **Deploy with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Initialize the database**
   ```bash
   docker-compose exec web flask db upgrade
   ```

## 📁 Project Structure

```
task_tracker_pro_flask/
├── app.py                 # Main application factory
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Multi-container setup
├── .env.example          # Environment variables template
├── models/               # Database models
├── routes/               # Route blueprints
├── utils/                # Utility functions
├── static/               # Static assets
├── templates/            # Jinja2 templates
└── tests/                # Test suite
```

## 🔧 Configuration

Key environment variables:

```env
SECRET_KEY=your-super-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379
MAIL_SERVER=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
GOOGLE_CALENDAR_CREDENTIALS=path/to/credentials.json
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
```

## 🎮 Gamification System

The application includes a comprehensive gamification system:

- **Points**: Earn points for completing tasks
- **Levels**: Advance through levels based on total points
- **Streaks**: Maintain daily activity streaks
- **Achievements**: Unlock badges for various milestones
- **Leaderboards**: Compete with other users

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout

### Tasks
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task details
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

## 🧪 Testing

Run the test suite:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=app tests/
```

## 📈 Monitoring & Analytics

The application includes built-in analytics:

- Task completion rates
- Project progress tracking
- User activity patterns
- Performance metrics

## 🔒 Security Features

- CSRF protection
- SQL injection prevention
- Rate limiting
- Secure password hashing
- Session security

## 🚀 Deployment

### Quick Deploy Options

#### 🚄 Railway (Recommended - Free Tier)
1. Push your code to GitHub
2. Go to [railway.app](https://railway.app)
3. Connect your GitHub repository
4. Add PostgreSQL database (automatically configured)
5. Set environment variable: `SECRET_KEY=your-secret-key`

#### 🎯 Render
1. Go to [render.com](https://render.com)
2. Create new Web Service from GitHub
3. Add PostgreSQL database
4. Set environment variables:
   - `SECRET_KEY=your-secret-key`
   - `DATABASE_URL` (from PostgreSQL service)

#### 🟣 Heroku
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

#### 🐳 Docker Deployment
```bash
docker build -t tasktracker .
docker run -p 5000:5000 -e SECRET_KEY=your-secret-key tasktracker
```

### Environment Variables
Set these for production:
- `SECRET_KEY`: Secure random string
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: Set to "production"

Optional:
- `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD`: For email notifications
- `REDIS_URL`: For real-time features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Bootstrap team for the amazing UI framework
- Flask community for the excellent web framework
- All contributors who make this project better

---

**Made with ❤️ by the Task Tracker Pro X team**
