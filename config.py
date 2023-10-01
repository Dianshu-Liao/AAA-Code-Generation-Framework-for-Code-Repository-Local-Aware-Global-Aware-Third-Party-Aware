class Config:

    OPENAI_API_KEY = "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"


    embedding_model = "text-embedding-ada-002"
    embedding_encoding = "cl100k_base"  # this the encoding for text-embedding-ada-002
    embedding_max_tokens = 8000
    PL_Type = 'Python'
    Call_LLM_Type = 'Chat'  #OneQuery
    Shot_Type = 'Three-Shots' #Zero-Shot, One-Shot, Two-Shots, Three-Shots
    prompt_type = 'Chat'

    LocalFunctions = True
    InitFunctionCode = False
    LocalVariables = False
    FilePath = False

    code_summarization_prompt_file = '../prompts/code_summarization'


    normal_gen_prompt_dir = '../prompts/NormalGen'
    local_aware_LF_prompt_dir = '../prompts/LF'
    local_aware_LF_InitFC_prompt_dir = '../prompts/LF_InitFC'
    local_aware_LF_InitFC_Var_prompt_dir = '../prompts/LF_InitFC_Var'
    local_aware_LF_InitFC_Var_FP_prompt_dir = '../prompts/LF_InitFC_Var_FP'
    local_aware_LF_InitFC_FP_prompt_dir = '../prompts/LF_InitFC_FP'
    repo_aware_top5_prompt_dir = '../prompts/RepoAware_5_Gen'
    LF_InitFC_repo_aware_top5_library_prompt_dir = '../prompts/RepoAware_5_Library_Gen_LF_InitFC'
