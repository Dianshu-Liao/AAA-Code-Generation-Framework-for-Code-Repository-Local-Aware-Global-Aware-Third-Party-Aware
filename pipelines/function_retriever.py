import pandas as pd
from openai.embeddings_utils import get_embedding, cosine_similarity
from config import Config
import numpy as np
from ast import literal_eval
from utils.code_util import CodeUtil
import openai
pd.options.mode.chained_assignment = None  # 禁用SettingWithCopyWarning
openai.api_key = Config.OPENAI_API_KEY


class FunctionRetriever:
    def __init__(self, function_base_path):
        # embedding model parameters
        self.embedding_model = Config.embedding_model
        self.function_base = pd.read_csv(function_base_path)
        self.function_base['embedding'] = self.function_base['embedding'].apply(literal_eval).apply(np.array)

    # def retrieve_functions(self, query_function_code, top_k=10):
    #     '''
    #     :param query_function_code: query function code
    #     :param n: number of functions to retrieve
    #     '''
    #     query_function_code_embedding = get_embedding(query_function_code, engine=self.embedding_model)
    #     # code_repo = FileUtil.read_df(code_repo_embedding_path)
    #     # code_repo["embedding"] = code_repo['embedding'].apply(literal_eval).apply(np.array)
    #     self.function_base['similarity'] = self.function_base['embedding'].apply(lambda x: cosine_similarity(x, query_function_code_embedding))
    #     retrieved_functions = self.function_base.sort_values(by='similarity', ascending=False).head(top_k)
    #     return retrieved_functions

    def retrieve_functions(self, query_function_code, query_nl, top_k=10):
        '''
        :param query_function_code: query function code
        :param n: number of functions to retrieve
        '''
        query_function_code_embedding = get_embedding(query_function_code, engine=self.embedding_model)
        query_nl_embedding = get_embedding(query_nl, engine=self.embedding_model)

        self.function_base['similarity'] = self.function_base['embedding'].apply(lambda x: cosine_similarity(x, query_function_code_embedding))
        code_retrieved_functions = self.function_base.sort_values(by='similarity', ascending=False).head(top_k)
        code_retrieved_functions = code_retrieved_functions.drop('similarity', axis=1)
        code_retrieved_functions = code_retrieved_functions.drop('embedding', axis=1)

        self.function_base['similarity'] = self.function_base['embedding'].apply(lambda x: cosine_similarity(x, query_nl_embedding))
        nl_retrieved_functions = self.function_base.sort_values(by='similarity', ascending=False).head(top_k)
        nl_retrieved_functions = nl_retrieved_functions.drop('similarity', axis=1)
        nl_retrieved_functions = nl_retrieved_functions.drop('embedding', axis=1)

        # 合并两个 DataFrame
        merged = pd.concat([code_retrieved_functions, nl_retrieved_functions])

        # 去除重复行
        retrieved_functions = merged.drop_duplicates()

        return retrieved_functions

    # @staticmethod
    # def retrieve_functions_for_Evaluation(query_function_code, function_base, top_k=10):
    #     '''
    #     :param query_function_code: query function code
    #     :param n: number of functions to retrieve
    #     '''
    #     embedding_model = Config.embedding_model
    #     query_function_code_embedding = get_embedding(query_function_code, engine=embedding_model)
    #     # code_repo = FileUtil.read_df(code_repo_embedding_path)
    #     # code_repo["embedding"] = code_repo['embedding'].apply(literal_eval).apply(np.array)
    #     function_base['similarity'] = function_base['embedding'].apply(lambda x: cosine_similarity(x, query_function_code_embedding))
    #     retrieved_functions = function_base.sort_values(by='similarity', ascending=False).head(top_k)
    #     return retrieved_functions


    @staticmethod
    def retrieve_functions_for_Evaluation(query_function_code, query_nl, function_base, top_k=10):
        '''
        :param query_function_code: query function code
        :param n: number of functions to retrieve
        '''
        embedding_model = Config.embedding_model
        query_nl_embedding = get_embedding(query_nl, engine=embedding_model)
        function_base['similarity'] = function_base['summary_embedding'].apply(lambda x: cosine_similarity(x, query_nl_embedding))
        nl_retrieved_functions = function_base.sort_values(by='similarity', ascending=False).head(top_k)
        nl_retrieved_functions = nl_retrieved_functions.drop('similarity', axis=1)
        nl_retrieved_functions = nl_retrieved_functions.drop('code_embedding', axis=1)
        nl_retrieved_functions = nl_retrieved_functions.drop('summary_embedding', axis=1)
        if query_function_code == '':
            return nl_retrieved_functions

        query_function_code_embedding = get_embedding(query_function_code, engine=embedding_model)
        function_base['similarity'] = function_base['code_embedding'].apply(lambda x: cosine_similarity(x, query_function_code_embedding))
        code_retrieved_functions = function_base.sort_values(by='similarity', ascending=False).head(top_k)
        code_retrieved_functions = code_retrieved_functions.drop('similarity', axis=1)
        code_retrieved_functions = code_retrieved_functions.drop('code_embedding', axis=1)
        code_retrieved_functions = code_retrieved_functions.drop('summary_embedding', axis=1)



        # 合并两个 DataFrame
        merged = pd.concat([code_retrieved_functions, nl_retrieved_functions])

        # 去除重复行
        retrieved_functions = merged.drop_duplicates()


        return retrieved_functions

    @staticmethod
    def get_reusable_functions_for_Evaluation(retrieved_functions):
        '''
        :param retrieved_functions: retrieved functions
        '''
        reusable_functions_prompt = ''
        i = 1
        for _, row in retrieved_functions.iterrows():
            summary = row['summary']
            signature = row['function signature']
            signature = CodeUtil.remove_last_colon(signature)
            FQN = row['fully_qualified_name']
            # function_prompt = 'function {}:\nsummary: {}\nsignature: {}\nfully qualified name: {}\n\n'.\
            #     format(i, summary, signature, FQN)

            # function_prompt = '{\nsummary:' + summary + '\nsignature: ' + signature + '\n}\n'
            function_id = 'function' + str(i) + '{\n'
            function_item = 'fully qualified name: ' + FQN + '\nsummary:' + summary + '\nsignature: ' + signature
            function_item = CodeUtil.add_tabs_to_string(function_item, 1) + '\n'
            function_prompt = function_id + function_item + '}\n'


            # function_prompt = signature + '\n'
            reusable_functions_prompt += function_prompt
            i += 1
        reusable_functions_prompt = reusable_functions_prompt.strip()
        return reusable_functions_prompt

    def get_reusable_functions(self, retrieved_functions):
        '''
        :param retrieved_functions: retrieved functions
        '''
        reusable_functions_prompt = ''
        i = 1
        for _, row in retrieved_functions.iterrows():
            summary = row['summary']
            signature = row['function signature']
            signature = CodeUtil.remove_last_colon(signature)
            FQN = row['fully_qualified_name']
            # function_prompt = 'function {}:\nsummary: {}\nsignature: {}\nfully qualified name: {}\n\n'.\
            #     format(i, summary, signature, FQN)
            function_prompt = 'reusable function {}:\nsummary: {}\nsignature: {}\n\n'.\
                format(i, summary, signature)
            reusable_functions_prompt += function_prompt
            i += 1
        return reusable_functions_prompt

    def get_reusable_functions_from_code(self, query_function_code, query_nl, top_k=10):
        retrieved_functions = self.retrieve_functions(query_function_code, query_nl, top_k)
        reusable_functions_prompt = self.get_reusable_functions(retrieved_functions)
        return reusable_functions_prompt

