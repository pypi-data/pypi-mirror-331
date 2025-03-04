from __future__ import annotations

import json
from datetime import timedelta
from typing import Optional, Sequence, Type, Union

import pyarrow as pa
from pydantic import BaseModel, Field

from chalk.features.underscore import Underscore, UnderscoreFunction
from chalk.utils.pydanticutil.pydantic_compat import is_pydantic_v1


def message(role: str, content: str):
    return UnderscoreFunction(
        "struct_pack",
        ["role", "content"],
        role,
        content,
    )


def run_prompt(name: str):
    """
    Runs a named prompt.

    Examples
    --------
    >>> import chalk.prompts as P
    >>> from chalk.features import features
    >>> @features
    ... class User:
    ...    id: str
    ...    description: float = P.run_prompt("describe_user")
    """
    return UnderscoreFunction("run_prompt", prompt_name=name)


def completion(
    model: str,
    messages: Sequence[Underscore],
    *,
    timeout: Optional[timedelta] = None,
    output_structure: Optional[Union[Type[BaseModel], str]] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_completion_tokens: Optional[int] = None,
    max_tokens: Optional[int] = None,
    stop: Optional[list[str]] = None,
    presence_penalty: Optional[float] = None,
    frequency_penalty: Optional[float] = None,
    logit_bias: Optional[dict[int, float]] = None,
    seed: Optional[int] = None,
    user: Optional[str] = None,
    model_provider: Optional[str] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    num_retries: Optional[int] = None,
):
    """
    Generate LLM model completions from a list of messages.

    Examples
    --------
    >>> import chalk.prompts as P
    >>> import chalk.functions as F
    >>> from chalk.features import features, DataFrame
    >>> from pydantic import BaseModel, Field
    >>> class AgeEstimate(BaseModel):
    ...     age: float = Field(description="Estimated age of the user")
    ...
    >>> @features
    ... class User:
    ...    id: str
    ...    description: str
    ...    estimated_age_response: PromptResponse = P.completion(
    ...        model="gpt-3.5-turbo",
    ...        messages=[
    ...            P.message("system", P.jinja("Estimate the age of the user based on the description: {{User.description}}")),
    ...        ],
    ...        output_structure=AgeEstimate,
    ...        max_tokens=100+2*F.length(_.description)
    ...    )
    ...    estimated_age: float = F.json_value(_.estimated_age_response.response, "$.age")
    """
    if isinstance(messages, str) or isinstance(messages, Underscore):
        raise ValueError("Messages should be a list of P.message objects, not a single object.")
    messages_parsed = UnderscoreFunction(
        "array_constructor",
        *messages,
    )
    if output_structure is None:
        output_structure_json = None
    elif isinstance(output_structure, str):
        output_structure_json = output_structure
    elif is_pydantic_v1():
        output_structure_json = output_structure.schema_json()
    else:
        output_structure_json = json.dumps(
            output_structure.model_json_schema()  # pyright: ignore[reportAttributeAccessIssue]
        )

    return UnderscoreFunction(
        "completion",
        model=model,
        messages=messages_parsed,
        timeout=timeout,
        output_structure=output_structure_json,
        temperature=temperature,
        top_p=top_p,
        max_completion_tokens=max_completion_tokens,
        max_tokens=max_tokens,
        stop=stop,
        presence_penalty=presence_penalty,
        frequency_penalty=frequency_penalty,
        logit_bias=pa.scalar(list(logit_bias.items()), type=pa.map_(pa.int64(), pa.float64()))
        if logit_bias is not None
        else None,
        seed=seed,
        user=user,
        num_retries=num_retries,
        model_provider=model_provider,
        base_url=base_url,
        api_key=api_key,
    )


class Message(BaseModel):
    role: str
    content: str


class Prompt(BaseModel):
    model: str
    messages: list[Message]
    timeout: Optional[timedelta]
    output_structure: Optional[str] = Field("Json representation of the output structure")
    temperature: Optional[float]
    top_p: Optional[float]
    max_completion_tokens: Optional[int]
    max_tokens: Optional[int]
    stop: Optional[list[str]]
    presence_penalty: Optional[float]
    frequency_penalty: Optional[float]
    logit_bias: Optional[dict[int, float]]
    seed: Optional[int]
    user: Optional[str]
    model_provider: Optional[str]
    base_url: Optional[str]
    num_retries: Optional[int]


class Usage(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int


class PromptResponse(BaseModel):
    response: Optional[str] = Field(
        description="Response from the model. Raw string if no output structure specified, json encoded string otherwise. None if the response was not received or incorrectly formatted."
    )
    prompt: Prompt
    usage: Optional[Usage]
