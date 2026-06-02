import streamlit as st
from auth import authenticate
from logger import logger
import requests

#################################################
# Session State
#################################################

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

#################################################
# App Title
#################################################

st.title("Development AI Application")

#################################################
# Login Section
#################################################

if not st.session_state.logged_in:

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if authenticate(username, password):

            st.session_state.logged_in = True

            logger.info("User authenticated successfully")

            st.success("Login Successful")

            st.rerun()

        else:

            logger.error("Authentication Failed")

            st.error("Invalid Credentials")

#################################################
# AI Chat Section
#################################################

if st.session_state.logged_in:

    st.success("Login Successful")

    prompt = st.text_area("Ask AI")

    if st.button("Generate Response"):

        try:

            response = requests.post(
                "http://ollama:11434/api/generate",
                json={
                    "model": "tinyllama",
                    "prompt": prompt,
                    "stream": False
                }
            )

            result = response.json()

            logger.info("AI response generated")

            st.success("AI Response")

            st.write(result["response"])

        except Exception as e:

            logger.error(f"AI Error: {e}")

            st.error(e)