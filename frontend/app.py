import os
import time
import streamlit as st
import requests

from auth import authenticate
from logger import logger, configure_logging

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor

#################################################
# OTel Initialisation (runs once at module load)
#################################################

_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
_SERVICE_NAME  = os.getenv("OTEL_SERVICE_NAME", "llamaops-ai")

_resource = Resource.create({"service.name": _SERVICE_NAME})

_tracer_provider = TracerProvider(resource=_resource)
_tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=_OTLP_ENDPOINT, insecure=True))
)
trace.set_tracer_provider(_tracer_provider)

_metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=_OTLP_ENDPOINT, insecure=True),
    export_interval_millis=15_000,
)
_meter_provider = MeterProvider(resource=_resource, metric_readers=[_metric_reader])
metrics.set_meter_provider(_meter_provider)

RequestsInstrumentor().instrument()

tracer = trace.get_tracer(_SERVICE_NAME)
meter  = metrics.get_meter(_SERVICE_NAME)

ai_request_counter = meter.create_counter(
    "ai.requests.total",
    description="Total number of AI chat requests",
)
ai_response_duration = meter.create_histogram(
    "ai.response.duration",
    unit="s",
    description="Duration of AI model response in seconds",
)

#################################################
# Logging (OTel-correlated)
#################################################

configure_logging(_OTLP_ENDPOINT)

#################################################
# Session State Initialisation
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
.block-container { padding-top: 2rem; }
textarea { font-size: 16px !important; }
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

        with tracer.start_as_current_span("auth.login") as span:
            span.set_attribute("user.name", username)
            try:
                if authenticate(username, password):
                    st.session_state.logged_in = True
                    span.set_attribute("auth.success", True)
                    logger.info("User authenticated successfully")
                    st.rerun()
                else:
                    span.set_attribute("auth.success", False)
                    logger.error("Authentication failed for user: %s", username)
                    st.error("Invalid Credentials")

            except Exception as e:
                span.record_exception(e)
                logger.exception("Login error")
                st.error(f"Error: {e}")

#################################################
# AI Chat Section
#################################################

if st.session_state.logged_in:

    prompt = st.text_area("Ask AI", placeholder="Ask anything...")

    if st.button("Generate Response"):

        if prompt.strip() == "":
            st.warning("Please enter a question")

        else:

            with tracer.start_as_current_span("ai.chat.request") as span:

                span.set_attribute("ai.model", "phi")
                span.set_attribute("ai.prompt.length", len(prompt))

                with st.spinner("Generating response..."):

                    start = time.time()
                    status = "success"

                    try:
                        response = requests.post(
                            "http://ollama:11434/api/chat",
                            json={
                                "model": "phi",
                                "messages": [{"role": "user", "content": prompt}],
                                "stream": False,
                            },
                            timeout=120,
                        )

                        result = response.json()

                        if "message" in result:
                            reply = result["message"]["content"]
                            span.set_attribute("ai.response.length", len(reply))
                            logger.info("AI response generated successfully")
                            st.markdown(reply)
                        else:
                            status = "unexpected_response"
                            span.set_attribute("ai.error", "unexpected_response_format")
                            st.error("Unexpected response from AI model")
                            st.json(result)

                    except Exception as e:
                        status = "error"
                        span.record_exception(e)
                        span.set_status(trace.StatusCode.ERROR, str(e))
                        logger.exception("AI response error")
                        st.error(f"AI Error: {e}")

                    finally:
                        elapsed = time.time() - start
                        ai_request_counter.add(1, {"model": "phi", "status": status})
                        ai_response_duration.record(elapsed, {"model": "phi", "status": status})
                        span.set_attribute("ai.response.duration_s", elapsed)
