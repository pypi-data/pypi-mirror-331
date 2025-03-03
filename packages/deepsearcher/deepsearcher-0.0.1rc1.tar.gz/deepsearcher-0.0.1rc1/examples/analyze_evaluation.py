import json
import os
import pandas as pd
#

log_dir = "../eval_logs"

idx_list = []
naive_list = []
gpt_4o_mini_list = []
gpt_4o_mini_2_list = []
o1_mini_list = []
o1_mini_2_list = []

question_list = []
for file in os.listdir(log_dir):
    if file.endswith('.json'):
        res_list = json.load(open(os.path.join(log_dir, file)))
        print(file)
        for res_dict in res_list:
            if "4o_mini(2)" in file:
                gpt_4o_mini_2_list.append(res_dict['recall']["5"])
            elif "4o_mini.json" in file:
                gpt_4o_mini_list.append(res_dict['recall']["5"])
            elif "o1_mini(2)" in file:
                o1_mini_2_list.append(res_dict['recall']["5"])
            elif "o1_mini.json" in file:
                o1_mini_list.append(res_dict['recall']["5"])
                naive_list.append(res_dict['recall_naive']['5'])
                question_list.append(res_dict['question'])
                idx_list.append(res_dict['idx'])



data = {
    "idx": idx_list,
    'question': question_list,
    'naive_recall_at_5': naive_list,
    'recall_at_5-gpt_4o_mini': gpt_4o_mini_list,
    'recall_at_5-gpt_4o_mini(2)': gpt_4o_mini_2_list,
    'recall_at_5-o1_mini': o1_mini_list,
    'recall_at_5-o1_mini(2)': o1_mini_2_list,
}
df = pd.DataFrame(data)

csv_file_path = 'output.csv'
df.to_csv(csv_file_path, index=False)

print(f"DataFrame 已成功写入 {csv_file_path}")