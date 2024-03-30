from pydantic import BaseModel
class YelpQueryInput(BaseModel):
    text: str
class YelpQueryOutput(BaseModel):
    input: str
    output: str
    intermediate_steps: list[str]