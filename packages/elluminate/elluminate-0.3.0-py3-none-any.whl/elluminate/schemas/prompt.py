from datetime import datetime

from pydantic import BaseModel

from elluminate.schemas.prompt_template import PromptTemplate
from elluminate.schemas.template_variables import TemplateVariables


class Prompt(BaseModel):
    """New prompt model."""

    id: int
    prompt_template: PromptTemplate
    template_variables: TemplateVariables
    prompt_str: str  # Computed field
    created_at: datetime
