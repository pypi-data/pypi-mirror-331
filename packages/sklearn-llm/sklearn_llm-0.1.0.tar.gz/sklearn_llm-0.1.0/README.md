# README #

`sklearn-llm` is a Python module for building data transformation pipelines combining the power of scikit-learn and Large Language Models (LLMs).

# Installation

The easiest way to install is with `pip`: 

```
pip install sklearn-llm
```

See `pyproject.toml` for the list of dependencies.

## Pre-requisites

You will also need an API key from OpenAI to use its LLM models for your data transformations. Currently it's the only supported LLM provider.

Set the `OPENAI_API_KEY` variable in a `.env` file, following the same format as `.env_example`.

## Quick guide


To define a transformation, you need the following:
- An input class and an output class, both should be Pydantic base models. 
- The prompts (system and user prompt) for the transformation.

See `sklearn_llm/example.py` for an example.

## Benefits

With `sklearn-llm`, you can do the following:

- Define data transformations in sklearn's Transformer interface using LLM calls.
- Use type hints to enhance understanding of the data transformation flows (instead of generic dataframes).
- Compose flexible transformations using sklearn's Pipeline interface. This is similar to building chain of LLM calls in `langchain` but simpler if you only require this use case.

Example applications:
- Create a pipeline to generate synthetic data and evaluate the quality of the data using two transformers.

