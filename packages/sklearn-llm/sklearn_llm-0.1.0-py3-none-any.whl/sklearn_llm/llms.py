import asyncio

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic import BaseModel

load_dotenv()


class OpenAIClient:
    """
    A thin wrapper around the OpenAI API client that handles retries and
    multiple concurrent requests with a maximum limit using semaphore.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        max_concurrent_requests: int = 10,
        max_retries: int = 3,
    ):
        self.model = model
        self.max_retries = max_retries
        self.max_concurrent_requests = max_concurrent_requests
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._client = AsyncOpenAI()

    async def call(self, system_prompt: str, user_prompt: str, output_model: BaseModel) -> dict:
        if user_prompt == "" and system_prompt == "":
            raise ValueError("At least one of user_prompt or system_prompt must be provided.")

        for attempt in range(self.max_retries):
            async with self._semaphore:
                completion = await self._client.beta.chat.completions.parse(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format=output_model,
                )
                result = completion.choices[0].message
                if result.parsed:
                    return result.parsed
                else:
                    print("Failure: ", completion)
                    await asyncio.sleep(2**attempt)

        raise Exception("Max retries exceeded")
