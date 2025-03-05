import os

import vertexai
from vertexai.generative_models import GenerativeModel, Part
from vertexai.language_models import TextEmbeddingInput
from vertexai.preview.language_models import TextEmbeddingModel

from fi.integrations.otel import VertexAIInstrumentor, register
from fi.integrations.otel.types import (
    EvalName,
    EvalSpanKind,
    EvalTag,
    EvalTagType,
    ProjectType,
)

trace_provider = register(
    project_type=ProjectType.EXPERIMENT,
    project_name="FUTURE_AGI",
    project_version_name="v1",
)


VertexAIInstrumentor().instrument(tracer_provider=trace_provider)


def get_text_embedding(text, title=None, task_type=None, output_dimensionality=None):
    model = TextEmbeddingModel.from_pretrained("text-embedding-005")

    text_embedding_input = TextEmbeddingInput(
        text=text, title=title, task_type=task_type
    )

    kwargs = {}
    if output_dimensionality:
        kwargs["output_dimensionality"] = output_dimensionality

    embeddings = model.get_embeddings([text_embedding_input], **kwargs)
    return [embedding.values for embedding in embeddings]


# Example usage:
if __name__ == "__main__":
    sample_text = "Your text here"
    vectors = get_text_embedding(sample_text)
    for vector in vectors:
        print(vector)
