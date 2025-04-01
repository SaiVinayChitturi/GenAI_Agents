import ast

def extract_code_structure(file_path):
    """Parses a Python file and extracts imports, class definitions, and methods."""
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)

    imports = []
    class_defs = {}
    print(tree)
    for node in tree.body:
        print(node)
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            imports.append(node)
        elif isinstance(node, ast.ClassDef):
            methods = {m.name: m for m in node.body if isinstance(m, ast.FunctionDef)}
            class_defs[node.name] = {"methods": methods, "node": node}

    return imports, class_defs

def update_template(template_path, new_code_path, output_path):
    # Extract imports & class structure from both files
    template_imports, template_classes = extract_code_structure(template_path)
    new_imports, new_classes = extract_code_structure(new_code_path)

    with open(template_path, "r") as template_file:
        template_lines = template_file.readlines()

    with open(new_code_path, "r") as new_code_file:
        new_code_lines = new_code_file.readlines()

    new_content = []
    added_imports = set()

    # Process imports
    for imp in new_imports:
        imp_str = ast.unparse(imp)  # Convert AST node back to code
        if imp_str not in [ast.unparse(i) for i in template_imports]:
            new_content.append(imp_str + "\n")
            added_imports.add(imp_str)

    # Add the original template content
    new_content.extend(template_lines)

    # Process class methods
    for class_name, new_class in new_classes.items():
        if class_name in template_classes:
            template_methods = template_classes[class_name]["methods"]
            new_methods = new_class["methods"]

            for method_name, new_method in new_methods.items():
                if method_name not in template_methods:
                    # Find marker for method insertion
                    method_marker = f"# INSERT_METHOD_{class_name}"
                    for i, line in enumerate(new_content):
                        if method_marker in line:
                            new_content.insert(i + 1, ast.unparse(new_method) + "\n\n")
                            break

    # Write to output file
    with open(output_path, "w") as output_file:
        output_file.writelines(new_content)

    print(f"Updated template saved to {output_path}")

# Example usage
update_template("template.py", "generated.py", "output.py")
