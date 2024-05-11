import glob
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

def find_files_by_type(directory, filetype):
    """
    Recursively searches the given directory for files of the specified type.

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
    

def main():
    size = len(sys.argv)
    if size < 2:
        print("Invalid input. For help do, '-h' or '--help'")
        sys.exit()

    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        print("Usage: python main.py <project_path> <filetype> [Options]")
        print("Options:")
        print("\t -f : (DEFAULT) Create a graph based on file to file dependancies, each file is a node, with edges between files that are dependant on each other.")
        print("\t\t should have a depth passed aling with this option. Example: python main.py <project_path> <filetype> -f 2")
        print("\t -i : Create a graph based on import dependancies. Shows a graph with each file as a node, with edges between files and the imports that file depends on. Node size is based on the number of imports.")
        print("\t -c : Create a graph based on class dependancy dependancies. Shows each class as a node, with edges between classes that are dependant on each other. The more dependancies between classes, the bigger the edge.")
        print("\t -g : Create a graph based on git commits. Shows the files with more commits as bigger and less commits as smaller")
        sys.exit()


    project_path = sys.argv[1]
    filetype = sys.argv[2]
    graphType = sys.argv[3] if size == 4 else "f"
    depth = sys.argv[3]

    print("looking for files in project: " + project_path + " with type: " + filetype)

    # Filters the directory and returns only files of type 'filetype'
    files = find_files_by_type(project_path, filetype)

    for file in files: 
        print("filepath: "+ file)
    # Create a graph showing file dependencies

## This project will be made to first read each file in a project, then create nodes for each file, and then create edges between the nodes based on the imports of each file.
if __name__ == "__main__":
    main()
    


    
    