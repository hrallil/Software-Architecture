import glob
import os
import sys
import create_graph as cg
import matplotlib.pyplot as plt
import networkx as nx
import pathlib
from pathlib import Path
import networkx as nx
import re
from git import *


def find_files_by_type(directory:str, filetype:str)-> list[str]:
    """
    Find all files of a specified type in a directory and its subdirectories of a specified file type.
    Args:
    - directory (str): The directory to search in.
    - filetype (str): The file type to search for (e.g., 'txt', 'py', 'jpg').

    Returns:
    - file_paths (list): A list of strings, where each element is the path to a file of the specified type.
    """
    file_paths = []

    # Walk through the directory and its subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            # Check if the file extension matches the specified filetype
            if file.endswith(filetype):
                relativePath = os.path.relpath(os.path.join(root, file), directory)
                file_paths.append(relativePath)

    return file_paths




def top_level_package(module_name, depth=1):
    components = module_name.split(".")
    return ".".join(components[:depth])

# Create a graph that abstracts the dependencies to the top level package. 
# This is done by splitting all the module names by "." and then joining the first n components.
# After splitting and pruning away all module depths beyond the specified depth, the graph is created by adding an edge between the source and destination modules.
def abstracted_to_top_level(G:nx.DiGraph|nx.Graph, depth:int=1)-> nx.DiGraph:
    aG = nx.DiGraph()
    for each in G.edges():
        src = top_level_package(each[0], depth)
        dst = top_level_package(each[1], depth)

        if src != dst:
          aG.add_edge(src, dst)
        #   print(f"Adding edge from {src} to {dst}") # for debugging

    return aG

# Draw a graph
def draw_graph(G, size, commit_counts, color, **args):
    print("displaying graph")
    plt.figure(figsize=size)
    node_sizes = calculate_node_sizes(G, commit_counts)
    pos = nx.spring_layout(G)
    nx.draw(G,pos, node_size=node_sizes, node_color=color, **args)
    plt.show()


def calculate_node_sizes(G, commit_counts):
    """
    Calculate node sizes based on commit counts.

    Args:
    - G (networkx.Graph): The graph.
    - commit_counts (dict): A dictionary mapping node names to their respective commit counts.

    Returns:
    - list: A list of node sizes corresponding to the nodes in the graph.
    """
    node_sizes = []
    max_val = max(commit_counts.values())
    min_val = min(commit_counts.values())
    for node in G.nodes():
        size = 100 + ((commit_counts.get(node, 1)-min_val)/(max_val - min_val)) * 900
        node_sizes.append(size)
    return node_sizes

# Extract all the imports and module references from a file and create a directed graph of the dependencies between the modules.
def dependencies_digraph(code_root_folder):
    files = Path(code_root_folder).rglob("*.py")

    G = nx.DiGraph()

    for file in files:
        file_path = str(file)

        source_module = module_name_from_file_path(file_path)
        if not relevant_module(source_module):
          continue

        if source_module not in G.nodes:
            G.add_node(source_module)

        for target_module in imports_from_file(file_path):

            if relevant_module(target_module):
              G.add_edge(source_module, target_module)


    return G

def module_name_from_file_path(full_path):
    """
    Converts a path to a module name. In puthon every file .py, is also a module such that zeegu.core.model.User <=> ./zeeguu/core/model/user.py
    """
    file_name = full_path[len(sys.argv[1]):]
    file_name = file_name.replace("/__init__.py","") # for linux
    file_name = file_name.replace("\__init__.py","") # for windows

    file_name = file_name.replace("/",".") # for linux
    file_name = file_name.replace("\\",".") # for windows
    file_name = file_name.replace(".py","")
    return file_name


def import_from_line(line):
    """
    Regex patterns used
    -  ^   beginning of line
    -  \S  anything that is not space
    -  +   at least one occurrence of previous
    - ( )  capture group (read more at: https://pynative.com/python-regex-capturing-groups/)
    """
    try:
      y = re.search("^from (\S+)", line)
      if not y:
        y = re.search("^import (\S+)", line)
      return y.group(1)
    except:
      return None


