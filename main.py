import os
import sys
import create_graph as cg
import matplotlib.pyplot as plt
import networkx as nx

def create_graph(files:list, flag:str="f"):
    """
    Builds a graph from a list of files. The type of graph is dictated by the flag.
    Args:
        files (list): List of files to create a graph from.
        flag (str): Flag to determine the type of graph to create.
    Returns:
        nx.Graph: A networkx graph object.
    """
    if flag == "f":
        return cg.create_graph_files(files)
    elif flag == "c":
        return cg.create_graph_directories(files)
    elif flag == "i":
        return cg.create_graph_all(files)
    elif flag == "g":
        return cg.create_graph_directories(files)
    else:
        print("Invalid flag. Please provide a valid flag.")
        return None

def extract_files(project_path:str, filetype:str=".py")-> list:
    """ 
    Extracts files from a project directory.
    Args:
        project_path (str): Path to the project directory.
        filetype (str): File type to extract from the project directory.
    Returns:
        list: List of files in the project directory.
    """

    # print("Extracting files from project: " + project_path)
    dir_list = []
    for file in os.listdir(project_path):
        if file.endswith(filetype):
            dir_list.append(file)
    return  dir_list

def file_csv(l:list[str], path:str)-> bool:
    try:
        path.strip("/")
        f = open(f"tmp/file_{path}.csv", "w")
        f.write("Files\n")
        for file in l:
            f.write(file + "\n")
        f.close()
        return True
    except Exception as e:
        print("Error creating file" + e)
        return False
    
def display_graph(graph):
    print("Displaying graph")
    nx.draw(graph, with_labels=True, font_weight='bold')
    plt.show()
    

## This project will be made to first read each file in a project, then create nodes for each file, and then create edges between the nodes based on the imports of each file.
if __name__ == "__main__":
    size = len(sys.argv)
    if size < 2:
        print("Invalid input. Please provide a path to a project. \n Example: python main.py /path/to/project -f")
        sys.exit()
    # if sys.argv[2] == "-f":
    #     project_path = sys.argv[1]
    #     files = extract_files(project_path)
    #     file_csv(files, project_path)
    #     sys.exit()
    project_path = sys.argv[1]
    filetype = sys.argv[2]
    
    files = extract_files(project_path, filetype)
    # file_csv(files, project_path)


    print("Creating graph from project: " + project_path)
    graph = create_graph(files)


    display_graph(graph)


    
    