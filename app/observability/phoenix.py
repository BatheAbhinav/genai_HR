"""Arize Phoenix tracing setup.

Call `setup_phoenix()` once at application startup.  After that, every
LangChain / LangGraph invocation is automatically captured and visible in the
Phoenix UI at http://localhost:6006.
"""

import logging

logger = logging.getLogger("policy_search")


def setup_phoenix() -> None:
    """Start the Phoenix server and register the LangChain instrumentor."""
    try:
        import phoenix as px
        from openinference.instrumentation.langchain import LangChainInstrumentor
        from opentelemetry import trace as otel_trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor

        # Launch the embedded Phoenix server (opens http://localhost:6006).
        session = px.launch_app()
        logger.info("Phoenix UI available at %s", session.url)

        # Wire OpenTelemetry → Phoenix exporter.
        from phoenix.otel import register
        tracer_provider = register(project_name="policy-search")

        # Instrument LangChain (covers LangGraph nodes automatically).
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

        logger.info("Arize Phoenix tracing enabled — all agent traces will appear in the UI.")

    except ImportError:
        logger.warning(
            "Arize Phoenix packages not installed — tracing disabled. "
            "Run: pip install arize-phoenix openinference-instrumentation-langchain"
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Phoenix setup failed (tracing disabled): %s", exc)
