# Import Python's AST module to read code without running app.py
import ast

# Import regular expressions for splitting text into sentences
import re

# Read the application source code
with open("app.py", "r", encoding="utf-8") as file:
    source = file.read()

# Find the chunking function in the source code
tree = ast.parse(source)
function = next(
    node for node in tree.body
    if isinstance(node, ast.FunctionDef)
    and node.name == "split_text_into_chunks"
)

# Make the regular expression module available to the extracted function
namespace = {"re": re}
exec(compile(ast.Module(body=[function], type_ignores=[]), "app.py", "exec"), namespace)

# Test the function with sample text
sample_text = (
    "Artificial intelligence is transforming business operations. "
    "Machine learning enables systems to identify patterns in data. "
    "Natural language processing helps computers understand human language. "
    "Retrieval-Augmented Generation combines information retrieval with text generation."
)

chunks = namespace["split_text_into_chunks"](
    sample_text,
    chunk_size=100,
    overlap=20
)

# Display the chunks
for index, chunk in enumerate(chunks, start=1):
    print(f"Chunk {index}: {chunk}")