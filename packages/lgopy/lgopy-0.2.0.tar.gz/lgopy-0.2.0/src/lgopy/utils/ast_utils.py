import ast


class ClassesCodeExtractor(ast.NodeVisitor):
    """
    Extracts the code for each class defined in a Python file
    """
    def __init__(self):
        self.class_nodes = []

    def visit_ClassDef(self, node):
        """
        Extracts the code for each class defined in a Python file
        :param node:
        :return:
        """
        # Collect class definition nodes
        self.class_nodes.append(node)
        # Continue visiting other nodes in the class body
        self.generic_visit(node)

import ast

class ImportExtractor(ast.NodeVisitor):
    """
    Extracts the imports used within a specific class.
    """
    def __init__(self, class_name):
        self.class_name = class_name
        self.inside_class = False
        self.class_node = None
        self.imports = []  # List to store formatted imports
        self.used_imports = set()  # Set to store used import names

    def visit_Import(self, node):
        """
        Visit and extract all 'import ...' statements.
        :param node: The AST node representing the import.
        """
        for alias in node.names:
            # Store the import as it appears in the code
            if alias.asname:
                formatted_import = f"import {alias.name} as {alias.asname}"
            else:
                formatted_import = f"import {alias.name}"
            self.imports.append((alias.asname or alias.name, formatted_import))

    def visit_ImportFrom(self, node):
        """
        Visit and extract all 'from ... import ...' statements.
        :param node: The AST node representing the from import.
        """
        module_name = node.module if node.module else ''
        for alias in node.names:
            # Store the import as it appears in the code
            if alias.asname:
                formatted_import = f"from {module_name} import {alias.name} as {alias.asname}"
            else:
                formatted_import = f"from {module_name} import {alias.name}"
            self.imports.append((alias.asname or alias.name, formatted_import))

    def visit_ClassDef(self, node):
        """
        Visit a class definition and extract imports if the class name matches.
        :param node: The AST node representing the class.
        """
        if node.name == self.class_name:
            self.class_node = node
            self.inside_class = True
            self.generic_visit(node)  # Visit the class body
            self.inside_class = False

    def visit_Name(self, node):
        """
        Track usage of imported names within the target class.
        :param node: The AST node representing a name.
        """
        if self.inside_class and node.id in [imp[0] for imp in self.imports]:
            self.used_imports.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """
        Track usage of attributes that might belong to imported modules.
        :param node: The AST node representing an attribute.
        """
        if self.inside_class and isinstance(node.value, ast.Name) and node.value.id in [imp[0] for imp in self.imports]:
            self.used_imports.add(node.value.id)
        self.generic_visit(node)

    def get_used_imports(self):
        """
        Get the imports that are actually used in the class.
        :return: List of formatted import statements.
        """
        # Filter the formatted imports based on usage
        return [imp[1] for imp in self.imports if imp[0] in self.used_imports]



def extract_classes_code(source_code: str) -> dict:
    """
    Extracts the code for each class defined in a Python file
    :param source_code: str - The source code of the Python file
    :return:
    """
    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Initialize the visitor to find class nodes
    extractor = ClassesCodeExtractor()
    extractor.visit(tree)

    class_code_dict = {}
    for class_node in extractor.class_nodes:
        # Calculate start and end lines for each class definition
        start_lineno = class_node.lineno - 1
        end_lineno = class_node.end_lineno if hasattr(class_node, 'end_lineno') else None

        # Extract class code based on line numbers
        class_code_lines = source_code.splitlines()[start_lineno:end_lineno]
        class_code = "\n".join(class_code_lines)

        # Store the class code with the class name
        class_code_dict[class_node.name] = class_code

    return class_code_dict


def extract_imports_for_class(source_code: str, class_name: str) -> list:
    """
    Extracts the imports used within a specific class
    :param source_code: str - The source code of the Python file
    :param class_name: str - The name of the target class
    :return:
    """
    # Parse the file into an AST
    tree = ast.parse(source_code)
    extractor = ImportExtractor(class_name)
    extractor.visit(tree)

    return extractor.get_used_imports()
