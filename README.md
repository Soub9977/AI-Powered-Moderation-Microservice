Apologies for missing the Docker details! Here's the updated **README** that includes Docker setup, but still keeps everything concise:

---

# 🚀 AI-Powered Content Moderation

An AI-powered web service for content moderation, detecting toxic content using **FastAPI** and **PostgreSQL**.

🔗 **Live Demo**: [AI-Powered Content Moderation](https://ai-powered-content-moderation-oz7j.onrender.com)

---

## 🛠️ Tech Stack

- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Deployment**: Render (for live demo)
- **Containerization**: Docker (optional)

---

## 📋 Installation & Setup

### Step 1: Clone the Repository

Clone the repository to your local system:

```bash
git clone <your-repository-url>
cd ai-powered-content-moderation
```

### Step 2: Set Up PostgreSQL

1. **Install PostgreSQL**:
   - Install PostgreSQL on your local machine or use a PostgreSQL cloud service (like Render, Heroku, etc.).
   - Create a new database (e.g., `content_moderation`) and a user with necessary permissions.

2. **Create a `.env` file**:
   - In the project folder, create a `.env` file to store environment variables (e.g., PostgreSQL credentials).
   - Add your database connection details (host, port, username, password, and database name).

### Step 3: Install Dependencies

In your project directory, install the required Python dependencies:

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application Locally

Run the FastAPI application:

```bash
uvicorn main:app --reload
```

- The app will be running on `http://localhost:8000`.

---

## 🐳 Docker Setup (Optional)

If you prefer using Docker to containerize the app, follow these steps:

1. **Build the Docker Image**:

```bash
docker build -t ai-content-moderation .
```

2. **Run the Docker Container**:

```bash
docker run -d -p 8000:8000 ai-content-moderation
```

- The app will be accessible at `http://localhost:8000` inside the Docker container.

3. **Using Docker Compose** (Optional):

You can also use Docker Compose to manage both the FastAPI app and PostgreSQL container.

```bash
docker-compose up --build
```

This will set up both the app and the database in separate containers.

---

## 🚀 Deployment on Render

1. **Push your code to GitHub**: Ensure your project is on a GitHub repository.
2. **Create a Web Service on Render**:
   - Sign up/login to [Render](https://render.com).
   - Create a new Web Service and link your GitHub repository.
3. **Set up Environment Variables**:
   - Add the necessary environment variables (e.g., PostgreSQL connection details) in the Render dashboard.
4. **Deploy**: After linking, Render will automatically build and deploy your application.

---

## 📡 API Endpoints

- `POST /predict`: Submit content to analyze for toxic content.
- `GET /health`: Check if the server is running.

---

## 👤 Author

Built with ❤️ by **Soubhagya C. Kotian**  
🔗 [LinkedIn Profile](https://www.linkedin.com/in/soubhagya-kotian/)

---

This version now includes steps for **Docker setup** and **running the app inside Docker containers**, as well as the simple local setup. Let me know if this works!
