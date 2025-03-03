# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DashGridLayout(Component):
    """A DashGridLayout component.
DashGridLayout is a flexible grid layout system for arranging and moving components within a Dash application.
It leverages the react-grid-layout library to provide responsive and draggable grid items.

Keyword arguments:

- id (string; optional):
    The ID used to identify this component in Dash callbacks.

- autoSize (boolean; default True):
    Prevents dragging items outside the container.

- breakpointData (dict; optional):
    Data about the current breakpoint and columns.

    `breakpointData` is a dict with keys:

    - newBreakpoint (string; optional)

    - newCols (number; optional)

- breakpoints (dict; default {lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0}):
    Breakpoints for responsive layout.

    `breakpoints` is a dict with keys:

    - lg (number; optional)

    - md (number; optional)

    - sm (number; optional)

    - xs (number; optional)

    - xxs (number; optional)

- className (string; default 'layout'):
    CSS class name for the grid layout.

- cols (dict; default {lg: 12, md: 10, sm: 6, xs: 4, xxs: 2}):
    An object containing breakpoints and column numbers.

- compactType (a value equal to: 'vertical', 'horizontal', null; default 'vertical'):
    Compaction type. Can be 'vertical', 'horizontal', or None.

- currentLayout (list of dicts; optional):
    The current layout of the grid items.

    `currentLayout` is a list of dicts with keys:

    - h (number; optional)

    - i (string; optional)

    - w (number; optional)

    - x (number; optional)

    - y (number; optional)

- itemCount (number; optional):
    The number of items in the grid.

- itemLayout (list of dicts; optional):
    Layout configuration for each item.

    `itemLayout` is a list of dicts with keys:

    - h (number; optional)

    - i (string; optional)

    - w (number; optional)

    - x (number; optional)

    - y (number; optional)

- itemToRemove (boolean | number | string | dict | list; default ''):
    The item in the grid that should be removed when triggered.

- items (list of a list of or a singular dash component, string or numbers; optional):
    List of items to be rendered in the grid.

- maxRows (number; default Infinity):
    If True, the container height swells and contracts to fit
    contents.

- rowHeight (number; default 100):
    The height of a single row in pixels.

- showRemoveButton (boolean; default True):
    Whether to show remove buttons for grid items.

- showResizeHandles (boolean; default True):
    Whether to show resize handles for grid items.

- style (dict; optional):
    Inline styles for the grid layout."""
    _children_props = ['items']
    _base_nodes = ['items', 'children']
    _namespace = 'dash_dynamic_grid_layout'
    _type = 'DashGridLayout'
    @_explicitize_args
    def __init__(self, maxRows=Component.UNDEFINED, autoSize=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, rowHeight=Component.UNDEFINED, cols=Component.UNDEFINED, style=Component.UNDEFINED, itemCount=Component.UNDEFINED, itemToRemove=Component.UNDEFINED, compactType=Component.UNDEFINED, showRemoveButton=Component.UNDEFINED, showResizeHandles=Component.UNDEFINED, items=Component.UNDEFINED, itemLayout=Component.UNDEFINED, currentLayout=Component.UNDEFINED, breakpointData=Component.UNDEFINED, breakpoints=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'autoSize', 'breakpointData', 'breakpoints', 'className', 'cols', 'compactType', 'currentLayout', 'itemCount', 'itemLayout', 'itemToRemove', 'items', 'maxRows', 'rowHeight', 'showRemoveButton', 'showResizeHandles', 'style']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'autoSize', 'breakpointData', 'breakpoints', 'className', 'cols', 'compactType', 'currentLayout', 'itemCount', 'itemLayout', 'itemToRemove', 'items', 'maxRows', 'rowHeight', 'showRemoveButton', 'showResizeHandles', 'style']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        super(DashGridLayout, self).__init__(**args)
