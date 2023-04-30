from src.algo.CORN import CORN
from src.algo_runner import AlgoRunnerReq
from src.model.opt_weight_param import TCAdjustedReturnOptWeightParam

opt_weight_param = TCAdjustedReturnOptWeightParam(
    fee=0.2 / 100,
    lda=0.5
)

req = AlgoRunnerReq(algo_class=CORN, params={
    "window_size": 10, "corr_threshold": 0.3, "opt_weights_param": opt_weight_param
})