# extracts all the imported modules from a file
# returns a module of the form zeeguu_core.model.bookmark, e.g.
def imports_from_file(file):

    all_imports = []

    lines = [line for line in open(file)]

    for line in lines:
        imp = import_from_line(line)

        if imp:
            all_imports.append(imp)

    return all_imports

def relevant_module(module_name:str)->bool:
    """
    Filters the modules that are not relevant for the view. \n Currently only filters out test modules.
    """
    if "test" in module_name:
        return False
    if module_name.startswith("zeeguu"):
        return True
    return False

def file_path(file_name):
    return CODE_ROOT_FOLDER+file_name

def get_commit_count_file(file_name):
    repo = Repo(CODE_ROOT_FOLDER)
    commit_count = repo.git.rev_list('--count', 'HEAD', '--', file_name)
    return commit_count

def get_commit_count_repo(repo:list[str])->dict[str, int]:
    print("========== Getting commits from repository ===========")
    result = {}
    for file in repo: 
        commit_count = get_commit_count_file(file)
        result.update({file: int(commit_count)})
    return result

def get_abstraction_of(files:dict, depth:int)->dict:
    result = {}
    for file in files:
        file_new = "zeeguu."+top_level_package(module_name_from_file_path(file), depth)
        if file_new in result:
            result[file_new] += int(files[file]) # The "zeeguu."+ is added to make the module name consistent with the graph. #TODO     This could be handled better
        else:
            result[file_new] = int(files[file])
    return result

def filter_files(files:list[str])->list[str]:
    result = []
    for file in files:
        if relevant_module(file):
            result.append(file)
    return result

def get_test_modules(modules:list[str])->list[str]:
    result = []
    for module in modules:
        if "test" in module:
            result.append(module_name_from_file_path(module))
    return result

CODE_ROOT_FOLDER = sys.argv[1]

def get_tested_files(files:list[str], test_files:list[str])->dict[str, int]:
    result = {}
    for file in files:
        test_count = get_sum_tested(module_name_from_file_path(file), test_files)
        result[file] = test_count

    return result


def get_sum_tested(file:str, test_files:list[str])->int:
    result = 0
    file = file.split(".")[-1]
    for test in test_files:
        if file in test:
            result += 1
    return result


# Define a function to interpolate between red and green based on a given value
def interpolate_color(value):
    r = 1.0 - value  # Red component decreases as value increases
    g = value       # Green component increases as value increases
    b = 0.0         # Blue component stays constant
    return (r, g, b)

def get_color(color_values, G):
    color_map= []
    for node in G.nodes:
        print("node: ", node)

        try: 
            val = color_values[str(node)]
        except:
            val = 0

        color_value =  val / max(color_values.values())
        color = interpolate_color(color_value)
        color_map.append(color)
    return color_map

def main():

    # Testing 
    assert (top_level_package("zeeguu.core.model.util") == "zeeguu")
    assert (top_level_package("zeeguu.core.model.util", 2) == "zeeguu.core")
    # assert (file_path("zeeguu/core/model/user.py") == "/content/zeeguu-api/zeeguu/core/model/user.py")
    assert 'zeeguu.core.model.user' == module_name_from_file_path(file_path('zeeguu/core/model/user.py'))
    print("============ All tes  ts passed! =============")
    
    # Running
    programPath = sys.argv[1]
    depth = int(sys.argv[2])
    all_files = find_files_by_type(programPath, ".py")

    relevant_files = filter_files(all_files)
    all_tests = get_test_modules(all_files)

    tested_files = get_tested_files(relevant_files, all_tests)
    abstracted_testing_files = get_abstraction_of(tested_files, depth-1)

    print("======================== abstracted testing files =====================")
    for each in abstracted_testing_files:
        print(each, abstracted_testing_files[each])
    
    
    commits = get_commit_count_repo(relevant_files)
    abstracted_commits = get_abstraction_of(commits, depth-1)

    print("============================ abstracted commits ==========================")
    for each in abstracted_commits:
        print(each, abstracted_commits[each])

    DG = dependencies_digraph(programPath)
    ADG = abstracted_to_top_level(DG, depth)

    color_map = get_color(abstracted_testing_files, ADG)

    for node in ADG.nodes:
        print("node: ", node)

    draw_graph(ADG, (8,8), abstracted_commits, color_map, with_labels=True)

if __name__ == "__main__":
    main()


        
    


    
    