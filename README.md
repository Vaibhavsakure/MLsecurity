# SocialGuard AI 🛡️

SocialGuard AI is a full-stack, machine-learning-powered application designed to detect fake accounts, bots, and spam profiles across major social media platforms: Instagram, Twitter, Reddit, and Facebook. 

![SocialGuard AI](frontend/public/icons.svg) <!-- Replace with a real screenshot if needed -->

## Features ✨

- **Multi-Platform Detection:**
  - 📸 **Instagram:** Analyzes profile pictures, bio presence, follower ratios, and username patterns.
  - 🐦 **Twitter:** Evaluates tweet frequency, account age, follower/following ratios, and verification status.
  - 👽 **Reddit:** Checks account karma out-of-bounds, age, link-sharing frequency, and sentiment score.
  - 📘 **Facebook:** Detects spam profiles based on community involvement, age, post-sharing habits, and URL spam.
- **Advanced Machine Learning:** Powered by 4 custom-trained **XGBoost** classification models with high accuracy.
- **Premium User Interface:** A stunning, fully responsive "dark glassmorphism" UI built with React.
- **Secure Authentication:** Integrated with Firebase Authentication (Email/Password, Google Sign-In & GitHub Sign-In).
- **Fast Backend:** Real-time inference via a high-performance FastAPI Python backend.

## Tech Stack 🛠️

**Frontend:**
- React 19 + Vite
- React Router DOM
- Firebase Authentication SDK
- Pure Custom CSS (Glassmorphism design system)

**Backend:**
- Python 3.11
- FastAPI + Uvicorn
- Scikit-Learn + XGBoost + Pandas
- Joblib (Model serialization)

## Installation & Setup 🚀

### Prerequisites
- Node.js (v18+)
- Python 3.9+
- A Firebase Project (for authentication)

### 1. Clone the Repository
```bash
git clone https://github.com/Vaibhavsakure/MLsecurity.git
cd MLsecurity
```

### 2. Backend Setup
Navigate to the root directory and install dependencies:
```bash
pip install -r backend/requirements.txt
```
Start the FastAPI server:
```bash
cd backend
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```
The backend API will run at `http://127.0.0.1:8000`. You can view the Swagger UI documentation at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
Open a new terminal and navigate to the frontend directory:
```bash
cd frontend
npm install
```

Start the Vite development server:
```bash
npm run dev
```
The frontend will run at `http://localhost:5173`.

### 4. Firebase Configuration
Make sure your Firebase configuration allows **Email/Password**, **Google Sign-In**, and **GitHub Sign-In**. The configuration is located in `frontend/src/firebase.js`.

## API Endpoints 🛣️

- `GET /api/health` - Check backend and model loading status.
- `POST /api/predict/instagram` - Predict Instagram fake profiles.
- `POST /api/predict/twitter` - Predict Twitter bots.
- `POST /api/predict/reddit` - Predict Reddit bots.
- `POST /api/predict/facebook` - Predict Facebook spam.

## Model Training 🧠
The models were trained on publicly available datasets for social media bots and spam. The training scripts are included in the repository:
- `train_facebook.py`
- `train_reddit.py`
- `retrain_all.py` (Script to retrain Twitter, Facebook, and Reddit with optimized XGBoost hyper-parameters)

## Contributing 🤝
Contributions are welcome! Feel free to open an issue or submit a pull request if you want to improve feature extraction, add more platforms, or enhance the UI.

## License 📄
This project is licensed under the MIT License.
