# Turkish Learning App

A web application for learning Turkish language, featuring daily words, popular phrases, and grammar lessons with video tutorials.

## Features

- Daily Turkish Words with examples
- Popular Words categorized by themes
- Grammar Lessons with video tutorials
- Progress tracking
- Responsive design

## Tech Stack

- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript
- Database: SQLite (development) / PostgreSQL (production)
- Styling: Bootstrap 5
- Deployment: Render.com

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Visit `http://localhost:5000` in your browser

## Deployment

This application is configured for deployment on Render.com:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the following:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Add environment variables:
   - `SECRET_KEY`: [your-secret-key]
   - `FLASK_ENV`: production

## Environment Variables

- `SECRET_KEY`: Secret key for Flask sessions
- `DATABASE_URL`: Database connection string (provided by Render)
- `FLASK_ENV`: Application environment (development/production)
- `PORT`: Application port (provided by Render)

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
