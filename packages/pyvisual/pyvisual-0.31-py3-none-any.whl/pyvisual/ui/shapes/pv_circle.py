from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QBrush

class PvCircle(QWidget):
    def __init__(self, container, radius=30, x=100, y=100, width=None, height=None,
                 bg_color=(0, 0, 255, 1), border_color=None, border_thickness=0,
                 is_visible=True, opacity=1, tag=None):
        super().__init__(container)

        # If width or height not provided, default to diameter based on radius
        if width is None:
            width = radius * 2
        if height is None:
            height = radius * 2

        # Store properties
        self._radius = radius  # reference value; may be used to update width/height if desired
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._bg_color = bg_color
        self._border_color = border_color
        self._border_thickness = border_thickness
        self._is_visible = is_visible
        self._opacity = opacity
        self._tag = tag

        # Set visibility
        self.setVisible(is_visible)

        # Adjust widget size to fit the circle/ellipse
        self.adjust_size()

    def adjust_size(self):
        """Adjust the widget size to fit the circle (or ellipse)."""
        self.setGeometry(self._x - self._border_thickness,
                         self._y - self._border_thickness,
                         self._width + self._border_thickness * 2,
                         self._height + self._border_thickness * 2)

    def paintEvent(self, event):
        if not self._is_visible:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set opacity
        painter.setOpacity(self._opacity)

        # Set background brush if bg_color is provided, otherwise disable fill
        if self._bg_color is not None:
            color = QColor(int(self._bg_color[0]),
                           int(self._bg_color[1]),
                           int(self._bg_color[2]),
                           int(self._bg_color[3] * 255))
            brush = QBrush(color)
            painter.setBrush(brush)
        else:
            painter.setBrush(Qt.NoBrush)

        # Set border pen if thickness > 0 and border_color is provided
        if self._border_thickness > 0 and self._border_color is not None:
            color = QColor(int(self._border_color[0]),
                           int(self._border_color[1]),
                           int(self._border_color[2]),
                           int(self._border_color[3] * 255))
            pen = QPen(color)
            pen.setWidth(self._border_thickness)
            painter.setPen(pen)
        else:
            painter.setPen(Qt.NoPen)

        # Draw the ellipse (circle if width == height)
        painter.drawEllipse(self._border_thickness,
                            self._border_thickness,
                            self._width,
                            self._height)

    # Explicit getter and setter methods in snake_case
    def get_radius(self):
        return self._radius

    def set_radius(self, radius):
        self._radius = radius
        # Optionally update width and height to maintain a circle
        self._width = radius * 2
        self._height = radius * 2
        self.adjust_size()
        self.update()

    def get_x(self):
        return self._x

    def set_x(self, x):
        self._x = x
        self.adjust_size()
        self.update()

    def get_y(self):
        return self._y

    def set_y(self, y):
        self._y = y
        self.adjust_size()
        self.update()

    def get_width(self):
        return self._width

    def set_width(self, width):
        self._width = width
        self.adjust_size()
        self.update()

    def get_height(self):
        return self._height

    def set_height(self, height):
        self._height = height
        self.adjust_size()
        self.update()

    def get_bg_color(self):
        return self._bg_color

    def set_bg_color(self, bg_color):
        self._bg_color = bg_color
        self.update()

    def get_border_color(self):
        return self._border_color

    def set_border_color(self, border_color):
        self._border_color = border_color
        self.update()

    def get_border_thickness(self):
        return self._border_thickness

    def set_border_thickness(self, border_thickness):
        self._border_thickness = border_thickness
        self.adjust_size()
        self.update()

    def get_is_visible(self):
        return self._is_visible

    def set_is_visible(self, is_visible):
        self._is_visible = is_visible
        self.setVisible(is_visible)

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, opacity):
        self._opacity = opacity
        self.update()

# Example Usage
if __name__ == "__main__":
    import pyvisual as pv

    app = pv.PvApp()

    # Create a window
    window = pv.PvWindow(title="PvCircle Example")

    # Create a PvCircle with explicit width and height and no errors for None colors
    circle = PvCircle(
        container=window,
        radius=50,    # Used as reference if width/height are not provided
        x=150,
        y=150,
        width=120,    # Explicit width
        height=120,   # Explicit height (equal to width for a circle)
        bg_color=None,           # No background fill
        border_color=None,       # No border color
        border_thickness=0,
        is_visible=True,
        opacity=0.5  # Semi-transparent
    )

    # Optionally demonstrate setter/getter usage:
    print("Initial x:", circle.get_x())
    circle.set_x(200)
    print("Updated x:", circle.get_x())

    # Show the window
    window.show()

    # Run the application
    app.run()
