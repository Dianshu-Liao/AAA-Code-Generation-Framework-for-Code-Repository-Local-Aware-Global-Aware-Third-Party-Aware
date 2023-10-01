# AAA-Code-Generation-Framework-for-Code-Repository-Local-Aware-Global-Aware-Third-Party-Aware
Due to GitHub's limited capacity, we have uploaded our source code and data to Google Cloud Drive. You can access this link to our source code and data:
https://drive.google.com/file/d/1N-qtj6rR9uYrooygMdb6d5NZJZQTlC14/view?usp=sharing

# Data Crawling (Process to prepare for the benchmark)
1. Run dataset_collection/_1_PyPI_data_crrawler.py to obtain the code repositories information.
2. Run dataset_collection/_2_dataset_processor.py to download and filter the code repositories.
3. Run dataect_collection/_3_test_case_construction.py to get the test cases.
4. Run dataset_collection/_4_calculate_all_function.py to statistic the datas

# Evaluation 
1. Run Evaluation/_1_workflow.py to construction the function base and third-party-library base for each code repository
2. Run Evaluation/_2_Evaluator.py to generate the function code in different RQ settings.
