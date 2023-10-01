import re

import pandas as pd
from utils.code_util import CodeUtil
from pipelines.code_generator import CodeGenerator
from config import Config
from utils.file_util import FileUtil


class UserInput:

    def __init__(self, function_info, function_base):
        self.file_path = function_info['file_path']
        self.relative_file_path = function_info['relative_file_path']
        self.fully_qualified_name = function_info['fully_qualified_name']
        self.function_name = function_info['function_name']
        self.function_signature = function_info['function signature']
        self.raw_source_code = function_info['raw_source_code']
        self.comment_free_source_code = function_info['comment_free_source_code']
        self.correspongding_class = function_info['class']
        self.comment = function_info['comment']
        self.local_variables = eval(function_info['local variables'])
        self.code_n_tokens = function_info['n_tokens']
        self.code_embedding = function_info['code_embedding']
        self.summary_n_tokens = function_info['summary_n_tokens']
        self.summary_embedding = function_info['code_embedding']
        self.function_base = function_base


    def get_local_variables(self):
        local_variables = ''
        if len(self.local_variables) == 0:
            return local_variables
        if 'module' in self.local_variables:
            module_variables = self.local_variables['module']
            for module_variable in module_variables:
                local_variables += module_variable + '\n'
        for each_class in self.local_variables:
            if each_class == 'module':
                continue

            class_block = 'class {}:\n'.format(each_class)
            each_class_variables = self.local_variables[each_class]
            for each_class_variable in each_class_variables:
                class_block += CodeUtil.add_tabs_to_string(each_class_variable, n=1) + '\n'
            local_variables += class_block

        return local_variables.strip()

    def get_local_functions(self):

        same_file_path_functions = self.function_base[self.function_base['file_path'] == self.file_path]
        function_info = same_file_path_functions[
            (same_file_path_functions['file_path'] == self.file_path) &
            (same_file_path_functions['fully_qualified_name'] == self.fully_qualified_name) &
            (same_file_path_functions['function_name'] == self.function_name) &
            (same_file_path_functions['function signature'] == self.function_signature) &
            (same_file_path_functions['raw_source_code'] == self.raw_source_code) &
            (same_file_path_functions['comment_free_source_code'] == self.comment_free_source_code)
            ]

        same_file_path_functions = same_file_path_functions.drop(function_info.index)

        function_num = 1
        local_functions_signatures = ''
        # 使用条件过滤查找 'class' 列不是 NaN 的所有行
        all_class_rows = same_file_path_functions[~same_file_path_functions['class'].isna()]
        all_classes = list(set(all_class_rows['class'].tolist()))
        for each_class in all_classes:
            # 1. class classname
            class_block_signature = 'class {}\n'.format(each_class.split('.')[-1])

            # if Config.LocalVariables == True:
            #     # 2. class variables
            #     if each_class.split('.')[-1] in self.local_variables:
            #         each_class_variables = self.local_variables[each_class.split('.')[-1]]
            #         for each_class_variable in each_class_variables:
            #             class_block_signature += CodeUtil.add_tabs_to_string(each_class_variable, n=1) + '\n'


            each_class_grouped_functions = same_file_path_functions[same_file_path_functions['class'] == each_class]

            if '__init__' in each_class_grouped_functions['function_name'].values:
                # 3. handle __init__ function
                init_function = each_class_grouped_functions[each_class_grouped_functions['function_name'] == '__init__']
                init_function_summary = init_function['summary'].tolist()[0]
                if len(init_function) > 1:
                    print('error when handling init_function. In class {}, there are {} init_functions'.format(each_class, len(init_function)))

                if Config.InitFunctionCode == True:
                    fully_qualified_name = init_function['fully_qualified_name'].tolist()[0]
                    function_signature = init_function['function signature'].tolist()[0]
                    function_signature = CodeUtil.remove_last_colon(function_signature)
                    raw_source_code = init_function['raw_source_code'].tolist()[0]
                    function_id = 'function' + str(function_num) + '{\n'
                    function_item = 'fully qualified name: ' + fully_qualified_name + '\nsummary: ' + init_function_summary + '\nsignature:' + function_signature + '\nsource_code: ' + raw_source_code
                    # function_item = 'summary: ' + init_function_summary + '\nsignature:' + function_signature + '\nsource_code: ' + raw_source_code

                    function_item = CodeUtil.add_tabs_to_string(function_item, n=1) + '\n}'
                    function_item = function_id + function_item
                    function_item_with_tabs = CodeUtil.add_tabs_to_string(function_item, n=1) + '\n'

                    class_block_signature += function_item_with_tabs
                    function_num += 1
                else:
                    fully_qualified_name = init_function['fully_qualified_name'].tolist()[0]
                    function_signature = init_function['function signature'].tolist()[0]
                    function_signature = CodeUtil.remove_last_colon(function_signature)

                    function_id = 'function' + str(function_num) + '{\n'
                    function_item = 'fully qualified name: ' + fully_qualified_name + '\nsummary: ' + init_function_summary + '\nsignature: ' + function_signature
                    # function_item = 'summary: ' + init_function_summary + '\nsignature: ' + function_signature

                    function_item = CodeUtil.add_tabs_to_string(function_item, n=1) + '\n}'
                    function_item = function_id + function_item

                    function_item_with_tabs = CodeUtil.add_tabs_to_string(function_item, n=1)
                    class_block_signature += function_item_with_tabs + '\n'
                    function_num += 1


                non_init_functions = each_class_grouped_functions[each_class_grouped_functions['function_name'] != '__init__']
            else:
                non_init_functions = each_class_grouped_functions



            # 4. all members signatures
            for _, row in non_init_functions.iterrows():
                fully_qualified_name = row['fully_qualified_name']
                function_signature = row['function signature']
                function_signature = CodeUtil.remove_last_colon(function_signature)
                function_summary = row['summary']
                function_id = 'function' + str(function_num) + '{\n'
                # add the function summary into function info
                function_item = 'fully qualified name: ' + fully_qualified_name + '\nsummary: ' + function_summary + '\nsignature: ' + function_signature
                # function_item = 'summary: ' + function_summary + '\nsignature: ' + function_signature

                function_item = CodeUtil.add_tabs_to_string(function_item, n=1) + '\n}'
                function_item = function_id + function_item
                function_item_with_tabs = CodeUtil.add_tabs_to_string(function_item, n=1)

                class_block_signature += function_item_with_tabs + '\n'
                function_num += 1

            local_functions_signatures += class_block_signature + '\n'


        all_module_functions = same_file_path_functions[same_file_path_functions['class'].isna()]
        for _, row in all_module_functions.iterrows():
            fully_qualified_name = row['fully_qualified_name']
            function_signature = row['function signature']
            function_signature = CodeUtil.remove_last_colon(function_signature)
            function_summary = row['summary']
            function_id = 'function' + str(function_num) + '{\n'

            # add the function summary into function info
            function_item = 'fully qualified name: ' + fully_qualified_name + '\nsummary: ' + function_summary + '\nsignature: ' + function_signature
            # function_item = 'summary: ' + function_summary + '\nsignature: ' + function_signature

            function_item = CodeUtil.add_tabs_to_string(function_item, n=1) + '\n}'
            function_item = function_id + function_item

            local_functions_signatures += function_item + '\n'
            function_num += 1

        return local_functions_signatures.strip()

    def get_UserInput_Format_prompt(self, UserInput_prompt_dir, InputInfoNum, Format_Type, SlotContent):
        User_Input_Format_prompt_path = UserInput_prompt_dir + '/' + Format_Type
        User_Input_Format_prompt = FileUtil.read_prompt_file(User_Input_Format_prompt_path)
        User_Input_Format_prompt = User_Input_Format_prompt.replace('#{}#', str(InputInfoNum) + ')', 1)
        User_Input_Format_prompt = User_Input_Format_prompt.replace('#{}#', SlotContent, 1)
        return User_Input_Format_prompt

    def input_prompt_construction_for_normal_gen(self):
        Config.LocalFunctions = False
        Config.InitFunctionCode = False
        Config.LocalVariables = False
        Config.FilePath = False

        prompt_dir = Config.normal_gen_prompt_dir

        # get UserDemand prompt, FileName prompt, LocalVariables prompt, CorrespondingInitFunction prompt, LocalFunctions prompt
        FunctionDescription = self.comment

        FunctionDefinition = self.function_signature
        FunctionDefinition = CodeUtil.remove_last_colon(FunctionDefinition)
        if pd.isna(self.correspongding_class):
            pass
        else:
            FunctionDefinition += '\n@Note: This function belongs to class {}'.format(self.correspongding_class.split('.')[-1])

        system_prompt_file = prompt_dir + '/System'
        system_prompt = FileUtil.read_prompt_file(system_prompt_file)
        system = [{'role': 'system', 'content': system_prompt}]

        user_input_prompt_file = prompt_dir + '/UserInput'
        user_input_prompt = FileUtil.read_prompt_file(user_input_prompt_file)

        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDescription, 1), 1)
        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDefinition, 1), 1)

        user_input = [{'role': 'user', 'content': user_input_prompt}]
        example_prompt = get_examples(prompt_dir)

        input_prompt = system + example_prompt + user_input
        return input_prompt

    def input_prompt_construction_for_LocalAware_LF(self):
        Config.LocalFunctions = True
        Config.InitFunctionCode = False
        Config.LocalVariables = False
        Config.FilePath = False

        prompt_dir = Config.local_aware_LF_prompt_dir

        # get UserDemand prompt, FileName prompt, LocalVariables prompt, CorrespondingInitFunction prompt, LocalFunctions prompt
        FunctionDescription = self.comment

        FunctionDefinition = self.function_signature
        FunctionDefinition = CodeUtil.remove_last_colon(FunctionDefinition)
        if pd.isna(self.correspongding_class):
            pass
        else:
            FunctionDefinition += '\n@Note: This function belongs to class {}'.format(
                self.correspongding_class.split('.')[-1])

        LocalFunctions = self.get_local_functions()
        system_prompt_file = prompt_dir + '/System'
        system_prompt = FileUtil.read_prompt_file(system_prompt_file)
        system = [{'role': 'system', 'content': system_prompt}]

        user_input_prompt_file = prompt_dir + '/UserInput'
        user_input_prompt = FileUtil.read_prompt_file(user_input_prompt_file)

        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDescription, n=1), 1)
        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDefinition, n=1), 1)

        if LocalFunctions == '':
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string("None", n=1), 1)
        else:
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(LocalFunctions, n=1), 1)

        user_input = [{'role': 'user', 'content': user_input_prompt}]
        example_prompt = get_examples(prompt_dir)

        input_prompt = system + example_prompt + user_input
        return input_prompt

    def input_prompt_construction_for_LocalAware_LF_InitFC(self):
        Config.LocalFunctions = True
        Config.InitFunctionCode = True
        Config.LocalVariables = False
        Config.FilePath = False

        prompt_dir = Config.local_aware_LF_InitFC_prompt_dir

        # get UserDemand prompt, FileName prompt, LocalVariables prompt, CorrespondingInitFunction prompt, LocalFunctions prompt
        FunctionDescription = self.comment

        FunctionDefinition = self.function_signature
        FunctionDefinition = CodeUtil.remove_last_colon(FunctionDefinition)
        if pd.isna(self.correspongding_class):
            pass
        else:
            FunctionDefinition += '\n@Note: This function belongs to class {}'.format(
                self.correspongding_class.split('.')[-1])

        LocalFunctions = self.get_local_functions()
        system_prompt_file = prompt_dir + '/System'
        system_prompt = FileUtil.read_prompt_file(system_prompt_file)
        system = [{'role': 'system', 'content': system_prompt}]

        user_input_prompt_file = prompt_dir + '/UserInput'
        user_input_prompt = FileUtil.read_prompt_file(user_input_prompt_file)

        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDescription, n=1), 1)
        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDefinition, n=1), 1)

        if LocalFunctions == '':
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string("None", n=1), 1)
        else:
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(LocalFunctions, n=1), 1)

        user_input = [{'role': 'user', 'content': user_input_prompt}]
        example_prompt = get_examples(prompt_dir)

        input_prompt = system + example_prompt + user_input
        return input_prompt

    def input_prompt_construction_for_LocalAware_LF_InitFC_Var(self):
        Config.LocalFunctions = True
        Config.InitFunctionCode = True
        Config.LocalVariables = True
        Config.FilePath = False

        prompt_dir = Config.local_aware_LF_InitFC_Var_prompt_dir

        # get UserDemand prompt, FileName prompt, LocalVariables prompt, CorrespondingInitFunction prompt, LocalFunctions prompt
        FunctionDescription = self.comment

        FunctionDefinition = self.function_signature
        FunctionDefinition = CodeUtil.remove_last_colon(FunctionDefinition)
        LocalVariables = self.get_local_variables()

        if pd.isna(self.correspongding_class):
            pass
        else:
            FunctionDefinition += '\n@Note: This function belongs to class {}'.format(
                self.correspongding_class.split('.')[-1])

        LocalFunctions = self.get_local_functions()
        system_prompt_file = prompt_dir + '/System'
        system_prompt = FileUtil.read_prompt_file(system_prompt_file)
        system = [{'role': 'system', 'content': system_prompt}]

        user_input_prompt_file = prompt_dir + '/UserInput'
        user_input_prompt = FileUtil.read_prompt_file(user_input_prompt_file)

        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDescription, n=1), 1)
        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDefinition, n=1), 1)

        if LocalVariables == '':
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string("None", n=1), 1)
        else:
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(LocalVariables, n=1), 1)

        if LocalFunctions == '':
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string("None", n=1), 1)
        else:
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(LocalFunctions, n=1), 1)

        user_input = [{'role': 'user', 'content': user_input_prompt}]
        example_prompt = get_examples(prompt_dir)

        input_prompt = system + example_prompt + user_input
        return input_prompt

    def input_prompt_construction_for_LocalAware_LF_InitFC_Var_FP(self):
        Config.LocalFunctions = True
        Config.InitFunctionCode = True
        Config.LocalVariables = True
        Config.FilePath = True

        prompt_dir = Config.local_aware_LF_InitFC_Var_FP_prompt_dir

        # get UserDemand prompt, FileName prompt, LocalVariables prompt, CorrespondingInitFunction prompt, LocalFunctions prompt
        FunctionDescription = self.comment
        FilePath = self.relative_file_path

        FunctionDefinition = self.function_signature
        FunctionDefinition = CodeUtil.remove_last_colon(FunctionDefinition)
        LocalVariables = self.get_local_variables()

        if pd.isna(self.correspongding_class):
            pass
        else:
            FunctionDefinition += '\n@Note: This function belongs to class {}'.format(
                self.correspongding_class.split('.')[-1])

        LocalFunctions = self.get_local_functions()
        system_prompt_file = prompt_dir + '/System'
        system_prompt = FileUtil.read_prompt_file(system_prompt_file)
        system = [{'role': 'system', 'content': system_prompt}]

        user_input_prompt_file = prompt_dir + '/UserInput'
        user_input_prompt = FileUtil.read_prompt_file(user_input_prompt_file)

        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDescription, n=1), 1)
        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDefinition, n=1), 1)
        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FilePath, n=1), 1)

        if LocalVariables == '':
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string("None", n=1), 1)
        else:
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(LocalVariables, n=1), 1)

        if LocalFunctions == '':
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string("None", n=1), 1)
        else:
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(LocalFunctions, n=1), 1)

        user_input = [{'role': 'user', 'content': user_input_prompt}]
        example_prompt = get_examples(prompt_dir)

        input_prompt = system + example_prompt + user_input
        return input_prompt

    def input_prompt_construction_for_RepoAware_LF_InitFC(self, ReusableFunctions):
        Config.LocalFunctions = True
        Config.InitFunctionCode = True
        Config.LocalVariables = False
        Config.FilePath = False

        prompt_dir = Config.repo_aware_top5_prompt_dir

        # get UserDemand prompt, FileName prompt, LocalVariables prompt, CorrespondingInitFunction prompt, LocalFunctions prompt
        FunctionDescription = self.comment

        FunctionDefinition = self.function_signature
        FunctionDefinition = CodeUtil.remove_last_colon(FunctionDefinition)
        FilePath = self.relative_file_path

        if pd.isna(self.correspongding_class):
            pass
        else:
            FunctionDefinition += '\n@Note: This function belongs to class {}'.format(
                self.correspongding_class.split('.')[-1])

        LocalFunctions = self.get_local_functions()
        system_prompt_file = prompt_dir + '/System'
        system_prompt = FileUtil.read_prompt_file(system_prompt_file)
        system = [{'role': 'system', 'content': system_prompt}]

        user_input_prompt_file = prompt_dir + '/UserInput'
        user_input_prompt = FileUtil.read_prompt_file(user_input_prompt_file)

        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDescription, n=1), 1)
        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDefinition, n=1), 1)

        if LocalFunctions == '':
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string("None", n=1), 1)
        else:
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(LocalFunctions, n=1), 1)

        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(ReusableFunctions, n=1), 1)

        user_input = [{'role': 'user', 'content': user_input_prompt}]
        example_prompt = get_examples(prompt_dir)

        input_prompt = system + example_prompt + user_input
        return input_prompt

    def get_third_party_libs(self, ThirdPartyLibs):
        third_party_libs = '['
        for ThirdPartyLib in ThirdPartyLibs:
            third_party_libs += ThirdPartyLib + ', '
        third_party_libs = third_party_libs.strip(', ')
        third_party_libs += ']'
        return third_party_libs

    def input_prompt_construction_for_Repo_Lib_Aware_LF_InitFC(self, ReusableFunctions, ThirdPartyLibs):
        Config.LocalFunctions = True
        Config.InitFunctionCode = True
        Config.LocalVariables = False
        Config.FilePath = False

        prompt_dir = Config.LF_InitFC_repo_aware_top5_library_prompt_dir

        # get UserDemand prompt, FileName prompt, LocalVariables prompt, CorrespondingInitFunction prompt, LocalFunctions prompt
        FunctionDescription = self.comment

        FunctionDefinition = self.function_signature
        FunctionDefinition = CodeUtil.remove_last_colon(FunctionDefinition)
        FilePath = self.relative_file_path

        if pd.isna(self.correspongding_class):
            pass
        else:
            FunctionDefinition += '\n@Note: This function belongs to class {}'.format(
                self.correspongding_class.split('.')[-1])

        LocalFunctions = self.get_local_functions()
        third_party_libs = self.get_third_party_libs(ThirdPartyLibs)
        system_prompt_file = prompt_dir + '/System'
        system_prompt = FileUtil.read_prompt_file(system_prompt_file)
        system = [{'role': 'system', 'content': system_prompt}]

        user_input_prompt_file = prompt_dir + '/UserInput'
        user_input_prompt = FileUtil.read_prompt_file(user_input_prompt_file)
        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(third_party_libs, n=1), 1)

        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDescription, n=1), 1)
        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(FunctionDefinition, n=1), 1)

        if LocalFunctions == '':
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string("None", n=1), 1)
        else:
            user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(LocalFunctions, n=1), 1)

        user_input_prompt = user_input_prompt.replace('#{}#', CodeUtil.add_tabs_to_string(ReusableFunctions, n=1), 1)

        user_input = [{'role': 'user', 'content': user_input_prompt}]
        example_prompt = get_examples(prompt_dir)

        input_prompt = system + example_prompt + user_input
        return input_prompt


