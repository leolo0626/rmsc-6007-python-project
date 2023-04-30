import pandas as pd
from pydantic import BaseModel
from typing import Dict, Any


class AlgoRunnerReq(BaseModel):
    params: Dict[str, Any]
    algo_class: Any = None

    def initialize_algo(self):
        return self.algo_class(**self.params)

    def get_output_file_name(self):
        param_str = "_".join([f"[{param},{self.params[param]}]" for param in self.params])
        return f"{self.algo_class.__name__}_{param_str}.csv"

    def __str__(self):
        return f"{self.algo_class.__name__}: {self.params}"

class AlgoRunner:
    def __init__(self,
                 asset_price=None,
                 abs_parent_path=None,
                 save_path=None,
                 ):
        self.abs_parent_path = abs_parent_path
        self.save_path = self._get_path(save_path)
        self.asset_price = asset_price

    def run(self, algo_opt_req: AlgoRunnerReq):
        import warnings
        warnings.filterwarnings("ignore")
        print(f"{algo_opt_req} start......")
        algo = algo_opt_req.initialize_algo()
        weight = algo.run(self.asset_price)
        weight_df = pd.DataFrame(weight)
        weight_df.index = self.asset_price.index
        weight_df.columns = self.asset_price.columns
        print(f"{algo_opt_req} end......")
        return weight_df

    def _get_path(self, file_path):
        if self.abs_parent_path:
            return f'{self.abs_parent_path}/{file_path}'
        else:
            return f'../{file_path}'

    def run_and_save(self, algo_opt_req: AlgoRunnerReq):
        weight_df = self.run(algo_opt_req)
        weight_df.to_csv(f'{self.save_path}/{algo_opt_req.get_output_file_name()}')
