import pandas as pd
from utils.file_util import FileUtil
from utils.code_util import CodeUtil

def Precision_Recall_F1_Acc(df, label_key, predict_key):
    TP = 0
    FP = 0
    TN = 0
    FN = 0

    for _, row in df.iterrows():

        predict = str(int(row[predict_key]))
        label = str(int(row[label_key]))

        if predict == '1':
            if label == '1':
                TP += 1
            elif label == '0':
                FP += 1

        elif predict == '0':
            if label == '1':
                FN += 1

            elif label == '0':
                TN += 1

    if TP + FP == 0:
        precision = 0
    else:
        precision = TP / (TP + FP)
    if TP + FN == 0:
        recall = 0
    else:
        recall = TP / (TP + FN)
    if precision + recall == 0:
        F1 = 0
    else:
        F1 = 2 * precision * recall / (precision + recall)
    Acc = (TP + TN) / (TP + TN + FP + FN)
    print('TP: ', TP)
    print('FP: ', FP)
    print('TN: ', TN)
    print('FN: ', FN)
    print('precision: ', round(precision, 3))
    print('recall: ', round(recall, 3))
    print('F1: ', round(F1, 3))
    print('Acc: ', round(Acc, 3))

def set_non_zero_to_1(value):
    if value == '0':
        return '0'
    else:
        return '1'

def convert_lib_to_label(df):

    df['Lib_A'] = df['Lib_A'].apply(set_non_zero_to_1)
    df['Lib_A_label'] = df['Lib_A_label'].apply(set_non_zero_to_1)
    return df

def RQ1_local_testing(df_path):

    print('file {}'.format(df_path))
    print('Local Reuse Results:')
    result_df = pd.read_csv(df_path)
    Precision_Recall_F1_Acc(result_df, 'local_A_label', 'local_A')
    print('-------------------------------')

def RQ1():
    RQ1_local_testing(normal_gen_code_path)
    RQ1_local_testing(local_aware_LF_code_path)
    RQ1_local_testing(LF_InitFC_code_path)
    RQ1_local_testing(LF_InitFC_Var_code_path)
    RQ1_local_testing(LF_InitFC_Var_FP_code_path)

def RQ2_global_testing(df_path):
    print('file {}'.format(df_path))
    print('Global Reuse Results:')
    result_df = pd.read_csv(df_path)
    Precision_Recall_F1_Acc(result_df, 'global_A_label', 'global_A')
    print('-------------------------------')

def RQ2():
    RQ2_global_testing(normal_gen_code_path)
    RQ2_global_testing(LF_InitFC_repo_aware_1_code_path)
    RQ2_global_testing(LF_InitFC_repo_aware_5_code_path)
    RQ2_global_testing(LF_InitFC_repo_aware_10_code_path)
    RQ2_global_testing(LF_InitFC_repo_aware_15_code_path)

def RQ3_lib_testing(df_path):
    print('file {}'.format(df_path))
    print('Third Party Lib Results:')
    result_df = pd.read_csv(df_path)
    lib_coverage(result_df)
    result_df_for_lib = convert_lib_to_label(result_df)
    Precision_Recall_F1_Acc(result_df_for_lib, 'Lib_A_label', 'Lib_A')

def RQ3():
    RQ3_lib_testing(LF_InitFC_repo_aware_5_code_path)
    RQ3_lib_testing(LF_InitFC_repo_aware_5_lib_code_path)

def lib_coverage(df):
    imports_converage_scores = 0
    imports_converage_count_num = 0
    for _, row in df.iterrows():
        predict_imports = row['Lib_A']
        if str(predict_imports) == '0':
            continue
        repo_name = row['repo name']
        # module_names = FileUtil.get_simple_subdirectories('../dataset/{}'.format(repo_name))

        third_party_libs_path = '../data/function_base/' + repo_name + '/third_party_libraries.npy'
        third_party_libs = FileUtil.read_npy_to_list(third_party_libs_path)
        _, fqns = CodeUtil.remove_and_return_imports_no_need_for_compile(predict_imports)
        # fqns = [item for item in fqns if item.startswith(repo_name)]
        fqn_list = []
        for fqn in fqns:
            fqn = fqn.split('.')[0]
            if fqn == repo_name:
                pass
            # if fqn in module_names:
            #     pass
            else:
                fqn_list.append(fqn)
        fqn_list = [item for item in fqn_list if item != ""]
        fqn_list = list(set(fqn_list))
        if len(fqn_list) == 0:
            continue
        converage_num = 0
        for fqn in fqn_list:
            if fqn in third_party_libs:
                converage_num += 1
            else:
                a = 1
        coverage = converage_num / len(fqn_list)
        imports_converage_scores += coverage
        imports_converage_count_num += 1

    print('3rd party library converage: {}'.format(imports_converage_scores/imports_converage_count_num))

