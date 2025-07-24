```python
"""
LogicFuzz Static Analysis

This single-file module implements:
 1. CWE-based bug clue extraction via LLM
 2. AST parsing of Structured Text (ST) code using ANSTL
 3. Semantic Dependency Graph (SDG) generation
 4. Orchestrator function to analyze a given instruction
"""
import json
import networkx as nx
from openai import OpenAI
from anstl.parser import STParser
from anstl.ast import AST

# --- Configuration / Globals ---
CWE_LIST_PATH = 'cwe_list.json'
llm = OpenAI()
st_parser = STParser()

# --- 1. CWE Bug Clue Extraction ---

def query_bug_clues(instruction_name: str, manual_text: str) -> dict:
    """
    Ask the LLM if the given instruction has known bugs and extract bug clues.
    Returns a dict of CWE identifiers and descriptions, or raw error if parsing fails.
    """
    # Load CWE list once
    try:
        with open(CWE_LIST_PATH) as f:
            cwe_list = json.load(f)
    except FileNotFoundError:
        cwe_list = {}

    prompt = (
        f"Given the following manual excerpt, identify any known bugs for instruction '{instruction_name}'. "
        "List CWE IDs and a brief description in JSON.\nManual excerpt:\n" + manual_text
    )
    resp = llm.chat.create(
        model='gpt-4o-2024-11-20',
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )
    content = resp.choices[0].message.content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": content}

# --- 2. AST Parsing via ANSTL ---

def parse_st_to_ast(st_code: str) -> AST:
    """
    Parse IEC 61131-3 Structured Text into an AST using ANSTL.
    """
    return st_parser.parse(st_code)

# --- 3. SDG Generation ---

def generate_sdg(st_code: str) -> nx.DiGraph:
    """
    Generate a semantic dependency graph (SDG) from ST code.
    Nodes represent variables/constants; edges represent data/control dependencies.
    """
    tree = parse_st_to_ast(st_code)
    sdg = nx.DiGraph()
    # Traverse AST and build dependencies
    for node in tree.walk():
        # Example: assignments
        if getattr(node, 'type', None) == 'Assignment':
            targets = [t.name for t in node.targets]
            values = [v.name for v in node.expression.variables()]
            for t in targets:
                sdg.add_node(t)
                for v in values:
                    sdg.add_node(v)
                    sdg.add_edge(v, t, type='data')
    return sdg

# --- 4. Orchestrator ---

def analyze_instruction(name: str, manual_text: str, st_code: str) -> dict:
    """
    Perform static analysis on a given logic instruction:
    1) Extract bug clues via LLM
    2) Generate the SDG from ST code
    Returns a dict with keys 'bug_clues' and 'sdg'.
    """
    bug_clues = query_bug_clues(name, manual_text)
    sdg = generate_sdg(st_code)
    return {'bug_clues': bug_clues, 'sdg': sdg}

# --- CLI Entry Point ---
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='LogicFuzz Static Analysis')
    parser.add_argument('instruction', type=str, help='Instruction name, e.g. Lx')
    parser.add_argument('manual', type=argparse.FileType('r'), help='Path to manual excerpt text')
    parser.add_argument('code', type=argparse.FileType('r'), help='Path to ST code file')
    args = parser.parse_args()

    name = args.instruction
    manual_text = args.manual.read()
    st_code = args.code.read()

    result = analyze_instruction(name, manual_text, st_code)
    print(json.dumps({
        'instruction': name,
        'bug_clues': result['bug_clues'],
        'sdg_nodes': list(result['sdg'].nodes()),
        'sdg_edges': [list(e) for e in result['sdg'].edges()]
    }, indent=2))
```