def get_examples(prompt_dir):
    example_prompt = []
    if Config.Shot_Type == 'Zero-Shot':
        example_num = 0
    elif Config.Shot_Type == 'One-Shot':
        example_num = 1
    elif Config.Shot_Type == 'Two-Shots':
        example_num = 2
    elif Config.Shot_Type == 'Three-Shots':
        example_num = 3
    else:
        raise ValueError('Wrong Config.Shot_Type!')

    example_dirs = get_example_directories(prompt_dir, example_num)
    for example_dir in example_dirs:
        example_input_prompt_file = example_dir + '/Input'
        example_output_prompt_file = example_dir + '/Output'

        example_input_prompt = FileUtil.read_prompt_file(example_input_prompt_file)
        example_output_prompt = FileUtil.read_prompt_file(example_output_prompt_file)
        example_user = {'role': 'user', 'content': example_input_prompt}
        example_assistant = {'role': 'assistant', 'content': example_output_prompt}
        example_prompt.append(example_user)
        example_prompt.append(example_assistant)
    return example_prompt

def get_System_Input_Format_Prompt(SystemInputPromptDir, InputInfoNum, Format_Type):

    Input_Format_prompt_path = SystemInputPromptDir + '/' + Format_Type
    Input_Format_prompt = FileUtil.read_prompt_file(Input_Format_prompt_path)
    Input_Format_prompt = Input_Format_prompt.replace('#{}#', str(InputInfoNum) + ')', 1)
    return Input_Format_prompt

