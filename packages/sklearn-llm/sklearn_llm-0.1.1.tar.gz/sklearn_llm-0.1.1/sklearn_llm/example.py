"""An example of using the LLM Transformer to chain multiple LLM-based transformations together."""

import asyncio

from sklearn.pipeline import make_pipeline

from .base import BaseModel, InputModel
from .transformation import LLMTransformer


class FirstLastName(InputModel):
    first_name: str
    last_name: str


class FullName(InputModel):
    full_name: str


class LowercaseFullName(BaseModel):
    full_name: str


system_prompt1 = "Return the user name by concatenating the first name and last name."
user_prompt1 = """
    First Name: {{first_name}}
    Last Name: {{last_name}}
"""

system_prompt2 = "Return the full name in lowercase."
user_prompt2 = """
    Full Name: {{full_name}}
"""


async def run_separate_transformers(first_last_names: list[FirstLastName]) -> list[LowercaseFullName]:
    """Manually run the two transformers sequentially by feeding output of the first transformer to the second."""
    t1 = LLMTransformer(
        input_type=FirstLastName, output_type=FullName, system_prompt=system_prompt1, user_prompt_template=user_prompt1
    )
    full_names = await t1.transform_async(first_last_names)
    print(full_names)

    t2 = LLMTransformer(
        input_type=FullName,
        output_type=LowercaseFullName,
        system_prompt=system_prompt2,
        user_prompt_template=user_prompt2,
    )
    lowercase_full_names = await t2.transform_async(full_names)
    print(lowercase_full_names)

    return lowercase_full_names


def run_pipeline(first_last_names: list[FirstLastName]) -> list[LowercaseFullName]:
    """Run the two transformers using sklearn's pipeline."""
    pipeline = make_pipeline(
        LLMTransformer(
            input_type=FirstLastName,
            output_type=FullName,
            system_prompt=system_prompt1,
            user_prompt_template=user_prompt1,
        ),
        LLMTransformer(
            input_type=FullName,
            output_type=LowercaseFullName,
            system_prompt=system_prompt2,
            user_prompt_template=user_prompt2,
        ),
    )
    # calling fit_transform will stop the pipeline from complaining about not `fit()` not being called
    lowercase_full_names = pipeline.fit_transform(first_last_names)

    return lowercase_full_names


if __name__ == "__main__":
    first_last_names = [
        FirstLastName(first_name="Trung", last_name="Nguyen"),
        FirstLastName(first_name="John", last_name="Doe"),
    ]
    result1 = run_pipeline(first_last_names)
    result2 = asyncio.run(run_separate_transformers(first_last_names))

    assert result1 == result2
