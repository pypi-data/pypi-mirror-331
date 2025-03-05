from .var import VarV1
from genotype import Model
from typing import List, Literal, Union, TypeAlias


SignatureInputV1Type: TypeAlias = Union[Literal["string"], Literal["number"]]


class SignatureInputV1(Model):
    """Input schema. It defines individual input variable and type."""

    type: SignatureInputV1Type
    """Input type."""
    var: VarV1
    """Input variable."""


class SignatureInputFieldsV1(Model):
    input: List[SignatureInputV1]
    """Input definition."""


SignatureOutputV1Type: TypeAlias = Union[Literal["string"], Literal["json"]]


class SignatureOutputV1(Model):
    """Output type. It defines output variable and type."""

    type: SignatureOutputV1Type
    """Output type."""
    var: VarV1
    """Output variable."""


class SignatureV1(SignatureInputFieldsV1, Model):
    """Prompt signature. It defines the input and output types of the prompt."""

    output: SignatureOutputV1
    """Output definition."""
    n: int
    """The number of choices to generate."""
