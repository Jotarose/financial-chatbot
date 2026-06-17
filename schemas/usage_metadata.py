from pydantic import BaseModel


class UsageMetadata(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
