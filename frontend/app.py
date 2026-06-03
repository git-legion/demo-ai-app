import streamlit as st
from auth import authenticate
from logger import logger
import requests

#################################################
# Session State Initialization
#################################################

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

#################################################
# Page Title
#################################################

st.set_page_config(
    page_title="Development AI Application",
    page_icon="🤖",
    layout="centered"
)

st.title("Development AI Application")

#################################################
# Login Section
#################################################

if not st.session_state.logged_in:

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        try:

            if authenticate(username, password):

                st.session_state.logged_in = True

                logger.info("User authenticated successfully")

                st.success("Login Successful")

                st.rerun()

            else:

                logger.error("Authentication Failed")

                st.error("Invalid Credentials")

        except Exception as e:

            logger.exception("Login Error")

            st.error(f"Error: {e}")

#################################################
# AI Chat Section
#################################################

if st.session_state.logged_in:

    st.success("Login Successful")

    prompt = st.text_area("Ask AI")

    if st.button("Generate Response"):

        try:

            #################################################
            # Validate Prompt
            #################################################

            if prompt.strip() == "":

                st.warning("Please enter a question")

            else:

                #################################################
                # Send Request To Ollama
                #################################################

                response = requests.post(
                    "http://ollama:11434/api/chat",
                    json={
                        "model": "phi",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "stream": False
                    },
                    timeout=120
                )

                #################################################
                # Convert Response To JSON
                #################################################

                result = response.json()

                logger.info("AI response generated successfully")

                #################################################
                # Display AI Response
                #################################################

                st.success("AI Response")

                if "message" in result:

                    st.write(result["message"]["content"])

                else:

                    st.error("Unexpected response from AI model")

                    st.write(result)

        except Exception as e:

            logger.exception("AI Response Error")

            st.error(f"AI Error: {e}")