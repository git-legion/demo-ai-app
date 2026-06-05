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
# Page Configuration
#################################################

st.set_page_config(
    page_title="LlamaOps AI",
    page_icon="🤖",
    layout="centered"
)

#################################################
# Custom Styling
#################################################

st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
}

textarea {
    font-size: 16px !important;
}

</style>
""", unsafe_allow_html=True)

#################################################
# Title
#################################################

st.title("LlamaOps AI")

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

    prompt = st.text_area(
        "Ask AI",
        placeholder="Ask anything..."
    )

    if st.button("Generate Response"):

        try:

            #################################################
            # Validate Prompt
            #################################################

            if prompt.strip() == "":

                st.warning("Please enter a question")

            else:

                #################################################
                # AI Loading Spinner
                #################################################

                with st.spinner("Generating response..."):

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

                    if "message" in result:

                        st.markdown(result["message"]["content"])

                    else:

                        st.error("Unexpected response from AI model")

                        st.json(result)

        except Exception as e:

            logger.exception("AI Response Error")

            st.error(f"AI Error: {e}")