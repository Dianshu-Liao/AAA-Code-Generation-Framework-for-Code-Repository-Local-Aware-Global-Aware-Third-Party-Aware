from pipelines.repo_data_extraction import FunctionBaseConstruction
from utils.file_util import FileUtil
import os

def get_all_repos_function_base(code_repo_dir, function_base_dir):

    code_repo_dir_list = FileUtil.subdirectories(code_repo_dir)


    for each_code_repo_dir in code_repo_dir_list:

        code_repo_name = each_code_repo_dir.replace(code_repo_dir + '\\', '')
        code_repo_base_folder = function_base_dir + code_repo_name
        if os.path.exists(code_repo_base_folder + '/function_base.csv'):
            continue
        FileUtil.create_new_folder(code_repo_base_folder)
        function_base_path = code_repo_base_folder + '/function_base.csv'
        third_party_libraries_path = code_repo_base_folder + '/third_party_libraries.npy'
        # function_base construction (only need to run once)
        code_repo_processor = FunctionBaseConstruction()
        code_repo_processor.extract_function_base(each_code_repo_dir, function_base_path, third_party_libraries_path)

if __name__ == '__main__':
    code_repo_dir = '../dataset'
    function_base_dir = '../data/function_base/'

    get_all_repos_function_base(code_repo_dir, function_base_dir)
