from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    @field_validator("parameters", mode="before")
    @classmethod
    def validate_parameter_names(cls, value):
        if isinstance(value, dict):
            cleaned_parameters = {}
            for name, definition in value.items():
                if not isinstance(name, str):
                    raise ValueError("Parameter names must be strings")
                name = name.strip()
                if not name:
                    raise ValueError("Parameter names cannot be empty")
                if name in cleaned_parameters:
                    raise ValueError(
                        f"Duplicate parameter name after stripping: {name}")
                cleaned_parameters[name] = definition
            return cleaned_parameters
        return value
