from pydantic import BaseModel
from typing import Optional

class Survey(BaseModel):
    id: Optional[str] = None
    image_path: str
    extracted_text: Optional[str]

    # in process