import pandas as pd
import re
from utils.file_util import FileUtil

file_path = '../saved_results/Four_Repo_Aware.csv'
df = pd.read_csv(file_path)

def handle_prompt(prompt):
    global_fun = prompt.split('#global_function_in_other_file')[-1]
    pattern = r'function\d+\{([^}]+)\}'
    functions = re.findall(pattern, global_fun)
    return len(functions)

def statistic_retrieved_global_functions_num():
    num_repo1 = 0
    num_repo5 = 0
    num_repo10 = 0
    num_repo15 = 0


    for _, row in df.iterrows():
        Repo1_prompt = eval(row['LF_InitFC_repo_aware_1_prompt'])[-1]['content']
        Repo5_prompt = eval(row['LF_InitFC_repo_aware_5_prompt'])[-1]['content']
        Repo10_prompt = eval(row['LF_InitFC_repo_aware_10_prompt'])[-1]['content']
        Repo15_prompt = eval(row['LF_InitFC_repo_aware_15_prompt'])[-1]['content']

        funRepo1_nums = handle_prompt(Repo1_prompt)
        funRepo5_nums = handle_prompt(Repo5_prompt)
        funRepo10_nums = handle_prompt(Repo10_prompt)
        funRepo15_nums = handle_prompt(Repo15_prompt)


        num_repo1 += funRepo1_nums
        num_repo5 += funRepo5_nums
        num_repo10 += funRepo10_nums
        num_repo15 += funRepo15_nums

    print('avg repo 1 f num: {}'.format(num_repo1/len(df)))
    print('avg repo 5 f num: {}'.format(num_repo5/len(df)))
    print('avg repo 10 f num: {}'.format(num_repo10/len(df)))
    print('avg repo 15 f num: {}'.format(num_repo15/len(df)))


def statistic_py_files():
    dataset_path = '../dataset'

    py_file_nums = 0

    all_sub_directories = FileUtil.subdirectories(dataset_path)
    for directory in all_sub_directories:
        nums = FileUtil.count_python_files(directory)
        py_file_nums += nums
    avg = py_file_nums / len(all_sub_directories)
    print('avg py file nums of each code repository: {}'.format(avg))

if __name__ == '__main__':
    statistic_retrieved_global_functions_num()
    statistic_py_files()