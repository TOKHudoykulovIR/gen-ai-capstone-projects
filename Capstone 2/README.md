# 🎨 Voice to Image App

A simple Streamlit application that takes a short voice message as input, converts it to text using OpenAI Whisper, generates a detailed image prompt via GPT, and finally creates an image using DALL·E. The app also displays a live log history in the UI.

<img width="800" alt="voice-to-image-ui" src="" />

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

# Install dependencies
pip install -r requirements.txt

## ⚙️ Environment Variables ### Create a file named .env in the project root and add:
bash
OPENAI_API_KEY=

▶️ Run the Application
bash
streamlit run app.py
## 🗂 Project Structure
project/
│── app.py                 # main logic
│── requirements.txt       # project dependencies 
└── .env                   # env variables file


