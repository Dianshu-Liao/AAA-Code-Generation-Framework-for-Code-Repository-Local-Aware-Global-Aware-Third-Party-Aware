import openai

from config import Config
from utils.file_util import FileUtil
from utils.llm_util import LLMUtil
class CodeSummarization:
    openai.api_key = Config.OPENAI_API_KEY
    # openai.organization = Config.OpenAI_ORG
    @staticmethod
    def code_summarization(source_code):
        """

        :param source_code:
        :return: code summary
        """

        prompt = FileUtil.read_prompt_file(Config.code_summarization_prompt_file)
        prompt = prompt.replace('#{}#', source_code, 1)
        # print(prompt)

        token_nums = len(LLMUtil.get_tokens(prompt))

        if token_nums > 8000:
            source_code = source_code[:2000]
            prompt = FileUtil.read_prompt_file(Config.code_summarization_prompt_file)
            prompt = prompt.replace('#{}#', source_code, 1)
        code_summary = LLMUtil.ask_16k_turbo(prompt)
        return code_summary



if __name__ == '__main__':
    source_code = """
    @hk.without_apply_rng
    @hk.transform
    def token_pos_embed(tokens):
      embed_modules = assemble._make_embedding_modules(
          residual_space=residual_space,
          tokens_space=input_space,
          indices_space=indices_space,
          output_space=output_space)
      return embed_modules.pos_embed(jnp.indices(tokens.shape)[-1])
    """
    code_summary = CodeSummarization.code_summarization(source_code)
    print(code_summary)