from datetime import datetime
import pandas as pd
from utils.file_util import FileUtil
import requests
import numpy as np
import tqdm
import tarfile
import matplotlib.pyplot as plt
import re
import os

class DatasetProcessor:

    def __init__(self, raw_data_path, compare_date, dataset_path):
        self.raw_data = pd.read_csv(raw_data_path)
        self.compare_date = datetime.strptime(compare_date, '%Y-%m-%d')
        self.dataset_path = dataset_path

    def get_the_first_release_data(self, release_info):
        first_release = release_info[-1]
        first_release_date = first_release[-1]
        first_release_date = datetime.strptime(first_release_date, '%Y-%m-%d')

        return first_release_date


    def download_all_repos_from_urls(self, data_filter_by_first_release_date_path, failed_to_downloaded_urls_path):
        new_filtered_data = pd.DataFrame()
        filtered_data = pd.read_csv(data_filter_by_first_release_date_path)
        filtered_data['py_file_nums'] = ''
        failed_downloaded_urls = []
        for _, row in tqdm.tqdm(filtered_data.iterrows(), total=filtered_data.shape[0]):
            url = row['file_href']
            # print('Now handling url : {}'.format(url))
            repo_name = url.split('/')[-1]
            dataset_repo_path = self.dataset_path + '/' + repo_name
            unziped_directory = dataset_repo_path.replace('.tar.gz', '')
            if FileUtil.judge_directory_exist(unziped_directory):
                continue

            try:
                # Set the maximum wait time for requests to 10 seconds
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    with open(dataset_repo_path, 'wb') as f:
                        f.write(response.content)
                    print(f"The file has successfully been downloaded to {dataset_repo_path}")

                    self.unzip_tar_gz_file(dataset_repo_path)

                    py_file_nums = FileUtil.count_python_files(unziped_directory)
                    if py_file_nums < 5:
                        os.rmdir(unziped_directory)
                        print('{} is removed since it contains less than 5 py files'.format(unziped_directory))

                    # filtered_data.loc[filtered_data['file_href'] == url, 'py_file_nums'] = py_file_nums
                    # new_filtered_data = new_filtered_data._append(filtered_data[filtered_data['file_href'] == url])
                    a = 1
                else:
                    print(f"Failed to download the file {url}")
                    failed_downloaded_urls.append(url)
            except :
                print(f"Failed to download the file {url}")
                failed_downloaded_urls.append(url)


        failed_downloaded_urls_array = np.array(failed_downloaded_urls)
        np.save(failed_to_downloaded_urls_path, failed_downloaded_urls_array)


    def filter_by_first_release_date(self):

        filtered_data = pd.DataFrame()

        for _, row in tqdm.tqdm(self.raw_data.iterrows(), total=self.raw_data.shape[0]):
            package_name = row['package_name']
            package_des = row['package_des']
            package_href = row['package_href']
            stars = row['stars']
            forks = row['forks']
            issues = row['issues']
            release_info = eval(row['release_info'])
            file_href = row['file_href']

            first_release_data = self.get_the_first_release_data(release_info)
            if first_release_data >= self.compare_date:
                filtered_data = filtered_data._append(row)
        return filtered_data

    # 定义一个函数来处理 'stars' 列中的值
    def process_stars_forks(self, stars):
        if pd.notna(stars):
            if 'k' in stars:
                # 如果包含 'k'，将 'k' 替换为空字符串，并乘以1000
                stars = stars.replace('k', '').strip()
                stars = int(float(stars) * 1000)
            elif stars == 'repo not found':
                stars = 0
            else:
                # 否则，将其转换为浮点数
                stars = int(stars)
        else:
            # 如果是 NaN，将其转换为0
            stars = 0
        return stars


    def filter_by_stars(self, dataset):
        dataset['stars'] = dataset['stars'].apply(self.process_stars_forks)
        dataset['forks'] = dataset['forks'].apply(self.process_stars_forks)
        stars_gt_100 = dataset[dataset['stars'] > 100]

        return stars_gt_100

    def filter_by_latest_version(self, dataset):
        filtered_data = pd.DataFrame()
        package_name_list = dataset['package_name'].tolist()
        pattern = r'[a-zA-Z-]+'
        package_names = list(set([re.search(pattern, package).group() for package in package_name_list]))


        for package_name in package_names:
            matching_rows = dataset[dataset['package_name'].str.contains(package_name, case=False, na=False)]
            matched_package_names = matching_rows['package_name']
            max_package_name = max(matched_package_names)
            row = dataset[dataset['package_name'] == max_package_name]
            filtered_data = filtered_data._append(row)

        return filtered_data

    def get_filtered_data(self, filter_data_path):
        data_filtered_by_release_date = self.filter_by_first_release_date()
        stars_gt_100 = self.filter_by_stars(data_filtered_by_release_date)
        filtered_data = self.filter_by_latest_version(stars_gt_100)
        filtered_data = filtered_data.drop_duplicates()

        filtered_data.to_csv(filter_data_path, index=False)

    def unzip_tar_gz_file(self, tar_gz_file_path):
        # unzip the file
        with tarfile.open(tar_gz_file_path, 'r:gz') as tar:
            tar.extractall(self.dataset_path)

        # delete the unzip file
        FileUtil.delete_file(tar_gz_file_path)




if __name__ == '__main__':
    raw_data_path = 'code_repos.csv'

    filtered_data_path = 'filtered_code_repos.csv'
    failed_to_downloaded_urls_path = 'failed_to_downloaded_urls.npy'
    compare_date = '2021-10-01'
    dataset_path = '../dataset'


    dataprocessor = DatasetProcessor(raw_data_path, compare_date, dataset_path)
    dataprocessor.get_filtered_data(filtered_data_path)
    dataprocessor.download_all_repos_from_urls(filtered_data_path, failed_to_downloaded_urls_path)
