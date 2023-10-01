import pandas as pd
from utils.file_util import FileUtil
import tqdm
def get_line_of_code(source_code):
    lines = source_code.split('\n')
    return len(lines)

function_base_directory = '../data/function_base'
all_num = 0
with_comment_nums = 0
no_class_num = 0
function_base_dirs = FileUtil.subdirectories(function_base_directory)
for function_base_dir in tqdm.tqdm(function_base_dirs):
    function_base_path = function_base_dir + '/function_base.csv'
    test_case_path = function_base_dir + '/test_case.csv'

    function_base = pd.read_csv(function_base_path)
    # function_num = len(function_base)
    # function_base_with_no_class = function_base[function_base['class'].isna()]
    #
    # # function_base_with_comment = function_base.dropna(subset=['comment'])
    #
    # all_num += function_num
    # function_base_with_no_class_num = len(function_base_with_no_class)
    # no_class_num += function_base_with_no_class_num
    # # function_num_with_comment = len(function_base_with_comment)
    # # with_comment_nums += function_num_with_comment

    function_base_with_comment = function_base.dropna(subset=['comment'])
    function_base_with_comment['line_count'] = function_base_with_comment['comment_free_source_code'].apply(
        get_line_of_code)
    test_data = function_base_with_comment[function_base_with_comment['line_count'] < 25]

    test_data = test_data[test_data['is_empty_function'] == False]
    test_data = test_data[test_data['class'].isna()]
    all_num += len(test_data)

a = 1