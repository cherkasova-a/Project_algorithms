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

results_log_personality = []
results_log_uni = []

test_date = "2026-04-01T00:00:00"
data_folder = "data"

for company, algo_func in algorithms.items():
    file_path = os.path.join(data_folder, f"sample_{company}.csv")
    
    try:
        df = pd.read_csv(file_path, encoding='utf-16')
        
        for idx, row in df.iterrows():
            raw_json = row['raw_json']
            
            try:
                result, phases_list = algo_func(raw_json, test_date)
                
                is_logic_ok = True
                error_detail = ""
                error_type = "OK"
                
                for i in range(1, len(phases_list)-1):
                    current_p = phases_list[i]
                    next_p = phases_list[i+1]
                    
                    if next_p < current_p or (next_p - current_p) > 1:
                        allowed_exception = (current_p in [3, 4] and next_p in [3, 4])
                        if not allowed_exception:
                            is_logic_ok = False
                            if next_p < current_p:
                                error_type = "REVERSE"
                                error_detail = f"Уменьшение: {current_p} -> {next_p}"
                            else:
                                error_type = "SKIP"
                                error_detail = f"Скачок: {current_p} -> {next_p}"
                            break
                            
                results_log_personality.append({
                    'company': company,
                    'row_idx': idx,
                    'logic_status': 'OK' if is_logic_ok else 'BAD_SEQUENCE',
                    'error_type': error_type,
                    'error_info': error_detail,
                    'phases_path': str(phases_list)
                })
                
            except Exception as e:
                results_log_personality.append({
                    'company': company,
                    'row_idx': idx,
                    'logic_status': 'CRASH',
                    'error_type': 'CRASH',
                    'error_info': str(e),
                    'phases_path': ''
                })

            try:
                result_uni, phases_list_uni = algorithm_ALL(raw_json, test_date)
                
                is_logic_ok_uni = True
                error_detail_uni = ""
                error_type_uni = "OK"
                
                for i in range(1, len(phases_list_uni)-1):
                    current_p = phases_list_uni[i]
                    next_p = phases_list_uni[i+1]
                    
                    if next_p < current_p or (next_p - current_p) > 1:
                        allowed_exception = (current_p in [3, 4] and next_p in [3, 4])
                        if not allowed_exception:
                            is_logic_ok_uni = False
                            if next_p < current_p:
                                error_type_uni = "REVERSE"
                                error_detail_uni = f"Уменьшение: {current_p} -> {next_p}"
                            else:
                                error_type_uni = "SKIP"
                                error_detail_uni = f"Скачок: {current_p} -> {next_p}"
                            break
                            
                results_log_uni.append({
                    'company': company,
                    'row_idx': idx,
                    'logic_status': 'OK' if is_logic_ok_uni else 'BAD_SEQUENCE',
                    'error_type': error_type_uni,
                    'error_info': error_detail_uni,
                    'phases_path': str(phases_list_uni)
                })
                
            except Exception as e:
                results_log_uni.append({
                    'company': company,
                    'row_idx': idx,
                    'logic_status': 'CRASH',
                    'error_type': 'CRASH',
                    'error_info': str(e),
                    'phases_path': ''
                })
                
    except Exception as e:
        print(f"Не удалось открыть или обработать файл {file_path}: {e}")

# Сохраняем отчеты
df_personality = pd.DataFrame(results_log_personality)
df_personality.to_csv("report_personality.csv", index=False, encoding='utf-8')

df_uni = pd.DataFrame(results_log_uni)
df_uni.to_csv("report_universal.csv", index=False, encoding='utf-8')


for algo_name, df_report in [("Персональные алгоритмы", df_personality), ("Универсальный алгоритм (ALL)", df_uni)]:
    print(f"\n{algo_name}:")
    
    total_rows = len(df_report)
    if total_rows == 0:
        print("  Данные для анализа отсутствуют.")
        continue
        
    ok_count = sum(df_report['error_type'] == 'OK')
    skip_count = sum(df_report['error_type'] == 'SKIP')
    reverse_count = sum(df_report['error_type'] == 'REVERSE')
                
    print(f"  Всего обработано строк: {total_rows}")
    print(f"  Успешные цепочки (OK): {ok_count} ({ok_count/total_rows*100:.1f}%)")
    print(f"  Скачки через фазы (Пропуски): {skip_count}")
    print(f"  Уменьшение фазы (Обратный ход): {reverse_count}")
