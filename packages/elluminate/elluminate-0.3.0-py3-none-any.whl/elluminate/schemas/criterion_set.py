from pydantic import BaseModel

from elluminate.schemas.prompt_template import PromptTemplate


class CriterionSet(BaseModel):
    """Criterion set model."""

    id: int
    name: str
    prompt_templates: list[PromptTemplate] | None = None


class CreateCriterionSetRequest(BaseModel):
    """Request to create a new criterion set.

    Args:
        name: The name of the criterion set
        prompt_template_id: The ID of the prompt template to associate with the criterion set
        criteria: Optional list of criterion strings to create alongside the criterion set

    """

    name: str
    prompt_template_id: int
    criteria: list[str] | None = None
