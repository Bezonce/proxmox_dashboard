import os
import smtplib
import ssl

# New imports for handling attachments
from email.message import EmailMessage

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.title("📧 Email Sender with Attachments")
recipient = st.text_input("Send to:")
message_text = st.text_area("Message:", "Check out this attachment!")
uploaded_file = st.file_uploader("Choose a file to attach")

if st.button("Send Email"):
    if not recipient or not uploaded_file:
        st.error("Please provide both a recipient and a file.")
    else:
        # 1. Create the 'Package'
        msg = EmailMessage()
        msg["Subject"] = "File from Streamlit"
        msg["From"] = os.getenv("GMAIL_ADDRES")
        msg["To"] = recipient
        msg.set_content(message_text)

        # 2. Process the Attachment
        file_data = uploaded_file.read()
        file_name = uploaded_file.name

        # Add the attachment to the package
        msg.add_attachment(
            file_data,
            maintype="application",
            subtype="octet-stream",  # This is a generic type for any file
            filename=file_name,
        )

        # 3. Send via SMTP
        smtp_server = "smtp.gmail.com"
        port = 587
        password = os.getenv("GMAIL_APP_PASSWORD")
        context = ssl.create_default_context()

        try:
            with st.spinner("Sending message with attachment..."):
                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls(context=context)
                    server.login(msg["From"], password)
                    server.send_message(msg)  # Note: we use send_message now
            st.success("Sent successfully!")
        except Exception as e:
            st.error(f"Error: {e}")
