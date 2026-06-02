import streamlit as st
from auth import authenticate
from logger import logger
import requests

st.title("Development AI Application")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):

    try:

        if authenticate(username, password):

            logger.info("User authenticated successfully")

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

                except Exception as ai_error:

                    logger.error(f"AI Error: {ai_error}")

                    st.error(ai_error)

        else:

            logger.error("Authentication Failed")

            st.error("Invalid Credentials")

    except Exception as e:

        logger.exception("Application Error")

        st.error("Something went wrong")