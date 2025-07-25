# Ware2 - Warehouse Intelligence Platform

A full-stack web application designed for warehouse management and inventory analysis. It provides a comprehensive dashboard to visualize inventory data, track item movements, and identify anomalies.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ware2
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   **⚠️ IMPORTANT**: Edit `.env` and set a strong `FLASK_SECRET_KEY` (minimum 32 characters)

3. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start Backend** (Terminal 1)
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python src/app.py
   ```

2. **Start Frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

## 🔒 Security Notes

- Never commit `.env` files to version control
- Use strong, unique secret keys for production
- File uploads are restricted to Excel formats only
- Production deployments should use PostgreSQL instead of SQLite

## Features

-   **Dashboard:** An interactive dashboard with key metrics, charts, and activity feeds.
-   **Inventory Analysis:** Upload inventory reports (Excel files) and perform analysis.
-   **Column Mapping:** Dynamically map columns from uploaded files to the system's schema.
-   **User Authentication:** Secure user registration and login.
-   **Responsive UI:** Modern user interface built with Next.js and Tailwind CSS.

## Tech Stack

-   **Frontend:** [Next.js](https://nextjs.org/), [React](https://reactjs.org/), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/)
-   **Backend:** [Flask](https://flask.palletsprojects.com/), [Python](https://www.python.org/)
-   **Data Processing:** [Pandas](https://pandas.pydata.org/) (for `.xlsx` processing)

## Project Structure

This project is a monorepo containing both the frontend and backend applications.

```
/
├── backend/      # Flask API
└── frontend/     # Next.js Web App
```

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

-   [Node.js](https://nodejs.org/en/) (v18.x or later recommended)
-   [Python](https://www.python.org/downloads/) (v3.8 or later) & `pip`

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd ware2
    ```

2.  **Set up the Backend (Flask):**
    ```bash
    # Navigate to the backend directory
    cd backend

    # Create and activate a virtual environment
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate

    # Install Python dependencies
    pip install -r requirements.txt

    # Go back to the root directory
    cd ..
    ```

3.  **Set up the Frontend (Next.js):**
    ```bash
    # Navigate to the frontend directory
    cd frontend

    # Install Node.js dependencies
    npm install
    
    # Go back to the root directory
    cd ..
    ```

## Running the Application

You need to run both the backend and frontend servers simultaneously in separate terminals.

1.  **Run the Backend Server:**
    ```bash
    # From the root directory
    cd backend

    # Activate the virtual environment if not already active
    # On Windows: .\venv\Scripts\activate
    # On macOS/Linux: source venv/bin/activate
    
    # Run the Flask application
    # The main Flask app instance is in 'src/app.py'
    flask --app src/app run
    
    # The backend will be running on http://127.0.0.1:5000
    ```

2.  **Run the Frontend Server:**
    ```bash
    # From the root directory, in a new terminal
    cd frontend

    # Run the Next.js development server
    npm run dev
    
    # The frontend will be available at http://localhost:3000
    ```
    Open [http://localhost:3000](http://localhost:3000) in your browser to see the application.

## Deployment

This application is configured for a monorepo deployment strategy:

-   **Frontend:** Can be deployed to a platform like [Vercel](https://vercel.com). Connect your Git repository and set the **Root Directory** to `frontend`.
-   **Backend:** Can be deployed to a service like [Render](https://render.com) or [Heroku](https://www.heroku.com/). Connect your Git repository and set the **Root Directory** to `backend`. Remember to configure environment variables for production. 