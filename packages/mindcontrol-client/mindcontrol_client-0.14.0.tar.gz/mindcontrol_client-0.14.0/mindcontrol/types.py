from typing import Callable, Awaitable, Dict, Literal, Union, TypeAlias
from mindcontrol_types import PromptV1

Interop = Callable[[PromptV1], Awaitable[str]]
"""Prompt interop function."""

TemplateVars: TypeAlias = Dict[str, Union[str, int, float, bool, None]]
"""Prompt template variables."""

VersionTag: TypeAlias = Union[Literal["published"], Literal["any"]]
"""Version tag."""
