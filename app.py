import streamlit as st
from auth import authenticate
from logger import logger
import requests

# Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.title("Development AI Application")

# Login Section
if not st.session_state.logged_in:

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        try:

            if authenticate(username, password):

                logger.info("User authenticated successfully")

                st.session_state.logged_in = True

                st.success("Login Successful")

                st.rerun()

            else:

                logger.error("Authentication Failed")

                st.error("Invalid Credentials")

        except Exception as e:

            logger.exception("Application Error")

            st.error(str(e))

# AI Section
else:

    st.success("Login Successful")

    prompt = st.text_area("Ask AI")

    if st.button("Generate Response"):

        try:

            logger.info("Generating AI response")

            response = requests.post(
                "http://ollama:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                }
            )

            ai_response = response.json()["response"]

            st.subheader("AI Response")

            st.write(ai_response)

        except Exception as e:

            logger.exception("AI Generation Failed")

            st.error(str(e))