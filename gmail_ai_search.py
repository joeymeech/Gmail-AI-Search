import streamlit as st
import base64
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Gmail read-only scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def get_email_body(payload):
    parts = payload.get("parts", [])
    if not parts and "body" in payload:
        data = payload["body"].get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    for part in parts:
        if part["mimeType"] == "text/plain":
            data = part["body"].get("data")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        elif part.get("parts"):
            for subpart in part["parts"]:
                if subpart["mimeType"] == "text/plain":
                    data = subpart["body"].get("data")
                    if data:
                        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    return ""

def fetch_emails(service, query, label, max_results=100):
    if label.startswith("All"):
        full_query = query
    else:
        full_query = f"{query} label:{label}"

    results = service.users().messages().list(userId="me", q=full_query, maxResults=max_results).execute()
    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(userId="me", id=msg["id"], format="full").execute()
        payload = msg_data.get("payload", {})
        headers = payload.get("headers", [])
        internal_date = int(msg_data.get("internalDate", "0")) // 1000
        email_date = datetime.datetime.fromtimestamp(internal_date)

        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        body = get_email_body(payload)
        emails.append({"subject": subject, "body": body, "date": email_date})
    return emails

def main():
    st.title("\U0001F4E7 AI-Powered Gmail Search")

    search_text = st.text_input("\U0001F50D What do you remember about the email?")
    start_date = st.date_input("\U0001F4C5 Start Date", datetime.date(2024, 1, 1))
    end_date = st.date_input("\U0001F4C5 End Date", datetime.date.today())
    label = st.selectbox("\U0001F4C2 Inbox Type", [
        "All (excluding Trash/Spam/Promotions)",
        "All (including everything)",
        "INBOX", "IMPORTANT", "SENT", "CATEGORY_PERSONAL", "CATEGORY_UPDATES"
    ])

    if st.button("Search Emails"):
        st.write("\U0001F504 Searching...")

        service = get_gmail_service()
        base_query = f"after:{start_date.strftime('%Y/%m/%d')} before:{(end_date + datetime.timedelta(days=1)).strftime('%Y/%m/%d')}"

        if label == "All (excluding Trash/Spam/Promotions)":
            query = base_query + " -category:promotions -in:trash -in:spam"
        elif label == "All (including everything)":
            query = base_query
        else:
            query = base_query + f" label:{label}"

        emails = fetch_emails(service, query, label)
        if not emails:
            st.warning("No emails found!")
            return

        # Filter by strict date range
        emails = [e for e in emails if start_date <= e["date"].date() <= end_date]

        model = load_model()
        email_texts = [e["subject"] + " " + e["body"] for e in emails]
        email_embeddings = model.encode(email_texts)

        query_embedding = model.encode([search_text])
        sims = cosine_similarity(query_embedding, email_embeddings)[0]

        top_indices = sims.argsort()[::-1][:5]
        for i in top_indices:
            st.markdown("---")
            st.subheader(f"\U0001F4E8 Subject: {emails[i]['subject']}")
            st.text(emails[i]['body'][:700] + "...")
            st.caption(f"\U0001F9E0 Similarity Score: {sims[i]:.2f}")
            st.caption(f"\U0001F4C5 Date: {emails[i]['date'].strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    main()
