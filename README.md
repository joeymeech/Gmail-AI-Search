# Gmail AI Search App

This Streamlit app uses OpenAI-compatible sentence embedding models to help you search your Gmail inbox using natural language. You can search by keyword, time range, and Gmail category.

## Features
- ✅ Secure Gmail OAuth login
- 🔎 Natural language search using semantic similarity
- 📅 Time range filtering
- 📂 Category filtering (e.g., Inbox, Promotions)
- 🤖 AI-based matching using cosine similarity

---

## Setup Instructions

### 1. Clone this repo
```bash
git clone https://github.com/YOUR_USERNAME/gmail-ai-search.git
cd gmail-ai-search
```

### 2. Set up Gmail API credentials
- Go to https://console.cloud.google.com/
- Create a new project
- Enable the **Gmail API**
- Create OAuth credentials (Desktop type)
- Download `credentials.json` and place it in your project root
- In the OAuth consent screen, add your email to test users

### 3. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the app
```bash
streamlit run gmail_ai_search.py
```

---

## Notes
- The first time you run the app, it will open a browser window to authenticate with Google.
- You can only use Gmail accounts that are test users in your Google Cloud project unless the app is verified.

---
## Image

![Screenshot 2025-05-27 200912](https://github.com/user-attachments/assets/a6e0c704-3b8f-43b8-b475-a012c3aaf720)

---

## To-Do / Future Improvements
- Export matched emails
- Improve HTML email parsing
- UI refinements


## Credits
Created with ❤️ by Joey Milici
