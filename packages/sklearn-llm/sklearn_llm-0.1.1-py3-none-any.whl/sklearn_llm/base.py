from typing import TypeVar

from pydantic import BaseModel


class InputModel(BaseModel):

    @classmethod
    def prompt_fields(cls) -> list[str]:
        """Return the fields that should be included in the prompt.

        By default, all fields will be included. Subclass can override this to include only specific fields.
        """
        return list(cls.model_fields.keys())


InputType = TypeVar("InputModel", bound=BaseModel)
OutputType = TypeVar("OutputModel", bound=BaseModel)