def get_line_of_code(source_code):
    lines = source_code.split('\n')
    return len(lines)

def ave_LOC(df, key):
    all_generated_code = df[key].to_list()
    lines_of_code = 0
    for code in all_generated_code:
        code = CodeUtil.remove_comments(code)
        line_of_code = get_line_of_code(code)
        lines_of_code += line_of_code
    print('Avg LOC : {}'.format(lines_of_code/len(df)))

def local_global_lib_aware(df):
    print('--------------------------------\nlocal')
    Precision_Recall_F1_Acc(df, 'local_A_label', 'local_A')
    print('--------------------------------\nglobal')
    Precision_Recall_F1_Acc(df, 'global_A_label', 'global_A')
    print('--------------------------------\nlibrary')
    result_df_for_lib = convert_lib_to_label(df)
    Precision_Recall_F1_Acc(result_df_for_lib, 'Lib_A_label', 'Lib_A')



def RQ4_testing(df_path, key_word):
    print('file {}'.format(df_path))

    result_df = pd.read_csv(df_path)
    lib_coverage(result_df)
    ave_LOC(result_df, key_word)
    local_global_lib_aware(result_df)

def RQ4():
    RQ4_testing(normal_gen_code_path, 'normal_gen_code')
    print()
    RQ4_testing(LF_InitFC_code_path, 'LF_InitFC_code')
    print()
    RQ4_testing(LF_InitFC_repo_aware_5_code_path, 'LF_InitFC_repo_aware_5_code')
    print()
    RQ4_testing(LF_InitFC_repo_aware_5_lib_code_path, 'LF_InitFC_repo_aware_5_lib_code')
    print()
    calling_correctness()

def FourRQs():

    print('RQ1:')
    print('---------------------------------------')
    print('---------------------------------------')
    RQ1()
    print('\n\n')

    print('RQ2:')
    print('---------------------------------------')
    print('---------------------------------------')
    RQ2()
    print('\n\n')


    print('RQ3:')
    print('---------------------------------------')
    print('---------------------------------------')
    RQ3()
    print('\n\n')

    print('RQ4:')
    print('---------------------------------------')
    print('---------------------------------------')
    RQ4()




def Precision_Recall_F1_Acc_for_calling_correctness(label_list, predict_list):

    intersection = set(label_list) & set(predict_list)
    precision = len(intersection) / len(predict_list)
    recall = len(intersection) / len(label_list)

    return precision, recall


def calling_correctness():
    print('local call correctness')
    print('file {}'.format(local_call_correctness_for_local_aware))
    result_df = pd.read_csv(local_call_correctness_for_local_aware)
    calling_correctness_local_global_aware(result_df, 'local')

    print('file {}'.format(local_call_correctness_for_global_aware))
    result_df = pd.read_csv(local_call_correctness_for_global_aware)
    calling_correctness_local_global_aware(result_df, 'local')

    print('file {}'.format(local_call_correctness_for_aaa_aware))
    result_df = pd.read_csv(local_call_correctness_for_aaa_aware)
    calling_correctness_local_global_aware(result_df, 'local')

    print('global call correctness')
    print('file {}'.format(global_call_correctness_for_global_aware))
    result_df = pd.read_csv(global_call_correctness_for_global_aware)
    calling_correctness_local_global_aware(result_df, 'global')

    print('file {}'.format(global_call_correctness_for_aaa_aware))
    result_df = pd.read_csv(global_call_correctness_for_aaa_aware)
    calling_correctness_local_global_aware(result_df, 'global')


    print('3rd party lib call correctness')
    print('file {}'.format(lib_call_correctness_for_normal_gen))
    result_df = pd.read_csv(lib_call_correctness_for_normal_gen)
    calling_correctness_lib(result_df)

    print('file {}'.format(lib_call_correctness_for_local_aware))
    result_df = pd.read_csv(lib_call_correctness_for_local_aware)
    calling_correctness_lib(result_df)

    print('file {}'.format(lib_call_correctness_for_global_aware))
    result_df = pd.read_csv(lib_call_correctness_for_global_aware)
    calling_correctness_lib(result_df)

    print('file {}'.format(lib_call_correctness_for_aaa_aware))
    result_df = pd.read_csv(lib_call_correctness_for_aaa_aware)
    calling_correctness_lib(result_df)

