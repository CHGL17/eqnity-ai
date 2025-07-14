from pydantic import BaseModel, Field
from typing import List

class ParameterChange(BaseModel):
    parameter_name: str = Field(description="El nombre exacto del parámetro a cambiar.")
    value: float = Field(description="El nuevo valor normalizado para el parámetro, entre 0.0 y 1.0.")
