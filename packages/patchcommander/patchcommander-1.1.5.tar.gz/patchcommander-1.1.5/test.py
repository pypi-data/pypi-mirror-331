"""
Test script for parser functionality.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from parsers.python_parser import PythonParser
from parsers.javascript_parser import JavaScriptParser
from core.languages import get_language_for_file

def test_python_parser():
    """Test basic functionality of the Python parser."""
    print("\n=== Python parser test ===")

    code = """
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def say_hello(self):
        print(f"Hello, my name is {self.name}")

def calculate_bmi(weight, height):
    return weight / (height * height)

greeting = lambda name: f"Hello, {name}!"
"""
    parser = PythonParser()
    tree = parser.parse(code)

    print("Classes found:")
    classes = tree.find_classes()
    for cls in classes:
        print(f"- {cls.get_type()}: {cls.get_text()[:40]}...")

    print("\nFunctions found:")
    functions = tree.find_functions()
    for func in functions:
        print(f"- {func.get_type()}: {func.get_text()[:40]}...")

    if classes:
        print("\nMethods in first class:")
        methods = tree.find_methods(classes[0])
        for method in methods:
            print(f"- {method.get_type()}: {method.get_text()[:40]}...")

    if classes:
        new_method = "def get_details(self):\n    return f\"{self.name} is {self.age} years old\"\n"
        print("\nAdding new method to Person class...")
        new_tree = tree.add_method_to_class(classes[0], new_method)
        print(new_tree.original_code)


def test_javascript_parser():
    """Test basic functionality of the JavaScript parser."""
    print("\n=== JavaScript parser test ===")

    code = """
class Person {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }

    sayHello() {
        console.log(`Hello, my name is ${this.name}`);
    }
}

function calculateBMI(weight, height) {
    return weight / (height * height);
}

const greet = (name) => {
    console.log(`Hello, ${name}!`);
};
"""
    parser = JavaScriptParser()
    tree = parser.parse(code)

    print("Classes found:")
    classes = tree.find_classes()
    for cls in classes:
        print(f"- {cls.get_type()}: {cls.get_text()[:40]}...")

    print("\nFunctions found:")
    functions = tree.find_functions()
    for func in functions:
        print(f"- {func.get_type()}: {func.get_text()[:40]}...")

    if classes:
        print("\nMethods in first class:")
        methods = tree.find_methods(classes[0])
        for method in methods:
            print(f"- {method.get_type()}: {method.get_text()[:40]}...")

    if classes:
        new_method = "getDetails() {\n    return `${this.name} is ${this.age} years old`;\n}"
        print("\nAdding new method to Person class...")
        new_tree = tree.add_method_to_class(classes[0], new_method)
        print(new_tree.original_code)


def test_language_detection():
    """Test language detection based on file extension."""
    print("\n=== Language detection test ===")

    test_files = ["example.py", "script.js", "component.jsx", "module.ts", "app.tsx"]

    for file in test_files:
        try:
            language = get_language_for_file(file)
            print(f"{file} -> {language}")
        except ValueError as e:
            print(f"{file} -> Error: {e}")


def main():
    """Main function running the tests."""
    print("=== Parser and code operation tests ===")

    test_python_parser()
    test_javascript_parser()
    test_language_detection()

    print("\nAll tests completed.")


if __name__ == "__main__":
    main()