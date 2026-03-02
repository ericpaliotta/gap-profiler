#!/bin/bash
# this file generates all documentation at the top level of this repository

# generate profiler docs
echo "generating profiler docs..."
pandoc --number-sections profiler_docs/profiler_docs.md -o profiler_docs.pdf

# generates user guide documentation
echo "generating user guide..."
pandoc --number-sections user_guide/user_guide.md -o user_guide.pdf

# generates UML diagram
echo "generating class diagram..."
plantuml ./diagrams/class_diagram.puml -o ../

# generates sphinx documentation
echo "generating sphinx docs..."
cd sphinx_docs
sphinx-apidoc -f -o source ../../gap_profiler
make html
cd ../
# constructs a symlink to the actual html so that the docs can be accessed easily
ln -s sphinx_docs/build/html/gap_profiler.html ./sphinx_docs.html
echo "success"
