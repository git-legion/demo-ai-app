import streamlit as st
from auth import authenticate
from logger import logger

st.title("Demo AI Application")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):

    try:

        if authenticate(username, password):

            logger.info("User authenticated successfully")

            st.success("Login Successful")

            prompt = st.text_area("Ask AI")

            if st.button("Generate Response"):

                logger.info("AI response generated")

                st.write("AI Response Generated Successfully")

        else:

            logger.error("Authentication Failed")

            st.error("Invalid Credentials")

    except Exception:

        logger.exception("Application Error")

        st.error("Something went wrong")

