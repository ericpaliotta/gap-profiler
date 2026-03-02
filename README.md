# gap-profiler

# Installation Guide

1. Clone the repository onto your local machine
2. *(optional)* Create a virtual environment if you do not want to modify your normal python environment. To do this run:
- `python -m venv /path/to/virtual/env` which here should be outside of the profiler package. 
- `/path/to/venv/bin/activate` to activate your virtual environment
3. run `pip install -e .` to install the package in development mode
4. run `pip install -r requirements.txt` to install all package dependencies
<br>
Congratulations! You can now run the parser and profiler. Now however, you need an example to run.

## Creating and Running examples
To generate all examples at once, navigate to the `examples/` directory and run `source gen_examples.sh`. To clear the examples run `source clear_examples.sh`. However, these examples can also be generated manually one at a time (especially useful for creating new examples). Below are instructions for how to do this.

1. Navigate into one of the example sub-directories labelled `examples/name/`.
2. In this directory there will be a file called `name.g`. Run this file by executing `path/to/gap name.g`
3. Step 2. should output a file called `name.json` (where name is still a stand-in for the example name). From the example directory run `python ../../gap_profiler/data_processsing/parser.py name.json name.zip`. Here you can additionally pass a third argument to `parser.py` specifying the "project root" directory which is a path to the top of the gap project to make finding files in the profiler interface easier. Here the additional argument would be `path/from/root/CS4098_GAP_Profiler/examples/name/`
4. Step 3. will generate the file `name.zip` which is a self-contained and portable profile which can be visualized using `python ../../gap_profiler/visualization/main.py name.zip`
<br>
Congratulations! You now have a working example.
<br>

### A few notes:
- In Step 1. of the above, navigating into the `examples/name` directory is not strictly necessary, and may seem over-complicated. However, it does keep the examples and their peripheral files grouped more neatly. This additionally makes the commands to run the parser and graphical interface more complex.
- The parser generates full profiles from the GAP generated profiles in Json (the `name.json` files)
- The command to run the parser is `path/to/parser.py input_file.json output_file.zip project_root` where `project_root` is a path to the GAP project being profiled to create a shortcut in the profiler's file explorer as previously mentioned.
- The command to run the visualization for the profile zip file is `path/to/main.py path/to/profile.zip`

# Development Guide

## Repository Structure
The source code of the repository is split into three main directories: `gap_profiler/data_processing`, `gap_profiler/data_types` and `gap_profiler/visualization`. Their functionality is summarized below
- **data_processing** : this module contains all of the functionality specific to taking the raw Json files as output by the GAP profiler and parsing them into a format which is usable by the profiler GUI. To run the main script in this module run the command `python path/to/gap_profiler/data_processing/parser.py rawprofile.json outputfilename.zip path/to/gap/project` where the third argument is optional and is a path to the top level directory of the GAP project being profiled. 
- **visualization** : this module contains all of the code to run the GUI for the profiler. All of this code is written in PyQt5, and any self-contained custom widgets are in the `gap_profiler/visualization/widgets/` directory. The command to run the profiler GUI is `gap_profiler/visualization/main.py path/to/parser/output.zip`.
- **data_types** : this module contains all data types shared between the GUI and parser. Data types such as the call graph class, the code lookup class, and all project-specific custom exceptions. It should be noted that none of the files in this module are self-contained runnable units of code. 
- **test** : this directory contains unit tests for the easily testable parts of the code. The directory structure should mirror that of the source directory with dirs named `data_types_tests` and `data_processing_tests` to test the functionality in the `data_types` and `data_processing` directories respectively.
- **documentation** : this directory contains UML diagrams for the project and other documentation resources. Any time something structural is altered in this project (new classes, moving a class to another package) make sure to update the UML diagram and other documentation files.

## Documentation
all code for this repository is commented in the Google documentation format so that any documentation can be auto-generated. See [this tutorial](https://google.github.io/styleguide/pyguide.html) for a guide on the Google python style guide format. 

The directory `docs` at the top level of this project contains all sphinx and otherwise documentation. This 
