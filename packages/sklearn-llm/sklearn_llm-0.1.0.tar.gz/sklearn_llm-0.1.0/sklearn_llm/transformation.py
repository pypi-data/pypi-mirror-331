import asyncio
import logging
from typing import Generic, Type

from jinja2 import Template
from sklearn.base import TransformerMixin

from .base import InputType, OutputType
from .llms import OpenAIClient

logging.basicConfig(level=logging.INFO)


class LLMTransformer(TransformerMixin, Generic[InputType, OutputType]):
    """
    A scikit-learn based Transformer that uses an LLM to transform the data.

    Currently it only supports OpenAI models.
    """

    def __init__(
        self,
        input_type: Type[InputType],
        output_type: Type[OutputType],
        system_prompt: str = "",
        user_prompt_template: str = "",
        model: str = "gpt-4o-mini",
        max_concurrent_requests: int = 10,
        max_retries: int = 3,
    ):
        """
        Initialize the transformer.

        Args:
            input_type: The type of the input data (should be derived from pydantic.BaseModel).
            output_type: The type of the output data (should be derived from pydantic.BaseModel).
            system_prompt: The system prompt string (not a template).
            user_prompt_template: The user prompt template.
            model: The OpenAI GPT model to use (e.g. `gpt-4o-mini`).
            max_concurrent_requests: The maximum number of concurrent requests to avoid hitting rate limits.
            max_retries: The maximum number of retries.
        """
        self.system_prompt = system_prompt
        self.user_prompt = Template(user_prompt_template)
        self._input_type = input_type
        self._output_type = output_type
        self._llm_client = OpenAIClient(model, max_concurrent_requests, max_retries)

    def fit(self, X: any, y=None):
        return self

    async def transform_async(self, X: list[InputType]) -> list[OutputType]:
        user_prompts = [self.user_prompt.render(**x.model_dump()) for x in X]
        tasks = [
            self._llm_client.call(
                system_prompt=self.system_prompt, user_prompt=user_prompt, output_model=self._output_type
            )
            for user_prompt in user_prompts
        ]
        result = await asyncio.gather(*tasks, return_exceptions=True)

        return result

    def transform(self, X: list[InputType]) -> list[OutputType]:
        """
        Transforms input using LLM API and returns the list of output instances.
        """
        return asyncio.run(self.transform_async(X))
