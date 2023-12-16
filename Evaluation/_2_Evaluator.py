from utils.file_util import FileUtil
from ast import literal_eval
import numpy as np
import pandas as pd
from pipelines.input_construction import UserInput
from pipelines.code_generator import CodeGenerator
from utils.code_util import CodeUtil
from pipelines.function_retriever import FunctionRetriever
import tqdm
import re
import os

class Evaluator:


    @staticmethod
    def evaluationRQ1(function_base_dir, saved_result_path):
        if os.path.exists(saved_result_path):
            RQ1_result = pd.read_csv(saved_result_path)
        else:
            RQ1_result = pd.DataFrame()
        repos_function_base_dir_list = FileUtil.subdirectories(function_base_dir)
        for code_repo_base_folder in repos_function_base_dir_list:
            normal_and_five_local_aware = Evaluator.normal_and_five_local_aware_results(code_repo_base_folder, RQ1_result)
            RQ1_result = pd.concat([RQ1_result, normal_and_five_local_aware], ignore_index=True)
            RQ1_result.to_csv(saved_result_path, index=False)
            break

    @staticmethod
    def evaluationRQ3(function_base_dir, saved_result_path, RQ1_Result_path):
        RQ1_Result = pd.read_csv(RQ1_Result_path)

        if os.path.exists(saved_result_path):
            RQ3_result = pd.read_csv(saved_result_path)
        else:
            RQ3_result = pd.DataFrame()
        repos_function_base_dir_list = FileUtil.subdirectories(function_base_dir)
        for code_repo_base_folder in repos_function_base_dir_list:
            single_repo_result = Evaluator.AAAGen(code_repo_base_folder, RQ3_result, RQ1_Result)
            RQ3_result = pd.concat([RQ3_result, single_repo_result], ignore_index=True)
        RQ3_result.to_csv(saved_result_path, index=False)

    @staticmethod
    def normal_and_five_local_aware_results(function_base_dir, RQ1_result):

        function_base_path = function_base_dir + '/function_base.csv'
        test_case_path = function_base_dir + '/test_case.csv'
        third_party_libs_path = function_base_dir + '/third_party_libraries.npy'



        function_base = pd.read_csv(function_base_path)
        test_case = pd.read_csv(test_case_path)

        cases = {'repo name': [], 'file_path': [], 'relative_file_path': [], 'fully_qualified_name':[], 'comment': [], 'raw_source_code': [], 'comment_free_source_code': [],
                 'normal_gen_prompt': [], 'normal_gen_code': [], 'pure_normal_gen_code': [],
                 'local_aware_LF_prompt': [], 'local_aware_LF_code': [], 'pure_local_aware_LF_code': [],
                 'LF_InitFC_prompt': [], 'LF_InitFC_code': [], 'pure_LF_InitFC_code': [],
                 'LF_InitFC_Var_prompt': [], 'LF_InitFC_Var_code': [], 'pure_LF_InitFC_Var_code': [],
                 'LF_InitFC_Var_FP_prompt': [], 'LF_InitFC_Var_FP_code': [], 'pure_LF_InitFC_Var_FP_code': [],
                 }

        num = 0
        function_base['code_embedding'] = function_base['code_embedding'].apply(literal_eval).apply(np.array)
        function_base['summary_embedding'] = function_base['summary_embedding'].apply(literal_eval).apply(np.array)


        for _, function_info in tqdm.tqdm(function_base.iterrows(), total=function_base.shape[0]):
            if num > 1:
                break
            repo_name = function_info['repo name']
            comment = function_info['comment']
            file_path = function_info['file_path']
            fully_qualified_name = function_info['fully_qualified_name']
            comment_free_source_code = function_info['comment_free_source_code']
            if len(RQ1_result) == 0:
                pass
            else:
                sameLine_in_RQ1_result = RQ1_result[(RQ1_result['file_path'] == file_path) & (RQ1_result['fully_qualified_name'] == fully_qualified_name)]
                if len(sameLine_in_RQ1_result) >= 1:
                    continue

            #检查function_dataset中是否存在同样的行
            sameLine = test_case[(test_case['file_path'] == file_path) &
                                        (test_case['fully_qualified_name'] == fully_qualified_name)]
            if len(sameLine) >= 1:
                pass
            else:
                continue

            try:

                userInput = UserInput(function_info, function_base)


                normal_gen_prompt = userInput.input_prompt_construction_for_normal_gen()
                local_aware_LF_prompt = userInput.input_prompt_construction_for_LocalAware_LF()
                LF_InitFC_prompt = userInput.input_prompt_construction_for_LocalAware_LF_InitFC()
                LF_InitFC_Var_prompt = userInput.input_prompt_construction_for_LocalAware_LF_InitFC_Var()
                LF_InitFC_Var_FP_prompt = userInput.input_prompt_construction_for_LocalAware_LF_InitFC_Var_FP()

                normal_gen_code = CodeGenerator.generate(normal_gen_prompt)
                pure_normal_gen_code = CodeUtil.remove_comments(normal_gen_code)

                local_aware_LF_code = CodeGenerator.generate(local_aware_LF_prompt)
                pure_local_aware_LF_code = CodeUtil.remove_comments(local_aware_LF_code)

                LF_InitFC_code = CodeGenerator.generate(LF_InitFC_prompt)
                pure_LF_InitFC_code = CodeUtil.remove_comments(LF_InitFC_code)

                LF_InitFC_Var_code = CodeGenerator.generate(LF_InitFC_Var_prompt)
                pure_LF_InitFC_Var_code = CodeUtil.remove_comments(LF_InitFC_Var_code)

                LF_InitFC_Var_FP_code = CodeGenerator.generate(LF_InitFC_Var_FP_prompt)
                pure_LF_InitFC_Var_FP_code = CodeUtil.remove_comments(LF_InitFC_Var_FP_code)


                cases['repo name'].append(repo_name)
                cases['file_path'].append(file_path)
                cases['relative_file_path'].append(function_info['relative_file_path'])
                cases['fully_qualified_name'].append(fully_qualified_name)
                cases['comment'].append(comment)
                cases['raw_source_code'].append(function_info['raw_source_code'])
                cases['comment_free_source_code'].append(comment_free_source_code)
                cases['normal_gen_prompt'].append(normal_gen_prompt)
                cases['normal_gen_code'].append(normal_gen_code)
                cases['pure_normal_gen_code'].append(pure_normal_gen_code)
                cases['local_aware_LF_prompt'].append(local_aware_LF_prompt)
                cases['local_aware_LF_code'].append(local_aware_LF_code)
                cases['pure_local_aware_LF_code'].append(pure_local_aware_LF_code)

                cases['LF_InitFC_prompt'].append(LF_InitFC_prompt)
                cases['LF_InitFC_code'].append(LF_InitFC_code)
                cases['pure_LF_InitFC_code'].append(pure_LF_InitFC_code)

                cases['LF_InitFC_Var_prompt'].append(LF_InitFC_Var_prompt)
                cases['LF_InitFC_Var_code'].append(LF_InitFC_Var_code)
                cases['pure_LF_InitFC_Var_code'].append(pure_LF_InitFC_Var_code)


                cases['LF_InitFC_Var_FP_prompt'].append(LF_InitFC_Var_FP_prompt)
                cases['LF_InitFC_Var_FP_code'].append(LF_InitFC_Var_FP_code)
                cases['pure_LF_InitFC_Var_FP_code'].append(pure_LF_InitFC_Var_FP_code)


                num += 1
            except:
                print('error when handling {}, FQN: {}'.format(file_path, function_info['fully_qualified_name']))

        print('num: {}'.format(num))

        df_cases = pd.DataFrame(cases)
        return df_cases

    @staticmethod
    def AAAGen(function_base_dir, RQ3_result, RQ1_Result):

        function_base_path = function_base_dir + '/function_base.csv'
        test_case_path = function_base_dir + '/test_case.csv'
        third_party_libs_path = function_base_dir + '/third_party_libraries.npy'

        function_base = pd.read_csv(function_base_path)
        test_case = pd.read_csv(test_case_path)
        third_party_libs = FileUtil.read_npy_to_list(third_party_libs_path)

        cases = {'repo name': [], 'file_path': [], 'relative_file_path': [], 'fully_qualified_name': [], 'comment': [],
                 'raw_source_code': [], 'comment_free_source_code': [],
                 'LF_InitFC_repo_aware_5_lib_prompt': [], 'LF_InitFC_repo_aware_5_lib_code': [], 'pure_LF_InitFC_repo_aware_5_lib_code': []
                 }

        num = 0
        function_base['code_embedding'] = function_base['code_embedding'].apply(literal_eval).apply(np.array)
        function_base['summary_embedding'] = function_base['summary_embedding'].apply(literal_eval).apply(np.array)

        for _, function_info in tqdm.tqdm(function_base.iterrows(), total=function_base.shape[0]):

            repo_name = function_info['repo name']
            comment = function_info['comment']
            file_path = function_info['file_path']
            fully_qualified_name = function_info['fully_qualified_name']
            comment_free_source_code = function_info['comment_free_source_code']

            if len(RQ3_result) == 0:
                pass
            else:
                sameLine_in_RQ3_result = RQ3_result[(RQ3_result['file_path'] == file_path) & (RQ3_result['fully_qualified_name'] == fully_qualified_name)]
                if len(sameLine_in_RQ3_result) >= 1:
                    continue

            sameLine = test_case[(test_case['file_path'] == file_path) &
                                 (test_case['fully_qualified_name'] == fully_qualified_name)]
            if len(sameLine) >= 1:
                pass
            else:
                continue

            # Use the re.escape() function to escape special characters in file paths
            escaped_file_path = re.escape(file_path)

            try:

                userInput = UserInput(function_info, function_base)

                normal_gen_code = RQ1_Result[(RQ1_Result['file_path'] == file_path) &
                                        (RQ1_Result['fully_qualified_name'] == fully_qualified_name)]['normal_gen_code'].tolist()[0]

                pure_normal_gen_code = CodeUtil.remove_comments(normal_gen_code)

                function_base_for_retrieval = function_base[~function_base['file_path'].str.contains(escaped_file_path)]
                function_base_for_retrieval = function_base_for_retrieval[
                    function_base_for_retrieval['is_empty_function'] == False]
                function_base_for_retrieval = function_base_for_retrieval[
                    function_base_for_retrieval['function_name'] != '__init__']

                retrieved_functions = FunctionRetriever.retrieve_functions_for_Evaluation(pure_normal_gen_code, comment,
                                                                                          function_base_for_retrieval,
                                                                                          top_k=5)
                reusable_functions = FunctionRetriever.get_reusable_functions_for_Evaluation(retrieved_functions)


                LF_InitFC_repo_aware_5_lib_prompt = userInput.input_prompt_construction_for_Repo_Lib_Aware_LF_InitFC(reusable_functions,
                                                                                                 third_party_libs)
                LF_InitFC_repo_aware_5_lib_code = CodeGenerator.generate(LF_InitFC_repo_aware_5_lib_prompt)
                pure_LF_InitFC_repo_aware_5_lib_code = CodeUtil.remove_comments(LF_InitFC_repo_aware_5_lib_code)


                cases['repo name'].append(repo_name)
                cases['file_path'].append(file_path)
                cases['relative_file_path'].append(function_info['relative_file_path'])
                cases['fully_qualified_name'].append(fully_qualified_name)
                cases['comment'].append(comment)
                cases['raw_source_code'].append(function_info['raw_source_code'])
                cases['comment_free_source_code'].append(comment_free_source_code)
                cases['LF_InitFC_repo_aware_5_lib_prompt'].append(LF_InitFC_repo_aware_5_lib_prompt)
                cases['LF_InitFC_repo_aware_5_lib_code'].append(LF_InitFC_repo_aware_5_lib_code)
                cases['pure_LF_InitFC_repo_aware_5_lib_code'].append(pure_LF_InitFC_repo_aware_5_lib_code)

                num += 1
            except:
                print('error when handling {}, FQN: {}'.format(file_path, function_info['fully_qualified_name']))

        print('num: {}'.format(num))

        df_cases = pd.DataFrame(cases)
        return df_cases

    @staticmethod
    def four_different_top_k_repo_aware(function_base_dir, RQ2_result, RQ1_Result):

        function_base_path = function_base_dir + '/function_base.csv'
        test_case_path = function_base_dir + '/test_case.csv'
        third_party_libs_path = function_base_dir + '/third_party_libraries.npy'

        function_base = pd.read_csv(function_base_path)
        test_case = pd.read_csv(test_case_path)

        cases = {'repo name': [], 'file_path': [], 'relative_file_path': [], 'fully_qualified_name': [], 'comment': [],
                 'raw_source_code': [], 'comment_free_source_code': [],
                 'LF_InitFC_repo_aware_1_prompt': [], 'LF_InitFC_repo_aware_1_code': [],
                 'pure_LF_InitFC_repo_aware_1_code': [],
                 'LF_InitFC_repo_aware_5_prompt': [], 'LF_InitFC_repo_aware_5_code': [], 'pure_LF_InitFC_repo_aware_5_code': [],
                 'LF_InitFC_repo_aware_10_prompt': [], 'LF_InitFC_repo_aware_10_code': [],
                 'pure_LF_InitFC_repo_aware_10_code': [],
                 'LF_InitFC_repo_aware_15_prompt': [], 'LF_InitFC_repo_aware_15_code': [],
                 'pure_LF_InitFC_repo_aware_15_code': [],

                 }

        num = 0
        function_base['code_embedding'] = function_base['code_embedding'].apply(literal_eval).apply(np.array)
        function_base['summary_embedding'] = function_base['summary_embedding'].apply(literal_eval).apply(np.array)

        for _, function_info in tqdm.tqdm(function_base.iterrows(), total=function_base.shape[0]):

            repo_name = function_info['repo name']
            comment = function_info['comment']
            file_path = function_info['file_path']
            fully_qualified_name = function_info['fully_qualified_name']
            comment_free_source_code = function_info['comment_free_source_code']
            if len(RQ2_result) == 0:
                pass
            else:
                sameLine_in_RQ2_result = RQ2_result[
                    (RQ2_result['file_path'] == file_path) & (RQ2_result['fully_qualified_name'] == fully_qualified_name)]
                if len(sameLine_in_RQ2_result) >= 1:
                    continue


            sameLine = test_case[(test_case['file_path'] == file_path) &
                                 (test_case['fully_qualified_name'] == fully_qualified_name)]
            if len(sameLine) >= 1:
                pass
            else:
                continue

            escaped_file_path = re.escape(file_path)


            try:

                userInput = UserInput(function_info, function_base)


                normal_gen_code = RQ1_Result[(RQ1_Result['file_path'] == file_path) &
                                        (RQ1_Result['fully_qualified_name'] == fully_qualified_name)]['normal_gen_code'].tolist()[0]

                pure_normal_gen_code = CodeUtil.remove_comments(normal_gen_code)

                function_base_for_retrieval = function_base[~function_base['file_path'].str.contains(escaped_file_path)]
                function_base_for_retrieval = function_base_for_retrieval[
                    function_base_for_retrieval['is_empty_function'] == False]
                function_base_for_retrieval = function_base_for_retrieval[
                    function_base_for_retrieval['function_name'] != '__init__']


                retrieved_functions = FunctionRetriever.retrieve_functions_for_Evaluation(pure_normal_gen_code, comment,
                                                                                          function_base_for_retrieval,
                                                                                          top_k=1)
                reusable_functions = FunctionRetriever.get_reusable_functions_for_Evaluation(retrieved_functions)
                LF_InitFC_repo_aware_1_prompt = userInput.input_prompt_construction_for_RepoAware_LF_InitFC(reusable_functions)
                LF_InitFC_repo_aware_1_code = CodeGenerator.generate(LF_InitFC_repo_aware_1_prompt)
                pure_LF_InitFC_repo_aware_1_code = CodeUtil.remove_comments(LF_InitFC_repo_aware_1_code)



                retrieved_functions = FunctionRetriever.retrieve_functions_for_Evaluation(pure_normal_gen_code, comment,
                                                                                          function_base_for_retrieval,
                                                                                          top_k=5)
                reusable_functions = FunctionRetriever.get_reusable_functions_for_Evaluation(retrieved_functions)
                LF_InitFC_repo_aware_5_prompt = userInput.input_prompt_construction_for_RepoAware_LF_InitFC(reusable_functions)
                LF_InitFC_repo_aware_5_code = CodeGenerator.generate(LF_InitFC_repo_aware_5_prompt)
                pure_LF_InitFC_repo_aware_5_code = CodeUtil.remove_comments(LF_InitFC_repo_aware_5_code)


                retrieved_functions = FunctionRetriever.retrieve_functions_for_Evaluation(pure_normal_gen_code, comment,
                                                                                          function_base_for_retrieval,
                                                                                          top_k=10)
                reusable_functions = FunctionRetriever.get_reusable_functions_for_Evaluation(retrieved_functions)
                LF_InitFC_repo_aware_10_prompt = userInput.input_prompt_construction_for_RepoAware_LF_InitFC(reusable_functions)
                LF_InitFC_repo_aware_10_code = CodeGenerator.generate(LF_InitFC_repo_aware_10_prompt)
                pure_LF_InitFC_repo_aware_10_code = CodeUtil.remove_comments(LF_InitFC_repo_aware_10_code)

                retrieved_functions = FunctionRetriever.retrieve_functions_for_Evaluation(pure_normal_gen_code, comment,
                                                                                          function_base_for_retrieval,
                                                                                          top_k=15)
                reusable_functions = FunctionRetriever.get_reusable_functions_for_Evaluation(retrieved_functions)
                LF_InitFC_repo_aware_15_prompt = userInput.input_prompt_construction_for_RepoAware_LF_InitFC(reusable_functions)
                LF_InitFC_repo_aware_15_code = CodeGenerator.generate(LF_InitFC_repo_aware_15_prompt)
                pure_LF_InitFC_repo_aware_15_code = CodeUtil.remove_comments(LF_InitFC_repo_aware_15_code)


                cases['repo name'].append(repo_name)
                cases['file_path'].append(file_path)
                cases['relative_file_path'].append(function_info['relative_file_path'])
                cases['fully_qualified_name'].append(fully_qualified_name)
                cases['comment'].append(comment)
                cases['raw_source_code'].append(function_info['raw_source_code'])
                cases['comment_free_source_code'].append(comment_free_source_code)
                cases['LF_InitFC_repo_aware_1_prompt'].append(LF_InitFC_repo_aware_1_prompt)
                cases['LF_InitFC_repo_aware_1_code'].append(LF_InitFC_repo_aware_1_code)
                cases['pure_LF_InitFC_repo_aware_1_code'].append(pure_LF_InitFC_repo_aware_1_code)

                cases['LF_InitFC_repo_aware_5_prompt'].append(LF_InitFC_repo_aware_5_prompt)
                cases['LF_InitFC_repo_aware_5_code'].append(LF_InitFC_repo_aware_5_code)
                cases['pure_LF_InitFC_repo_aware_5_code'].append(pure_LF_InitFC_repo_aware_5_code)

                cases['LF_InitFC_repo_aware_10_prompt'].append(LF_InitFC_repo_aware_10_prompt)
                cases['LF_InitFC_repo_aware_10_code'].append(LF_InitFC_repo_aware_10_code)
                cases['pure_LF_InitFC_repo_aware_10_code'].append(pure_LF_InitFC_repo_aware_10_code)

                cases['LF_InitFC_repo_aware_15_prompt'].append(LF_InitFC_repo_aware_15_prompt)
                cases['LF_InitFC_repo_aware_15_code'].append(LF_InitFC_repo_aware_15_code)
                cases['pure_LF_InitFC_repo_aware_15_code'].append(pure_LF_InitFC_repo_aware_15_code)

                num += 1
            except:
                print('error when handling {}, FQN: {}'.format(file_path, function_info['fully_qualified_name']))

        print('num: {}'.format(num))

        df_cases = pd.DataFrame(cases)
        return df_cases

    @staticmethod
    def evaluationRQ2(function_base_dir, saved_result_path, RQ1_Result_path):
        RQ1_Result = pd.read_csv(RQ1_Result_path)

        if os.path.exists(saved_result_path):
            RQ2_result = pd.read_csv(saved_result_path)
        else:
            RQ2_result = pd.DataFrame()
        repos_function_base_dir_list = FileUtil.subdirectories(function_base_dir)
        for code_repo_base_folder in repos_function_base_dir_list:
            single_repo_result = Evaluator.four_different_top_k_repo_aware(code_repo_base_folder, RQ2_result, RQ1_Result)
            RQ2_result = pd.concat([RQ2_result, single_repo_result], ignore_index=True)
        RQ2_result.to_csv(saved_result_path, index=False)


if __name__ == '__main__':
    function_bases_dir = '../data/function_base/'


    RQ1_saved_result_path = '../saved_results/Normal_5LocalInfo_Gen.csv'
    Evaluator.evaluationRQ1(function_bases_dir, RQ1_saved_result_path)

    saved_result_path = '../saved_results/Four_Repo_Aware.csv'
    Evaluator.evaluationRQ2(function_bases_dir, saved_result_path, RQ1_saved_result_path)

    saved_result_path = '../saved_results/AAA_result.csv'
    Evaluator.evaluationRQ3(function_bases_dir, saved_result_path, RQ1_saved_result_path)



