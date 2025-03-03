from .prompt import PromptV1
from .var import VarV1
from .signature import SignatureV1
from .settings import SettingsV1
from .prompt_template import PromptTemplateV1
from typing import Union, TypeAlias, Literal, List, Optional, Any
from typing_extensions import Annotated
from pydantic import Field
from genotype import Model


class ResourceChainV1(Model):
    """Prompt chain resource. Represents a chain of prompts."""

    type: Literal["chain"]
    """Resource type."""
    var: VarV1
    """Chain variable"""
    signature: SignatureV1
    """Chain signature."""
    chain: List[PromptV1]
    """Prompts chain."""
    system: Optional[str] = None
    """Default system model instructions. Applied to each prompt in the chain unless specified."""
    settings: Optional[SettingsV1] = None
    """Default settings. Applied to each prompt in the chain unless specified."""


class ResourceDataV1(Model):
    """Data resource. Represents free-form data."""

    type: Literal["data"]
    """Resource type."""
    var: VarV1
    """Data variable."""
    data: Any
    """Data."""


class ResourcePromptV1(Model):
    """Prompt resource. Represents a prompt template."""

    type: Literal["prompt"]
    """Resource type."""
    var: VarV1
    """Prompt variable."""
    signature: SignatureV1
    """Prompt signature."""
    prompt: PromptV1
    """Prompt."""


class ResourceSettingsV1(Model):
    """AI model settings resource."""

    type: Literal["settings"]
    """Resource type."""
    var: VarV1
    """Settings variable."""
    settings: SettingsV1
    """Settings object."""


class ResourcePromptTemplatesV1(Model):
    """Templates resource."""

    type: Literal["templates"]
    """Resource type."""
    var: VarV1
    """Templates variable."""
    templates: List[PromptTemplateV1]
    """Templates object."""


ResourceV1: TypeAlias = Annotated[Union[ResourcePromptV1, ResourceChainV1, ResourceDataV1, ResourceSettingsV1, ResourcePromptTemplatesV1], Field(json_schema_extra={'discriminator': 'type'})]