if __name__ == '__main__':


    query_function_code = '''
def _construct_text(tag_elem, include_tail_text):
    def replace_unicode_quotes(text) -> str:
        text = text.replace("\x91", "‘")
        text = text.replace("\x92", "’")
        text = text.replace("\x93", "“")
        text = text.replace("\x94", "”")
        text = text.replace("&apos;", "'")
        text = text.replace("â\x80\x99", "'")
        text = text.replace("â\x80“", "—")
        text = text.replace("â\x80”", "–")
        text = text.replace("â\x80˜", "‘")
        text = text.replace("â\x80¦", "…")
        text = text.replace("â\x80™", "’")
        text = text.replace("â\x80œ", "“")
        text = text.replace("â\x80?", "”")
        text = text.replace("â\x80ť", "”")
        text = text.replace("â\x80ś", "“")
        text = text.replace("â\x80¨", "—")
        text = text.replace("â\x80ł", "″")
        text = text.replace("â\x80Ž", "")
        text = text.replace("â\x80‚", "")
        text = text.replace("â\x80‰", "")
        text = text.replace("â\x80‹", "")
        text = text.replace("â\x80", "")
        text = text.replace("â\x80s'", "")
        return text
    text = ''
    for item in tag_elem.itertext():
        if item:
            text += item
    if include_tail_text and tag_elem.tail:
        text = text + tag_elem.tail
    text = replace_unicode_quotes(text)
    return text.strip()
    '''

    query_nl = 'Extracts text from a text tag element.'

    function_base_path = '../data/function_base/unstructured-0.10.12/function_base.csv'
    function_retriever = FunctionRetriever(function_base_path)
    reusable_functions_prompt = function_retriever.get_reusable_functions_from_code(query_function_code, query_nl, top_k=6)
    print(reusable_functions_prompt)