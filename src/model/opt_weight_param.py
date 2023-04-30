from pydantic import BaseModel


class OptWeightParam(BaseModel):
    mode: str


class ReturnOptWeightParam(OptWeightParam):
    mode: str = 'return'

    def __str__(self):
        return 'RC'


class TCAdjustedReturnOptWeightParam(OptWeightParam):
    mode: str = 'TC_adjusted_return'
    lda: float
    fee: float

    def __str__(self):
        return f'TC[{self.lda},{self.fee}]'
