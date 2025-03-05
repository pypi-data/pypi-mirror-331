# grepjson

**Interactive JSON processor with built-in debugger**

`grepjson` is a command-line tool designed to help developers interactively inspect and process JSON/JSONL data. It integrates Python's built-in `pdb` debugger, allowing you to explore JSON objects in real-time or execute custom Python snippets directly from the command line.

## Features

- **Interactive Debugging**: Drop into a `pdb` session to inspect JSON objects interactively.
- **JSONL Support**: Process JSON Lines (JSONL) format with ease.
- **Custom Execution**: Execute Python code snippets on JSON objects directly from the command line.
- **Cross-Platform**: Works on UNIX-like systems and Windows (with some limitations).
- **Pipeline Integration**: Seamlessly integrates with Unix pipelines and other CLI tools.

## Installation

Install `grepjson` via pip:

```bash
pip install grepjson
```


## Usage

### Basic Usage

Parse a JSON file and enter an interactive debug session:

```bash
cat data.json | grepjson
```

In the debug session, access the parsed JSON object as `obj`:

```plaintext
(Pdb) print(obj['key'])
```

### JSONL Support

Process a JSON Lines file and enter debug mode with all objects available as `objs`:

```bash
cat data.jsonl | grepjson --line
```

Or use a simple form:

```bash
cat data.jsonl | grepjson -l
```

### Execute Code Snippets

Extract specific fields without entering debug mode:

```bash
cat data.json | grepjson --exec "print(obj['name'])"
```

Or use a simple form:

```bash
cat data.json | grepjson -x "print(obj['name'])"
```

Process each JSON object in a JSONL file:

```bash
cat data.jsonl | grepjson -l -x "print(obj['id'])"
```



### Print Results

Automatically print the result of a code snippet:

```bash
cat data.json | grepjson -x "obj['value']" -p
```

## Examples

### Example 1: Interactive Debugging

```bash
echo '{"name": "Alice", "age": 30}' | grepjson
```

In the debug session:

```plaintext
(Pdb) print(obj['name'])
Alice
(Pdb) obj['age'] += 1
(Pdb) print(obj)
{'name': 'Alice', 'age': 31}
```

### Example 2: JSONL Processing

```bash
echo -e '{"id": 1}\n{"id": 2}\n{"id": 3}' | grepjson -l -x "print(obj['id'])"
```

Output:

```plaintext
1
2
3
```

### Example 3: Field Extraction

```bash
echo '{"name": "Bob", "details": {"age": 25}}' | grepjson -x "obj['details']['age']" -p
```

Output:

```plaintext
25
```
