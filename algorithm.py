import json

from algorithms.algorithm_all_uni import algorithm_ALL
from algorithms.algorithm_cma_cgm import algorithm_cma_cgm
from algorithms.algorithm_evergreen import algorithm_evergreen
from algorithms.algorithm_concor import algorithm_concor
from algorithms.algorithm_cosco import algorithm_cosco
from algorithms.algorithm_hmm import algorithm_hmm
from algorithms.algorithm_kuehne_nagel import algorithm_kuehne_nagel
from algorithms.algorithm_leschaco import algorithm_leschaco
from algorithms.algorithm_maersk import algorithm_maersk
from algorithms.algorithm_msc import algorithm_msc
from algorithms.algorithm_one import algorithm_one
from algorithms.algorithm_oocl import algorithm_oocl
from algorithms.algorithm_hapag_lloyd import algorithm_hapag_lloyd

algorithms = {
    'CMA-CGM': algorithm_cma_cgm,
    'Evergreen': algorithm_evergreen,
    'Maersk': algorithm_maersk,
    'MSC': algorithm_msc,
    'Hapag-Lloyd': algorithm_hapag_lloyd,
    'COSCO': algorithm_cosco,
    'ONE': algorithm_one,
    'OOCL': algorithm_oocl,
    'HMM': algorithm_hmm,
    'Kuehne Nagel': algorithm_kuehne_nagel,
    'LESCHACO': algorithm_leschaco,
    'CONCOR': algorithm_concor
}
def algorithm(raw_json, target_date_str):
    name =json.loads(raw_json)['result']['summary']['company']['name']
    if name in algorithms:
        algo_func = algorithms[name]
        return algo_func(raw_json, target_date_str)
    else:
        return algorithm_ALL(raw_json, target_date_str)

