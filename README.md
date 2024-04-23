# Software-Architecture

Repository containing a project for extracting a form of diagram which can be used for graphing the architecture of the software.

### Notes for possible visualization:

- Make notes bigger if they have more dependancies going in or out
- Making arrows wider if there is more connections between 2 nodes.
- Mark circular dependancies in red
- Add numbers next to edges in graph
- Allow for 2 views, based on flag (python3 main.py [path] [flag]) Flag types:
  - -f: file relation, shows files and how they call eachother
  - -c: class relation, shows classes, and maybe methods
  - -i: import relation, shows imports and which files depend on which files.
  - -g: git commit view: make node size dependant on the amount of commits pushed to git for that file/module/ what ever

### Nice to haves:

- Initially shows the most abstract view, and then double clicking will expand the component to a lower abstraction. This can be done by using depth of the connections-tree of the files/dependancies... Teacher said smt about it the 15th of april.
