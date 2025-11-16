# 🎨 Voice to Image App

A simple Streamlit application that takes a short voice message as input, converts it to text using OpenAI Whisper, generates a detailed image prompt via GPT, and finally creates an image using DALL·E. The app also displays a live log history in the UI.

<img width="889" height="938" alt="instructions" src="https://github.com/user-attachments/assets/5e87e1a4-c8b2-46fe-b11a-00f818a9d3d2" />

---

## 📦 Installation

```bash
# Clone the repository
git clone https://...
cd voice-to-image-app

# Create a virtual environment
python -m venv venv

# Activate the environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

# Install dependencies
```bash
pip install -r requirements.txt
```

## ⚙️ Environment Variables ### Create a file named .env in the project root and add:
```bash
OPENAI_API_KEY=
```

▶️ Run the Application
```bash
streamlit run app.py
```

## 🗂 Project Structure
```bash
project/
│── app.py                 # main logic
│── requirements.txt       # project dependencies 
└── .env                   # env variables file
```

