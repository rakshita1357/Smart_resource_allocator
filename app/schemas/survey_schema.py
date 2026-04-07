from pydantic import BaseModel
from typing import List, Optional


class SurveyCreateResponse(BaseModel):
    survey_id: int
    extracted_text: Optional[str]
    identified_skills: List[str]

