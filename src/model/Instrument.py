from pydantic import BaseModel
import re


class Instrument(BaseModel):
    symbol: str
    location: str


class HKEquityInstrument(Instrument):
    location = 'hk'

    @property
    def yahoo_finance_symbol(self):
        return '{:0>4}.HK'.format(self.symbol)

    @property
    def aastock_symbol(self):
        return '{:0>5}.HK'.format(self.symbol)

    @property
    def hang_seng_symbol(self):
        return self.symbol

    @classmethod
    def from_hang_seng_symbol(cls, code):
        return HKEquityInstrument(
            symbol=code
        )

    @classmethod
    def from_aastock_symbol(cls, code):
        regexPattern = "^0+(?!$)"
        code = re.sub(regexPattern, "", code)
        code = code.replace(".HK", "")
        return HKEquityInstrument(
            symbol=code
        )
