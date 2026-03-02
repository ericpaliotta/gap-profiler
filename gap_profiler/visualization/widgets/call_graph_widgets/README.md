# Call Graph Visualization Widgets
this directory contains a number of types of visualizations and accessory widgets for the Call Graph

## Adding new visualizations
before adding new visualizations, you must understand the elements involved.
- **CallGraphWidget** (in `gap_profiler/visualization/widgets/call_graph_vis.py`) : the wrapper class for all visualizations of the call graph data structure. This data structure manages all signals between visualizations, filters, and tabs to alternate between views. While adding a new visualization class involves adding a few lines to this class (i.e. adding the widget to the tabs) but modifying the overall structure of the class should be avoided. 
- **AbstractCallGraphWidget** (in `gap_profiler/visualization/widgets/call_graph_widgets/abstract_call_graph_widget.py`): this is the abstract class which defines all public functions and some shared functionality for all CallGraph visualizations. In order to implement this widget, you must implement three functions: `_config_models`, `highlight_node`, and `highlight_in_file`. This abstract class defines the models (both proxy and actual) as well as the tree view for displaying the model. This class also defines some shared methods, and formatting things so that the different visualizations of the call graph are uniform. Modifying this class in any structural way will likely require editing of all derived classes so do so at your own risk. 
- **CallGraphVisualizationDelegate** (in `gap_profiler/visualization/widgets/call_graph_widgets/abstract_call_graph_widget.py`) : this class is a delegate which dynamically creates widgets (visualization element widgets as described below) for each index in the model. This is an essential component as it allows for filtering widgets dynamically (if the widgets are statically linked to model indices the widgets are deleted upon filtering). Do not modify this class except to add a line to the `createEditor()` method to return a new widget if you create one. For this to be possible you must also add a line to the `WidgetType` class in the same file.
- **the visualization itself** (i.e. CallTree etc.) : the class which takes care of the actual visualization of the call graph. To write your own version of this first study one of the existant widgets.
- **visualization element widgets** : your view will likely require some small widget to visualize each function call as a unit. It is easiest to have a sub-class of `QWidget` to do this. Look at the code for `CallTreeElement` for an example.

Now that you have an understanding of each of the elements that go into creating a CallGraph visualization widget, it is time to implement:
1. Create a file in `gap_profiler/visualization/widgets/call_graph_widgets/` to hold your widget and paste in the following (note that `highlight_node` and `highlight_in_file` are defined in children because there is no universal way for child classes to track items in the source model for these operations (if you can think of a way to do this please do):

```python
class YourClassName(AbstractCallGraphWidget):
    def _config_models(self) -> None:
        '''method to populate model with items'''
        pass

    def highlight_node(self, node_id: str, mode=None) -> None:
        '''highlights a node with the given id'''
        mode = mode if mode else QItemSelectionModel.SelectCurrent
        pass

    def highlight_in_file(self, id: int) -> None:
        '''highlights all nodes in a given file with the given id'''
        pass
```
in addition to implementing these methods, make sure the `highlight_node` method is called from the `CallGraphWrapperWidget` class in the `_list_node_highlighted` and `_tree_node_highlighted` methods. Create a corresponding method the newly created view equivalent to these.

2. Implement a child element widget class if necessary.

3. Implement all of the methods in the above snippets. See `CallTree` for an example

4. Add the new widget to `CallGraphWrapperWidget` in a new tab in the tab widget for that class.

5. Add your child element widget class to the `CallGraphVisualizationDelegate` in the `createEditor` method. To do this you will need to add an attribute to the `WidgetType` class for your new type of visualization element widget. 