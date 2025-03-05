import dspy

from fi.integrations.otel import DSPyInstrumentor, register
from fi.integrations.otel.types import (
    EvalName,
    EvalSpanKind,
    EvalTag,
    EvalTagType,
    ProjectType,
)

# Configure trace provider with custom evaluation tags
trace_provider = register(
    project_type=ProjectType.EXPERIMENT,
    project_name="FUTURE_AGI",
    project_version_name="v1",
)

# Instrument DSPy with the trace provider
DSPyInstrumentor().instrument(tracer_provider=trace_provider)


embedder = dspy.Embedder("openai/text-embedding-3-small", batch_size=100)
embeddings = embedder(
    ["hello", "world", "asre"],
)

# print("Embedding for 'hello':", embeddings[0].tolist())
