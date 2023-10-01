import pandas as pd
from utils.file_util import FileUtil
import tqdm
from utils.code_util import CodeUtil
import random

def get_line_of_code(source_code):
    lines = source_code.split('\n')
    return len(lines)

def get_test_cases_for_each_repo(function_base_directory):
    all_num = 0
    function_base_dirs = FileUtil.subdirectories(function_base_directory)
    for function_base_dir in tqdm.tqdm(function_base_dirs):
        function_base_path = function_base_dir + '/function_base.csv'
        test_case_path = function_base_dir + '/test_case.csv'

        function_base = pd.read_csv(function_base_path)
        function_base_with_comment = function_base.dropna(subset=['comment'])
        function_base_with_comment['line_count'] = function_base_with_comment['comment_free_source_code'].apply(get_line_of_code)
        test_data = function_base_with_comment[function_base_with_comment['line_count'] < 25]

        test_data = test_data[test_data['is_empty_function'] == False]
        test_data = test_data[test_data['class'].isna()]
        if len(test_data) > 25:
            random_number = random.randint(5, 25)
            test_data = test_data.sample(n=random_number)

        all_num += len(test_data)
        test_data.to_csv(test_case_path, index=False)


if __name__ == '__main__':
    function_base_directory = '../data/function_base'
    get_test_cases_for_each_repo(function_base_directory)