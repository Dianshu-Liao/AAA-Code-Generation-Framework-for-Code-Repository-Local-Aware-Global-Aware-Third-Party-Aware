import re
import ast
from utils.file_util import FileUtil
import tokenize
import io
import spacy
import numpy as np
from config import Config

class CodeUtil:

    @staticmethod
    def remove_comments(code):
        """
        Remove comments from the code, both single-line comments (those beginning with #) and multi-line comments ('''' ''''' or in """" """").
        :param code: the input source code
        :return: Code after removing comments
        """
        # 删除单行注释
        code = re.sub(r'#.*', '', code)
        # 删除多行注释
        code = re.sub(r"'''[\s\S]*?'''", '', code)
        code = re.sub(r'"""[\s\S]*?"""', '', code)
        return code

    @staticmethod
    def get_function_definition(source_code):
        """
        Extracting function definition from source code
        :param source_code:
        :return: function definition
        """

        source_code = CodeUtil.remove_comments(source_code)
        function_definition = re.search(r'def.*?:', source_code).group()
        return function_definition

    @staticmethod
    def remove_and_return_imports_no_need_for_compile(source_code):
        # Matching import statements with regular expressions
        import_pattern = r'^(?:import|from\s+\S+\s+import)\s+.*$'
        import_statements = re.findall(import_pattern, source_code, re.MULTILINE)

        fqn_list = []
        for statement in import_statements:
            statement = statement.strip()
            parts = statement.split(' ')
            parts = [i for i in parts if i != '']
            if ('import' in parts) & ('from' not in parts):
                import_idx = parts.index('import')
                if 'as' in parts:
                    as_idx = parts.index('as')
                    for i in range(import_idx + 1, as_idx):
                        fqn_list.append(parts[i])
                else:
                    for i in range(import_idx + 1, len(parts)):
                        fqn_list.append(parts[i])
            elif ('import' in parts) & ('from' in parts):
                if 'as' not in parts:
                    from_index = parts.index('from')
                    import_index = parts.index('import')
                    for i in range(from_index + 1, import_index):
                        module_name = parts[i]
                    for i in range(import_index + 1, len(parts)):
                        fqn = module_name + '.' + parts[i]
                        fqn_list.append(fqn)
                else:
                    from_index = parts.index('from')
                    import_index = parts.index('import')
                    for i in range(from_index + 1, import_index):
                        module_name = parts[i]
                    as_indexs = [index for index, value in enumerate(parts) if value == 'as']
                    first_as_index = as_indexs[0]
                    if first_as_index - import_index > 1:
                        # 说明import后面至少有一个是直接import。
                        for i in range(import_index + 1, first_as_index - 1):
                            fqn = module_name + '.' + parts[i]
                            fqn_list.append(fqn)
                    for as_index in as_indexs:
                        fqn = module_name + '.' + parts[as_index - 1]
                        fqn_list.append(fqn)

        cleaned_code = re.sub(import_pattern, '', source_code, flags=re.MULTILINE).strip()
        return cleaned_code, fqn_list

    @staticmethod
    def code_and_imports_repo_aware(result_code):


        all_used_library_content = re.search(r'#all_used_library_and_function(.*?)#to_be_generated_function', result_code, re.DOTALL)
        if all_used_library_content:
            all_used_library_content = all_used_library_content.group(1).strip()
        else:
            all_used_library_content = ''

        to_be_generated_function_content = re.search(r'#to_be_generated_function(.*?)$', result_code, re.DOTALL)
        if to_be_generated_function_content:
            to_be_generated_function_content = to_be_generated_function_content.group(1).strip()
        else:
            to_be_generated_function_content = ''

        return to_be_generated_function_content, all_used_library_content

    @staticmethod
    def code_and_imports_local_aware(result_code):

        all_used_library_content = re.search(r'#all_used_library_and_local_function(.*?)#to_be_generated_function', result_code, re.DOTALL)
        if all_used_library_content:
            all_used_library_content = all_used_library_content.group(1).strip()
        else:
            all_used_library_content = ''

        to_be_generated_function_content = re.search(r'#to_be_generated_function(.*?)$', result_code, re.DOTALL)
        if to_be_generated_function_content:
            to_be_generated_function_content = to_be_generated_function_content.group(1).strip()
        else:
            to_be_generated_function_content = ''

        return to_be_generated_function_content, all_used_library_content

    @staticmethod
    def code_and_imports_normal_gen(result_code):



        all_used_library_content = re.search(r'#all_used_library(.*?)#to_be_generated_function', result_code, re.DOTALL)
        if all_used_library_content:
            all_used_library_content = all_used_library_content.group(1).strip()
        else:
            all_used_library_content = ''

        to_be_generated_function_content = re.search(r'#to_be_generated_function(.*?)$', result_code, re.DOTALL)
        if to_be_generated_function_content:
            to_be_generated_function_content = to_be_generated_function_content.group(1).strip()
        else:
            to_be_generated_function_content = ''

        return to_be_generated_function_content, all_used_library_content

    @staticmethod
    def remove_and_return_imports(source_code):

        """
        Remove import statements from the source code.
        Returns a list of deleted import statements, the code of the deleted import statements.
        """
        try:
            import_statements = []  # Store the deleted import statement
            cleaned_code_lines = []  # Store the line of code after the import statement is removed.

            # Parsing the source code
            parsed_tree = ast.parse(source_code)

            for node in parsed_tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        import_statements.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module
                    for alias in node.names:
                        full_name = alias.name if module_name is None else f"{module_name}.{alias.name}"
                        import_statements.append(full_name)
                else:
                    cleaned_code_lines.append(ast.unparse(node))

            cleaned_code = "\n".join(cleaned_code_lines)

        except:
            cleaned_code, import_statements = CodeUtil.remove_and_return_imports_no_need_for_compile(source_code)

        return cleaned_code, import_statements


    @staticmethod
    def get_purecode_and_imports(source_code):
        removed_comment_source_code = CodeUtil.remove_comments(source_code)
        return CodeUtil.remove_and_return_imports(removed_comment_source_code)

    @staticmethod
    def all_import_statements(code_repo_dir):
        import_statements = []
        all_py_files = FileUtil.all_py_files(code_repo_dir)
        for py_file_path in all_py_files:
            source_code = FileUtil.read_py_file(py_file_path).lstrip('\ufeff')


            parsed_tree = ast.parse(source_code)
            fqn_list = []


            for node in ast.walk(parsed_tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        fqn_list.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module
                    for alias in node.names:
                        fqn_list.append(f"{module_name}.{alias.name}")
            import_statements += fqn_list

        return import_statements

    @staticmethod
    def get_line_content(code_file_path, line):
        lines = FileUtil.read_file_lines(code_file_path)
        line_content = lines[line-1]
        return line_content.strip()

    @staticmethod
    def add_tabs_to_string(input_string, n):
        # Use the splitlines() method to split a string into lines.
        lines = input_string.splitlines()

        # Add n tabs at the beginning of each line using list derivation
        indented_lines = [('\t' * n) + line for line in lines]

        # Concatenate each line back to the string with a newline character
        result_string = '\n'.join(indented_lines)

        return result_string

    @staticmethod
    def remove_last_colon(input_string):
        # Checks if a string is empty
        if not input_string:
            return input_string

        # Checks if the last character of a string is a colon
        if input_string[-1] == ':':
            # If it is a colon, remove the last character using slicing
            return input_string[:-1]
        else:
            # If it is not a colon, return the original string
            return input_string

    @staticmethod
    def split_identifier(identifier):
        """
        A more detailed cut of the identifier.

        :param identifier The identifier to cut.

        :return The list of cut identifiers.
        """
        # Segmentation based on camel naming
        words = re.findall(r'[A-Z]?[a-z]+|\d+|[A-Z]+(?![a-z])', identifier)

        # If the identifier begins with a number or capital letter, add an empty string as a prefix
        if re.match(r'\d+|[A-Z]+', identifier[0]):
            words.insert(0, '')

        return words

    @staticmethod
    def tokenize_and_split_python_code(code, spacy_nlp):
        """
        Segment Python code and cut identifiers more finely.

        :param code string of Python code to process.

        :return list containing tokens, each token is a token_value with a finer cut for identifiers.
        """
        try:
            tokens = []



            tokenized_tokens = tokenize.tokenize(io.BytesIO(code.encode('utf-8')).readline)


            for token in tokenized_tokens:
                if token.type == tokenize.NAME:
                    identifier = token.string
                    words = CodeUtil.split_identifier(identifier)
                    tokens.extend(words)
                elif token.type == tokenize.STRING:
                    # Using spaCy to cut string text as a sentence
                    sentence = token.string.strip('"\'')

                    # 处理字符串文字的文本内容
                    doc = spacy_nlp(sentence)
                    for sent in doc.sents:
                        words = [token.text for token in sent]
                        tokens.extend(words)
                else:
                    tokens.append(token.string)
        except:

            pattern = r'(\b\w+\b|[^\s\w])'

            tokens = re.findall(pattern, code)

        return tokens

    @staticmethod
    def convert_imports_to_fqns(imports):

        # Use regular expressions to match what comes after the number (including what comes at the end of the line or at the end of the text)
        pattern = r'\d+\)\s*(.+?)(?:\n|$)'
        matches = re.findall(pattern, imports)
        return matches

    @staticmethod
    def convert_candidate_imports_to_fqns(imports):
        matches = re.findall(r'\S+', imports)
        return matches



    @staticmethod
    def is_body_empty_or_only_pass(code):
        try:
            parsed_code = ast.parse(code)

            # Get the body of the AST
            main_body = parsed_code.body

            # Check if the body part is empty or contains only pass statements
            if not main_body:
                return True
            elif len(main_body) == 1 and isinstance(main_body[0], ast.FunctionDef):
                # If the body contains only a function definition
                function_def = main_body[0]
                return not function_def.body or (
                            len(function_def.body) == 1 and isinstance(function_def.body[0], ast.Pass))
            else:
                return False
        except SyntaxError:
            # Code is invalid or contains syntax errors
            return True

if __name__ == '__main__':
    a = 1