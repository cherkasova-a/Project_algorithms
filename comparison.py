import os
import pandas as pd
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
from algorithms.algorithm_all_uni import algorithm_ALL


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

data_folder = "data"
def compare_logic(test_date):
    comparison_results = []

    for company, specific_algo in algorithms.items():
        file_path = os.path.join(data_folder, f"sample_{company}.csv")
        
        try:
            df = pd.read_csv(file_path, encoding='utf-16')
            
            for idx, row in df.iterrows():
                raw_json = row['raw_json']
                
                res_spec, phases_spec = specific_algo(raw_json, test_date)
                
                res_all, phases_all = algorithm_ALL(raw_json, test_date)
                
                is_equal = (phases_spec == phases_all)
                
                if not is_equal:
                    comparison_results.append({
                        'company': company,
                        'row_index': idx,
                        'diff': f"Спец: {phases_spec} != Общий: {phases_all}"
                    })
        except Exception as e:
            print(f"Ошибка при обработке {company}: {e}")

    diff_df = pd.DataFrame(comparison_results)
    if diff_df.empty:
        print("Расхождений не найдено")
    else:
        print(f"Найдено расхождений: {len(diff_df)}")
        diff_df.to_csv("comparison_diff_report.csv", index=False)
        print("Детальный отчет сохранен в comparison_diff_report.csv")
        
    return diff_df

# Запуск
test_date = "2026-04-20T12:00:00"
differences = compare_logic(test_date)