def get_System_Input(system_directory):

    SystemInputPromptDir = system_directory + '/Input_Format'
    SystemInputPrompt = ''
    InputDesDef_prompt_path = SystemInputPromptDir + '/Input_Des_Def'
    InputDesDef_prompt = FileUtil.read_prompt_file(InputDesDef_prompt_path)

    SystemInputPrompt += InputDesDef_prompt

    InputInfoNum = 2
    if Config.FilePath == True:
        InputInfoNum += 1
        System_Input_FilPath_prompt = get_System_Input_Format_Prompt(SystemInputPromptDir, InputInfoNum, 'FilePath')
        SystemInputPrompt += System_Input_FilPath_prompt
    if Config.LocalVariables == True:
        InputInfoNum += 1
        System_Input_LocalVariables_prompt = get_System_Input_Format_Prompt(SystemInputPromptDir, InputInfoNum, 'LocalVariables')
        SystemInputPrompt += System_Input_LocalVariables_prompt
    if (Config.LocalFunctions == True) & (Config.InitFunctionCode == True):
        InputInfoNum += 1
        System_Input_LocalFunctions_prompt = get_System_Input_Format_Prompt(SystemInputPromptDir, InputInfoNum, 'LocalFunctions_with_InitF')
        SystemInputPrompt += System_Input_LocalFunctions_prompt
    if (Config.LocalFunctions == True) & (Config.InitFunctionCode == False):
        InputInfoNum += 1
        System_Input_LocalFunctions_prompt = get_System_Input_Format_Prompt(SystemInputPromptDir, InputInfoNum, 'LocalFunctions_without_InitF')
        SystemInputPrompt += System_Input_LocalFunctions_prompt

    SystemInputPrompt = SystemInputPrompt.replace('#{}#', str(InputInfoNum), 1)

    return SystemInputPrompt


def get_example_directories(prompt_dir, example_num):
    example_dirs = []
    for i in range(1, example_num+1):
        example_dir = prompt_dir + '/Example{}'.format(i)
        example_dirs.append(example_dir)
    return example_dirs


