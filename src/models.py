from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal


class PromptInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prompt: str = Field(min_length=1)
    @field_validator("prompt", mode="before")
    @classmethod
    def strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class TypeDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["string", "number", "boolean"]


class FunctionDefinition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, TypeDefinition]
    returns: TypeDefinition

    @field_validator("name", "description", mode="before")
    @classmethod
    def strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value
