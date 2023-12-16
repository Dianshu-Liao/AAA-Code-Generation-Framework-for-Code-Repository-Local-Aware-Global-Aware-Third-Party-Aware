# AAA-Code-Generation-Framework-for-Code-Repository-Local-Aware-Global-Aware-Third-Party-Aware
Due to GitHub's limited capacity, we have uploaded our source code and data to Google Cloud Drive. You can access this link to our source code and data:
[https://drive.google.com/file/d/1N-qtj6rR9uYrooygMdb6d5NZJZQTlC14/view?usp=sharing](https://drive.google.com/file/d/1PQYIZuKGVPQBW0QgEDn9mmM2mRP2liFI/view?usp=sharing)

# Dataset
1. Locate the 29 function bases and third-party-library bases in the `data/function_base` folder, extracted from corresponding code repositories.
2. Explore the `data/Labeling_Results` folder to find all generated code from Language Model (LLMs) executions, along with their respective labels.
3. Navigate to the `dataset/` folder to access the code repositories obtained from the Python Package Index (PyPI).

# Evaluation 
1. Run `Evaluation/_1_workflow.py` to construction the function base and third-party-library base for each code repository
2. Run `Evaluation/_2_Evaluator.py` to generate the function code in different RQ settings.
3. Run `Evaluation/_3_Metrics_Calculation.py` to compute all experiment results.
4. Run `Evaluation/_4_statistic.py` to obtain the average retrieved global functions count and average Python file count for each code repository.

# Prompts
All prompts for AI units are available in the `prompts/` folder.
