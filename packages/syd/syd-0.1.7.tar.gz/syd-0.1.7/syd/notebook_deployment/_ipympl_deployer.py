from typing import Dict, Any, Optional
from dataclasses import dataclass
from contextlib import contextmanager
import ipywidgets as widgets
from IPython.display import display
import matplotlib.pyplot as plt
import warnings
from ..parameters import ParameterUpdateWarning

from ..viewer import Viewer
from .widgets import BaseWidget, create_widget


@contextmanager
def _plot_context():
    plt.ioff()
    try:
        yield
    finally:
        plt.ion()


@dataclass
class LayoutConfig:
    """Configuration for the viewer layout."""

    controls_position: str = "left"  # Options are: 'left', 'top'
    figure_width: float = 8.0
    figure_height: float = 6.0
    controls_width_percent: int = 30

    def __post_init__(self):
        valid_positions = ["left", "top"]
        if self.controls_position not in valid_positions:
            raise ValueError(
                f"Invalid controls position: {self.controls_position}. Must be one of {valid_positions}"
            )

    @property
    def is_horizontal(self) -> bool:
        return self.controls_position == "left"


class NotebookDeployer:
    """
    A deployment system for Viewer in Jupyter notebooks using ipywidgets.
    Built around the parameter widget system for clean separation of concerns.
    """

    def __init__(
        self,
        viewer: Viewer,
        layout_config: Optional[LayoutConfig] = None,
        continuous: bool = False,
        suppress_warnings: bool = False,
    ):
        if not isinstance(viewer, Viewer):  # type: ignore
            raise TypeError(f"viewer must be an Viewer, got {type(viewer).__name__}")

        self.viewer = viewer
        self.config = layout_config or LayoutConfig()
        self.continuous = continuous
        self.suppress_warnings = suppress_warnings

        # Initialize containers
        self.parameter_widgets: Dict[str, BaseWidget] = {}
        self.layout_widgets = self._create_layout_controls()
        self.plot_output = widgets.Output()
        self._canvas_widget = None

        # Store current figure
        self._current_figure = None
        # Flag to prevent circular updates
        self._updating = False

    def _create_layout_controls(self) -> Dict[str, widgets.Widget]:
        """Create widgets for controlling the layout."""
        controls: Dict[str, widgets.Widget] = {}

        # Controls width slider for horizontal layouts
        if self.config.is_horizontal:
            controls["controls_width"] = widgets.IntSlider(
                value=self.config.controls_width_percent,
                min=20,
                max=80,
                description="Controls Width %",
                continuous=True,
                layout=widgets.Layout(width="95%"),
                style={"description_width": "initial"},
            )
            controls["controls_width"].observe(
                self._handle_container_width_change, names="value"
            )

        return controls

    def _create_parameter_widgets(self) -> None:
        """Create widget instances for all parameters."""
        for name, param in self.viewer.parameters.items():
            widget = create_widget(
                param,
                continuous=self.continuous,
            )

            # Store in widget dict
            self.parameter_widgets[name] = widget

    def _handle_widget_engagement(self, name: str) -> None:
        """Handle engagement with an interactive widget."""
        if self._updating:
            print(
                "Already updating -- there's a circular dependency!"
                "This is probably caused by failing to disable callbacks for a parameter."
                "It's a bug --- tell the developer on github issues please."
            )
            return

        try:
            self._updating = True

            # Optionally suppress warnings during parameter updates
            with warnings.catch_warnings():
                if self.suppress_warnings:
                    warnings.filterwarnings("ignore", category=ParameterUpdateWarning)

                widget = self.parameter_widgets[name]

                if widget._is_action:
                    parameter = self.viewer.parameters[name]
                    parameter.callback(self.viewer.state)
                else:
                    self.viewer.set_parameter_value(name, widget.value)

                # Update any widgets that changed due to dependencies
                self._sync_widgets_with_state(exclude=name)

                # Update the plot
                self._update_plot()

        finally:
            self._updating = False

    def _handle_action(self, name: str) -> None:
        """Handle actions for parameter widgets."""

    def _sync_widgets_with_state(self, exclude: Optional[str] = None) -> None:
        """Sync widget values with viewer state."""
        for name, parameter in self.viewer.parameters.items():
            if name == exclude:
                continue

            widget = self.parameter_widgets[name]
            if not widget.matches_parameter(parameter):
                widget.update_from_parameter(parameter)

    def _handle_figure_size_change(self, change: Dict[str, Any]) -> None:
        """Handle changes to figure dimensions."""
        if self._current_figure is None:
            return

        self._redraw_plot()

    def _handle_container_width_change(self, change: Dict[str, Any]) -> None:
        """Handle changes to container width proportions."""
        width_percent = self.layout_widgets["controls_width"].value
        self.config.controls_width_percent = width_percent

        # Update container widths
        self.widgets_container.layout.width = f"{width_percent}%"
        self.plot_container.layout.width = f"{100 - width_percent}%"

    def _update_plot(self) -> None:
        """Update the plot with current state."""
        state = self.viewer.state

        with _plot_context():
            new_fig = self.viewer.plot(state)
            plt.close(self._current_figure)  # Close old figure
            self._current_figure = new_fig

            # Clear previous output and display new figure
            self.plot_output.clear_output(wait=True)
            with self.plot_output:
                # Make sure the canvas is created and displayed
                if self._canvas_widget is None:
                    self._canvas_widget = self._current_figure.canvas
                display(self._current_figure.canvas)

    def _redraw_plot(self) -> None:
        """Clear and redraw the plot in the output widget."""
        if self._canvas_widget is not None:
            self._canvas_widget.draw()

    def _create_layout(self) -> widgets.Widget:
        """Create the main layout combining controls and plot."""
        # Create layout controls section
        layout_box = widgets.VBox(
            [widgets.HTML("<b>Layout Controls</b>")]
            + list(self.layout_widgets.values()),
            layout=widgets.Layout(margin="10px 0px"),
        )

        # Set up parameter widgets with their observe callbacks
        for name, widget in self.parameter_widgets.items():
            widget.observe(lambda change, n=name: self._handle_widget_engagement(n))

        # Create parameter controls section
        param_box = widgets.VBox(
            [widgets.HTML("<b>Parameters</b>")]
            + [w.widget for w in self.parameter_widgets.values()],
            layout=widgets.Layout(margin="10px 0px"),
        )

        # Combine all controls
        self.widgets_container = widgets.VBox(
            [param_box, layout_box],
            layout=widgets.Layout(
                width=(
                    f"{self.config.controls_width_percent}%"
                    if self.config.is_horizontal
                    else "100%"
                ),
                padding="10px",
                overflow_y="auto",
            ),
        )

        # Create plot container
        self.plot_container = widgets.VBox(
            [self.plot_output],
            layout=widgets.Layout(
                width=(
                    f"{100 - self.config.controls_width_percent}%"
                    if self.config.is_horizontal
                    else "100%"
                ),
                padding="10px",
            ),
        )

        # Create final layout based on configuration
        if self.config.controls_position == "left":
            return widgets.HBox([self.widgets_container, self.plot_container])
        else:
            return widgets.VBox([self.widgets_container, self.plot_container])

    def deploy(self) -> None:
        """Deploy the interactive viewer with proper state management."""
        with self.viewer._deploy_app():
            # Create widgets
            self._create_parameter_widgets()

            # Create and display layout
            layout = self._create_layout()
            display(layout)

            # Create initial plot
            self._update_plot()
