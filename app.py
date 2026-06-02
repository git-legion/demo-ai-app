import streamlit as st
from auth import authenticate
from logger import logger
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

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

                logger.info("Generating AI response")

                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                ai_response = response.choices[0].message.content

                st.subheader("AI Response")

                st.write(ai_response)

        else:

            logger.error("Authentication Failed")

            st.error("Invalid Credentials")

    except Exception as e:

        logger.exception("Application Error")

        st.error(str(e))