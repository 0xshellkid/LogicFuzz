
import argparse
import importlib.util
import json
import logging
import random
import sys
from pathlib import Path

import networkx as nx
from openai import OpenAI

# --- Configuration & Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)
llm = OpenAI()

# Load prompt template from external file or raise error
PROMPT_TEMPLATE_PATH = Path('seed_prompt.txt')
if not PROMPT_TEMPLATE_PATH.is_file():
    logger.error(f"Prompt template not found: {PROMPT_TEMPLATE_PATH}")
    sys.exit(1)
PROMPT_TEMPLATE = PROMPT_TEMPLATE_PATH.read_text()

# Mutation targets: both call and param edges, or individually
MUTATION_TARGETS = ['both', 'call', 'param']

# --- 1. Subgraph Selection ---
def select_random_subgraph(sdg: nx.DiGraph, root: str, size: int = 5) -> nx.DiGraph:
    """
    Given an SDG and a root instruction name, randomly grow a connected
    subgraph of up to `size` nodes including the root.
    """
    if root not in sdg:
        raise KeyError(f"Root instruction '{root}' not found in SDG.")

    nodes = {root}
    frontier = set(sdg.predecessors(root)) | set(sdg.successors(root))
    while frontier and len(nodes) < size:
        next_node = random.choice(tuple(frontier))
        nodes.add(next_node)
        frontier |= set(sdg.predecessors(next_node)) | set(sdg.successors(next_node))
        frontier -= nodes
    subg = sdg.subgraph(nodes).copy()
    subg.graph['root'] = root
    logger.debug(f"Selected subgraph nodes={subg.nodes()} edges={subg.edges()}")
    return subg

# --- 2. Structural Mutation ---
def order_mutation(subg: nx.DiGraph, edge_type: str) -> None:
    """
    In-place shuffle of either call-edge order or param-edge lists.
    """
    if edge_type == 'call':
        call_order = subg.graph.get('call_order', list(subg.nodes()))
        random.shuffle(call_order)
        subg.graph['call_order'] = call_order
        logger.debug(f"Shuffled call order: {call_order}")
    elif edge_type == 'param':
        for u, v, data in subg.edges(data=True):
            if data.get('type') == 'param':
                params = data.get('params', [])
                random.shuffle(params)
                data['params'] = params
                logger.debug(f"Shuffled params on edge {u}->{v}: {params}")


def quantitative_mutation(subg: nx.DiGraph, edge_type: str, pool: list) -> None:
    """
    Add or remove a node (call) or an edge (param) based on pool.
    """
    if edge_type == 'call':
        call_edges = [(u, v) for u, v, d in subg.edges(data=True) if d.get('type') == 'call']
        if pool and random.random() < 0.5:
            # Add a new instruction before root
            new_ins = random.choice(pool)
            subg.add_node(new_ins)
            subg.add_edge(new_ins, subg.graph['root'], type='call')
            logger.debug(f"Added call edge: {new_ins} -> {subg.graph['root']}")
        elif call_edges:
            # Remove an existing call edge
            e = random.choice(call_edges)
            subg.remove_edge(*e)
            logger.debug(f"Removed call edge: {e}")
    elif edge_type == 'param':
        param_edges = [(u, v) for u, v, d in subg.edges(data=True) if d.get('type') == 'param']
        if pool and random.random() < 0.5:
            # Add a new param edge from random pool instruction
            src = random.choice(pool)
            tgt = subg.graph['root']
            subg.add_edge(src, tgt, type='param', params=[random.choice(list(subg.nodes()))])
            logger.debug(f"Added param edge: {src} -> {tgt}")
        elif param_edges:
            e = random.choice(param_edges)
            subg.remove_edge(*e)
            logger.debug(f"Removed param edge: {e}")


def mutate_subgraph_structure(subg: nx.DiGraph, instruction_pool: list) -> nx.DiGraph:
    """
    Apply one structural mutation (order or quantitative) to call and/or param edges.
    """
    target = random.choice(MUTATION_TARGETS)
    logger.info(f"Mutation target selected: {target}")
    if target in ('both', 'call'):
        if random.random() < 0.5:
            order_mutation(subg, 'call')
        else:
            quantitative_mutation(subg, 'call', instruction_pool)
    if target in ('both', 'param'):
        if random.random() < 0.5:
            order_mutation(subg, 'param')
        else:
            quantitative_mutation(subg, 'param', instruction_pool)
    return subg

# --- 3. LLM-Based Seed Generation ---
def generate_seed_program(subg: nx.DiGraph, instruction: str) -> str:
    """
    Use LLM to synthesize a seed ST program based on mutated subgraph.
    """
    prompt = PROMPT_TEMPLATE.format(
        instruction=instruction,
        nodes=subg.nodes(),
        edges=subg.edges(data=True)
    )
    logger.debug(f"Prompt to LLM: {prompt}")
    response = llm.chat.create(
        model='gpt-4o-2024-11-20',
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a PLC program generator."},
            {"role": "user", "content": prompt}
        ]
    )
    program = response.choices[0].message.content.strip()
    logger.info(f"Generated seed program of length {len(program)} characters")
    return program

# --- 4. Python Script Validation ---
def validate_with_python_script(program: str, script_path: str = 'validate.py') -> bool:
    """
    Write the program to a file and call external Python validator script.
    The script must define validate(path: str) -> bool.
    """
    seed_path = Path('seed_program.st')
    seed_path.write_text(program)
    spec = importlib.util.spec_from_file_location('validator', script_path)
    validator = importlib.util.module_from_spec(spec)
    sys.modules['validator'] = validator
    spec.loader.exec_module(validator)
    try:
        valid = validator.validate(str(seed_path))
        logger.info(f"Validation result: {valid}")
        return valid
    except Exception as e:
        logger.error(f"Validation script error: {e}")
        return False

# --- 5. Orchestrator & CLI ---
def generate_and_validate(instruction: str,
                          sdg: nx.DiGraph,
                          instruction_pool: list) -> dict:
    subg = select_random_subgraph(sdg, instruction)
    mutated = mutate_subgraph_structure(subg, instruction_pool)
    seed_program = generate_seed_program(mutated, instruction)
    validated = validate_with_python_script(seed_program)
    return {'seed_program': seed_program, 'validated': validated}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='LogicFuzz Seed Generator')
    parser.add_argument('instruction', help='Target logic instruction name')
    parser.add_argument('sdg_file', help='Path to pickled SDG file')
    parser.add_argument('pool_file', help='Path to JSON file listing all logic instructions')
    args = parser.parse_args()

    sdg = nx.read_gpickle(args.sdg_file)
    instruction_pool = json.load(open(args.pool_file))
    result = generate_and_validate(args.instruction, sdg, instruction_pool)
    print(json.dumps(result, indent=2))
```
