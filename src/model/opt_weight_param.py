from pydantic import BaseModel


class OptWeightParam(BaseModel):
    mode: str


class ReturnOptWeightParam(OptWeightParam):
    mode: str = 'return'


class TCAdjustedReturnOptWeightParam(OptWeightParam):
    mode: str = 'TC_adjusted_return'
    lda: float
    fee: float