def calling_correctness_local_global_aware(df, keyword):
    all_precision, all_recall = 0, 0
    for _, row in df.iterrows():
        if keyword == 'local':
            predicts = row['local_A'].split('\n')
            labels = row['local_A_label'].split('\n')
        elif keyword == 'global':
            predicts = row['global_A'].split('\n')
            labels = row['global_A_label'].split('\n')
        else:
            raise ValueError('wrong keyword!')
        predicts = [item for item in predicts if item != ""]
        predicts = list(set(predicts))

        labels = [item for item in labels if item != ""]
        labels = list(set(labels))

        precision, recall = Precision_Recall_F1_Acc_for_calling_correctness(labels, predicts)

        all_precision += precision
        all_recall += recall
    avg_precision = all_precision / len(df)
    avg_recall = all_recall / len(df)
    print('avg precision: {}'.format(round(avg_precision, 3)))
    print('avg recall: {}'.format(round(avg_recall, 3)))
    print()

def calling_correctness_lib(df):
    all_precision, all_recall = 0, 0
    for _, row in df.iterrows():
        predict_imports = row['Lib_A']
        _, fqns = CodeUtil.remove_and_return_imports_no_need_for_compile(predict_imports)
        fqn_list = []
        for fqn in fqns:
            fqn = fqn.split('.')[0]
            fqn_list.append(fqn)
        fqn_list = [item for item in fqn_list if item != ""]
        fqn_list = list(set(fqn_list))

        label_imports = row['Lib_A_label']
        _, fqns = CodeUtil.remove_and_return_imports_no_need_for_compile(label_imports)
        fqn_label_list = []
        for fqn in fqns:
            fqn = fqn.split('.')[0]
            fqn_label_list.append(fqn)
        fqn_label_list = [item for item in fqn_label_list if item != ""]
        fqn_label_list = list(set(fqn_label_list))

        precision, recall = Precision_Recall_F1_Acc_for_calling_correctness(fqn_label_list, fqn_list)

        all_precision += precision
        all_recall += recall
    avg_precision = all_precision / len(df)
    avg_recall = all_recall / len(df)
    print('avg precision: {}'.format(round(avg_precision, 3)))
    print('avg recall: {}'.format(round(avg_recall, 3)))
    print()

if __name__ == '__main__':

    normal_gen_code_path = '../data/Labeling_Results/normal_gen_code_label.csv'
    local_aware_LF_code_path = '../data/Labeling_Results/local_aware_LF_code_label.csv'
    LF_InitFC_code_path = '../data/Labeling_Results/LF_InitFC_code_label.csv'
    LF_InitFC_Var_code_path = '../data/Labeling_Results/LF_InitFC_Var_code_label.csv'
    LF_InitFC_Var_FP_code_path = '../data/Labeling_Results/LF_InitFC_Var_FP_code_label.csv'
    LF_InitFC_repo_aware_1_code_path = '../data/Labeling_Results/LF_InitFC_repo_aware_1_code.csv'
    LF_InitFC_repo_aware_5_code_path = '../data/Labeling_Results/LF_InitFC_repo_aware_5_code.csv'
    LF_InitFC_repo_aware_10_code_path = '../data/Labeling_Results/LF_InitFC_repo_aware_10_code.csv'
    LF_InitFC_repo_aware_15_code_path = '../data/Labeling_Results/LF_InitFC_repo_aware_15_code.csv'
    LF_InitFC_repo_aware_5_lib_code_path = '../data/Labeling_Results/LF_InitFC_repo_aware_5_lib_code.csv'

    lib_call_correctness_for_normal_gen = '../data/Labeling_Results/Calling_Correctness/Third_Party_Lib_Call/normal_gen_code_label.csv'
    lib_call_correctness_for_local_aware = '../data/Labeling_Results/Calling_Correctness/Third_Party_Lib_Call/LF_InitFC_code_label.csv'
    lib_call_correctness_for_global_aware = '../data/Labeling_Results/Calling_Correctness/Third_Party_Lib_Call/LF_InitFC_repo_aware_5_code.csv'
    lib_call_correctness_for_aaa_aware = '../data/Labeling_Results/Calling_Correctness/Third_Party_Lib_Call/LF_InitFC_repo_aware_5_lib_code.csv'

    local_call_correctness_for_local_aware = '../data/Labeling_Results/Calling_Correctness/Local_Call/LF_InitFC_code_label.csv'
    local_call_correctness_for_global_aware = '../data/Labeling_Results/Calling_Correctness/Local_Call/LF_InitFC_repo_aware_5_code.csv'
    local_call_correctness_for_aaa_aware = '../data/Labeling_Results/Calling_Correctness/Local_Call/LF_InitFC_repo_aware_5_lib_code.csv'

    global_call_correctness_for_global_aware = '../data/Labeling_Results/Calling_Correctness/Global_Call/LF_InitFC_repo_aware_5_code.csv'
    global_call_correctness_for_aaa_aware = '../data/Labeling_Results/Calling_Correctness/Global_Call/LF_InitFC_repo_aware_5_lib_code.csv'


    FourRQs()


