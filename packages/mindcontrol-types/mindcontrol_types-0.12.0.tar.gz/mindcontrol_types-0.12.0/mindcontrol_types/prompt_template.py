from .var import VarV1
from .signature import SignatureInputFieldsV1
from genotype import Model


class PromptTemplateV1(Model):
    """Prompt template. Represents an individual prompt with variables that can be
    used independently."""

    var: VarV1
    """Template variable"""
    signature: SignatureInputFieldsV1
    """Template signature."""
    content: str
    """Template content."""
