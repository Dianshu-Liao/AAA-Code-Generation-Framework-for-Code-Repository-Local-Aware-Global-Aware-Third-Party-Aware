import json
import pickle
import pandas as pd
import os
import ast
import numpy as np

class FileUtil:

    @staticmethod
    def load_json(filepath):
        """
        从文件中取数据
        :param filepath:
        :return:
        """
        with open(filepath, 'r') as load_f:
            data_list = json.load(load_f)
        return data_list

    @staticmethod
    def read_file(filepath):
        list_of_lines = []
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for line in lines:
                json_line = json.loads(line)
                list_of_lines.append(json_line)
        return list_of_lines

    @staticmethod
    def read_prompt_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def read_py_file(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def read_pkl(filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    @staticmethod
    def read_df(filepath):
        return pd.read_csv(filepath)

    @staticmethod
    def all_py_files(directory):
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    yield os.path.join(root, file)
    @staticmethod
    def count_python_files(directory_path):

        file_count = 0

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                if file.endswith('.py'):
                    file_count += 1

        return file_count


    @staticmethod
    def all_files_num(directory):
        num = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                num += 1
        return num

    @staticmethod
    def subdirectories(directory):
        subdirectories = [os.path.join(directory, name) for name in os.listdir(directory) if os.path.isdir(os.path.join(directory, name))]
        return subdirectories

    @staticmethod
    def read_npy_to_list(file_path):
        return list(np.load(file_path))

    @staticmethod
    def read_file_lines(file_path):
        f = open(file_path, 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()
        return lines

    @staticmethod
    def create_new_folder(folder_path):
        if not os.path.exists(folder_path):

            os.makedirs(folder_path)
            print(f"New folder '{folder_path}' has been created successfully.")
        else:
            print(f"The folder '{folder_path}' already exists. Skipping the creation.")

    @staticmethod
    def all_files_in_directory(directory):

        file_paths = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
        return file_paths


    @staticmethod
    def delete_file(file_path):

        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"file {file_path} not exists")

    @staticmethod
    def judge_directory_exist(directory):
        if os.path.exists(directory) and os.path.isdir(directory):
            return True
        else:
            return False

    @staticmethod
    def all_module_names(directory):
        all_modules = []
        for root, dirs, files in os.walk(directory):
            for dir_name in dirs:
                all_modules.append(dir_name)

        for root, _, files in os.walk(directory):
            for file_name in files:
                if file_name.endswith('.py'):
                    # 提取文件名部分并添加到列表
                    file_name_only = os.path.basename(file_name)
                    all_modules.append(file_name_only.replace('.py', ''))

        return all_modules

    @staticmethod
    def get_simple_subdirectories(folder_path):
        subdirectories = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
        if os.path.exists(folder_path+'/src'):

            subdirectories1 = [f for f in os.listdir(folder_path+'/src') if os.path.isdir(os.path.join(folder_path+'/src', f))]
        else:
            subdirectories1 = []
        return list(set(subdirectories + subdirectories1))



if __name__ == '__main__':
    directory = '../dataset/asent-0.8.0'
    subfolders = FileUtil.all_module_names(directory)


    subfolders = FileUtil.get_simple_subdirectories(directory)
    a = 1
