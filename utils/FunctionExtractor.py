import ast
from utils.file_util import FileUtil

class FunctionInfoVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.scope_level = 0

    def get_function_signature(self, node):
        if isinstance(node, ast.FunctionDef):
            parameters = []
            for arg in node.args.args:
                param_name = arg.arg
                param_annotation = ast.get_source_segment(self.source_code, arg.annotation)
                if param_annotation:
                    parameters.append(f"{param_name}: {param_annotation}")
                else:
                    parameters.append(param_name)

            return_annotation = ast.get_source_segment(self.source_code, node.returns)
            if return_annotation:
                signature = f"def {node.name}({', '.join(parameters)}) -> {return_annotation}:"
            else:
                signature = f"def {node.name}({', '.join(parameters)}):"
            return signature

        return None

    def visit_FunctionDef(self, node):
        if self.scope_level == 0:
            signature = self.get_function_signature(node)
            docstring = ast.get_docstring(node)
            self.functions.append({
                'name': node.name,
                'source': ast.unparse(node),
                'signature': signature,
                'docstring': docstring,
                'start_lineno': node.lineno,
                'end_lineno': node.end_lineno,
                'class': None
            })
        self.scope_level += 1
        self.generic_visit(node)
        self.scope_level -= 1

    def visit_ClassDef(self, node):
        self.scope_level += 1
        for sub_node in node.body:
            if isinstance(sub_node, ast.FunctionDef):
                signature = self.get_function_signature(sub_node)
                docstring = ast.get_docstring(sub_node)
                self.functions.append({
                    'name': sub_node.name,
                    'source': ast.unparse(sub_node),
                    'signature': signature,
                    'docstring': docstring,
                    'start_lineno': sub_node.lineno,
                    'end_lineno': sub_node.end_lineno,
                    'class': node.name
                })
        self.generic_visit(node)
        self.scope_level -= 1

def extract_function_info(file_path):
    source_code = FileUtil.read_py_file(file_path)
    tree = ast.parse(source_code)

    function_info_visitor = FunctionInfoVisitor()
    function_info_visitor.source_code = source_code  # 将源代码传递给访问者对象
    function_info_visitor.visit(tree)

    return function_info_visitor.functions

if __name__ == '__main__':
    file_path = '../code_repo/unstructured-0.10.12/unstructured/documents/html.py'
    # file_path = '../code_repo/unstructured-0.10.12/unstructured/cleaners/core.py'
    # file_path = '../data/deepmind_tracr/tracr/compiler/assemble_test.py'  # 替换为实际文件路径
    function_info = extract_function_info(file_path)
    for info in function_info:
        print(f"Function Name: {info['name']}")
        print(f"Source Code:\n{info['source']}")
        print(f"Signature: {info['signature']}")
        print(f"Docstring: {info['docstring']}")
        print(f"Class: {info['class']}")
        print(f"Start Line Number: {info['start_lineno']}")
        print(f"End Line Number: {info['end_lineno']}")
        print("=" * 30)
