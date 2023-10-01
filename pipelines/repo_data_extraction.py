from utils.file_util import FileUtil
from utils.FunctionExtractor import extract_function_info
from utils.LocalInfoExtractor import get_variables_from_file
import pandas as pd
from pipelines.code_summarization import CodeSummarization
import tiktoken
from utils.code_util import CodeUtil
from config import Config
import tqdm
from openai.embeddings_utils import get_embedding
import numpy as np

class FunctionBaseConstruction:

    def __init__(self):
        # embedding model parameters
        self.embedding_model = Config.embedding_model
        self.embedding_encoding = Config.embedding_encoding  # this the encoding for text-embedding-ada-002
        self.max_tokens = Config.embedding_max_tokens # the maximum for text-embedding-ada-002 is 8191
        self.encoding = tiktoken.get_encoding(self.embedding_encoding)


    def truncate_long_code(self, code):
        tokens = self.encoding.encode(code, disallowed_special=())
        if len(tokens) > self.max_tokens:
            return self.encoding.decode(tokens[:self.max_tokens])
        return code

    def get_embeddings_of_description(self, function_base):
        # 如果code snippet太长，就取前8000个token
        function_base['summary'] = function_base['summary'].apply(self.truncate_long_code)
        function_base['summary_n_tokens'] = function_base['summary'].apply(lambda x: len(self.encoding.encode(x, disallowed_special=())))


        embeddings = []

        for index, row in tqdm.tqdm(function_base.iterrows(), total=function_base.shape[0], desc="Embedding summary..."):
            summary = row['summary']
            embedding = get_embedding(summary, engine=self.embedding_model)
            embeddings.append(embedding)


        function_base['summary_embedding'] = embeddings

        return function_base

    def get_embedding_of_code(self, function_base):
        # 如果code snippet太长，就取前8000个token
        function_base['comment_free_source_code'] = function_base['comment_free_source_code'].apply(self.truncate_long_code)
        function_base['n_tokens'] = function_base['comment_free_source_code'].apply(lambda x: len(self.encoding.encode(x, disallowed_special=())))

        embeddings = []

        for index, row in tqdm.tqdm(function_base.iterrows(), total=function_base.shape[0], desc="Embedding codes..."):
            comment_free_source_code = row['comment_free_source_code']
            embedding = get_embedding(comment_free_source_code, engine=self.embedding_model)
            embeddings.append(embedding)

        function_base['code_embedding'] = embeddings

        return function_base

    def get_embeddings_of_function_base(self, function_base, function_base_path):
        function_base = self.get_embedding_of_code(function_base)
        function_base = self.get_embeddings_of_description(function_base)
        function_base.to_csv(function_base_path, index=False)

    def extract_function_base(self, directory, function_base_path, third_party_libraries_path):


        function_base = self.extract_basic_function_base(directory)

        self.get_third_party_libraries(directory, function_base, third_party_libraries_path)
        self.get_embeddings_of_function_base(function_base, function_base_path)



    def get_third_party_libraries(self, directory, function_base, third_party_libraries_path):
        local_repo_code_FQNs = function_base['fully_qualified_name'].tolist()
        all_fqn_module_names = []
        for local_repo_code_FQN in local_repo_code_FQNs:
            module_name = local_repo_code_FQN.split('.')[0]
            all_fqn_module_names.append(module_name)
        all_module_names = FileUtil.all_module_names(directory)
        all_module_names = list(set(all_fqn_module_names + all_module_names))

        all_import_statements = CodeUtil.all_import_statements(directory)
        third_party_FQNs = []
        for import_statement in all_import_statements:
            if import_statement in local_repo_code_FQNs:
                pass
            else:
                third_party_FQNs.append(import_statement)
        third_party_libraries = []
        for FQN in third_party_FQNs:
            third_party_libraries.append(FQN.split('.')[0])
        third_party_libraries = list(set(third_party_libraries) - set(all_module_names))
        third_party_libraries = np.array(third_party_libraries)
        np.save(third_party_libraries_path, third_party_libraries)


    def extract_basic_function_base(self, directory):

        dict_function_base = {'repo name': [], 'file_path': [], 'relative_file_path': [], 'fully_qualified_name': [], 'function_name': [],
                              'function signature': [], 'raw_source_code': [],'comment_free_source_code': [], 'class': [], 'is_empty_function': [],
                              'summary': [],
                              'comment': [], 'local variables': [],
                              }
        py_files = FileUtil.all_py_files(directory)
        all_files_num = FileUtil.all_files_num(directory)
        repo_name = directory.split('\\')[1]

        for py_file in tqdm.tqdm(py_files, total=all_files_num, desc="Extracting function base..."):
            # content = FileUtil.read_py_file(py_file)
            # if content == '﻿':
            #     continue
            variables = get_variables_from_file(py_file)
            module_FQN = py_file.replace(directory+'\\', '').replace('\\', '.').replace('.py', '')
            # get_all_functions
            print(py_file)
            functions_info = extract_function_info(py_file)
            for function_info in functions_info:
                function_name = function_info['name']
                raw_source_code = function_info['source']
                comment_free_source_code = CodeUtil.remove_comments(raw_source_code)
                is_empty = CodeUtil.is_body_empty_or_only_pass(comment_free_source_code)
                summary = CodeSummarization.code_summarization(raw_source_code)
                class_name = function_info['class']
                # start_lineno = function_info['start_lineno']
                # end_lineno = function_info['end_lineno']
                function_signature = function_info['signature']
                comment = function_info['docstring']
                relative_file_path = py_file.replace('../dataset\\', '').replace('\\', '/')
                # relative_file_path = py_file.replace('../code_repo\\', '').replace('\\', '/')
                if class_name == None:
                    fully_qualified_name = module_FQN + '.' + function_name
                else:
                    fully_qualified_name = module_FQN + '.' + class_name + '.' + function_name
                    class_name = module_FQN + '.' + class_name



                # dict_function_base['start_lineno'].append(start_lineno)
                # dict_function_base['end_lineno'].append(end_lineno)
                dict_function_base['repo name'].append(repo_name)
                dict_function_base['file_path'].append(py_file)
                dict_function_base['relative_file_path'].append(relative_file_path)
                dict_function_base['fully_qualified_name'].append(fully_qualified_name)
                dict_function_base['function_name'].append(function_name)
                dict_function_base['raw_source_code'].append(raw_source_code)
                dict_function_base['class'].append(class_name)
                dict_function_base['summary'].append(summary)
                dict_function_base['comment_free_source_code'].append(comment_free_source_code)
                dict_function_base['function signature'].append(function_signature)
                dict_function_base['comment'].append(comment)
                dict_function_base['local variables'].append(variables)
                dict_function_base['is_empty_function'].append(is_empty)

        df_function_base = pd.DataFrame(dict_function_base)
        return df_function_base




if __name__ == '__main__':



    directory = '../data/deepmind_tracr'
    function_base_path = '../data/function_base/deepmind_tracr_function_base.csv'
    third_party_libraries_path = '../data/function_base/third_party_libraries.npy'
    code_repo_processor = FunctionBaseConstruction()
    code_repo_processor.extract_function_base(directory, function_base_path, third_party_libraries_path)




