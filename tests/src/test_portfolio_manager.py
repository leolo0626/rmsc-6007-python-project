import pytest
import pandas as pd
import random
import numpy as np
from src.algo.CORN import CORN

from src.data_provider.data_helper import count_na_in_dataframe

exempt_list = ['META', 'TSLA', 'PYPL', 'MRNA', 'CHTR', 'ZM', 'NXPI', 'DOCU', 'JD', 'KHC', 'TEAM', 'WDAY', 'XLNX',
               'PTON', 'PDD', 'OKTA', 'CDW', 'MXIM', 'CERN', 'SPLK', 'FOX']

selections = ['DXCM', 'MTCH', 'ADBE', 'BIIB', 'TXN', 'PCAR', 'FAST', 'MSFT', 'GILD', 'ADI']



nasdaq100 = pd.read_csv('../../src/data/nasdaq100.csv', index_col=0)
nasdaq10 = nasdaq100[selections]
# Todo: Need a data processing tools to fill na case



result = CORN(5, 0.2).run(nasdaq10)