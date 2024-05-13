import os
import sys
import matplotlib.pyplot as plt
import networkx as nx
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




def top_level_package(module_name:str, depth:int=1)->str:
    """
    Extracts the top level package of a module name. \n
    The depth parameter specifies how many levels of the package name to keep. \n
    """
    components = module_name.split(".")
    return ".".join(components[:depth])


def abstracted_to_top_level(G:nx.DiGraph|nx.Graph, depth:int=1)-> nx.DiGraph:
    """
    Abstracts a graph to a specified depth. \n
    The depth parameter specifies how many levels of the package name to keep. \n
    """
    aG = nx.DiGraph()
    for each in G.edges():
        src = top_level_package(each[0], depth)
        dst = top_level_package(each[1], depth)

        if src != dst:
          aG.add_edge(src, dst)

    return aG

# Draw a graph
def draw_graph(G:nx.DiGraph|nx.Graph, size, commit_counts:dict, color:dict=None, **args)->None:
    """
    draws a graph if given a colour scheme and a size scheme.
    """
    print("=================== Displaying graph ===================")
    plt.figure(figsize=size)
    node_sizes = calculate_node_sizes(G, commit_counts) if commit_counts else [100]*len(G.nodes)
    pos = nx.spring_layout(G)
    nx.draw(G,pos, node_size=node_sizes, node_color=color, **args)
    plt.show()


def calculate_node_sizes(G:nx.DiGraph|nx.Graph, commit_counts:dict)->list[int]:
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
        size = 100 + ((commit_counts.get(node, 1)-min_val)/(max_val - min_val)) * 9900
        node_sizes.append(size)
    return node_sizes

def dependencies_digraph(code_root_folder:str)->nx.DiGraph:
    """
    Creates a graph based on a directory.
    This graph will show a model view of the directory. \n
    The nodes are the modules and the edges are the imports. \n
    Every file will have to import another file if it wants to use it, letting this graph be a good representation of the dependencies between the modules. \n
    """
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

def module_name_from_file_path(full_path:str)->str:
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


def import_from_line(line:str)->str:
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


def imports_from_file(file)->list[str]:
    """
    Extracts all the imported modules from a file\n
    Returns a module of the form zeeguu_core.model.bookmark
    """
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

def file_path(file_name:str)->str:
    """
    Concatinates the CODE_ROOT_FOLDER with the file name
    """
    return CODE_ROOT_FOLDER+file_name

def get_commit_count_file(file_name:str)->int:
    """
    retrieves the commit history for a file
    """
    repo = Repo(CODE_ROOT_FOLDER)
    commit_count = repo.git.rev_list('--count', 'HEAD', '--', file_name)
    return commit_count

def get_commit_count_repo(repo:list[str])->dict[str, int]:
    """
    Retrieves the commit history for a repository
    """
    print("========== Getting commits from repository ===========")
    result = {}
    for file in repo: 
        commit_count = get_commit_count_file(file)
        result.update({file: int(commit_count)})
    return result

def get_abstraction_of(files:dict, depth:int)->dict:
    """
    Abstracts away the file names to a specified depth. \n
    The depth parameter specifies how many levels of the package name to keep. \n
    """
    result = {}
    for file in files:
        file_new = "zeeguu."+top_level_package(module_name_from_file_path(file), depth)
        if file_new in result:
            result[file_new] += int(files[file]) # The "zeeguu."+ is added to make the module name consistent with the graph. #TODO     This could be handled better
        else:
            result[file_new] = int(files[file])
    return result

def filter_files(files:list[str])->list[str]:
    """
    Takes a list of files, and filters out the ones that are not relevant for the view.
    """
    result = []
    for file in files:
        if relevant_module(file):
            result.append(file)
    return result

def get_test_modules(files:list[str])->list[str]:
    """
    Takes a list of files, and filters out the ones that are not test files.
    Returns the list of test files, converted to module names.
    """
    result = []
    for file in files:
        if "test" in file:
            result.append(module_name_from_file_path(file))
    return result


def get_tested_files(files:list[str], test_files:list[str])->dict[str, int]:
    """
    Takes a list of files 'a', and a list of test files 'b', and returns a dictionary with the number of tests that have tested each file from 'a'.
    """
    result = {}
    for file in files:
        test_count = get_sum_tested(module_name_from_file_path(file), test_files)
        result[file] = test_count

    return result


def get_sum_tested(module:str, test_files:list[str])->int:
    """
    Gets a Module and compares it to the testing files. Returns a count of how many testing files refer to it\n
    The count is  based off of the naming convention of the files. \n
    If a file is named 'zeeguu.core.model.bookmark.py', and a test file is named 'zeeguu.core.model.test_bookmark.py', then the file is considered tested.
    """
    result = 0
    module = module.split(".")[-1]
    for test in test_files:
        if module in test:
            result += 1
    return result


def interpolate_color(value:int)->tuple:
    """
    A function which will interpolate a color between red and green based on a value between 0 and 1.
    """
    r = 1.0 - value  # Red component decreases as value increases
    g = value       # Green component increases as value increases
    b = 0.0         # Blue component stays constant
    return (r, g, b)

def get_color(color_values:dict, G:nx.DiGraph|nx.Graph)->list[tuple]:
    """
    creates a color map based on the values in the color_values dictionary, and all the nodes in G.\n
    The color map is interpolated between red and green based on the value of the node in the color_values dictionary.
    """
    color_map= []
    for node in G.nodes:
        try: 
            val = color_values[str(node)]
        except:
            val = 0

        color_value =  val / max(color_values.values())
        color = interpolate_color(color_value)
        color_map.append(color)
    return color_map

CODE_ROOT_FOLDER = sys.argv[1]
def main():
    """
    The main function of the program. \n
    """

    # The tests that came with the google colab
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

    print("======================== Abstracted testing files =====================")
    for each in abstracted_testing_files:
        print(each, abstracted_testing_files[each])
    
    
    commits = get_commit_count_repo(relevant_files)
    abstracted_commits = get_abstraction_of(commits, depth-1)

    print("============================ Abstracted commits ==========================")
    for each in abstracted_commits:
        print(each, abstracted_commits[each])

    DG = dependencies_digraph(programPath)
    ADG = abstracted_to_top_level(DG, depth)

    color_map = get_color(abstracted_testing_files, ADG)

    draw_graph(ADG, (8,8), abstracted_commits, color_map, with_labels=True)

if __name__ == "__main__":
    main()
