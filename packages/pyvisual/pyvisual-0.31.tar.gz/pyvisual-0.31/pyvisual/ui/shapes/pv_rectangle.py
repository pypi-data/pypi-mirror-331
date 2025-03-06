from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QBrush

class PvRectangle(QWidget):
    def __init__(self, container, x=100, y=100, width=100, height=100,
                 corner_radius=0, bg_color=(255, 0, 255, 1),
                 border_color=None, border_thickness=0,
                 is_visible=True, opacity=1, tag=None):
        super().__init__(container)

        # Store properties
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._corner_radius = corner_radius
        self._bg_color = bg_color
        self._border_color = border_color
        self._border_thickness = border_thickness
        self._is_visible = is_visible
        self._opacity = opacity
        self._tag = tag

        # Set visibility
        self.setVisible(is_visible)

        # Adjust widget size to fit the rectangle
        self.adjust_size()

    def adjust_size(self):
        """Adjust the widget size to fit the rectangle."""
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

        # Set background brush if bg_color is provided, otherwise disable it
        if self._bg_color is not None:
            brush = QBrush(QColor(int(self._bg_color[0]),
                                  int(self._bg_color[1]),
                                  int(self._bg_color[2]),
                                  int(self._bg_color[3]) * 255))
            painter.setBrush(brush)
        else:
            painter.setBrush(Qt.NoBrush)

        # Set border: disable pen if no border should be drawn
        if self._border_thickness > 0 and self._border_color is not None:
            pen = QPen(QColor(int(self._border_color[0]),
                              int(self._border_color[1]),
                              int(self._border_color[2]),
                              int(self._border_color[3]) * 255))
            pen.setWidth(self._border_thickness)
            painter.setPen(pen)
        else:
            painter.setPen(Qt.NoPen)

        # Draw the rectangle with optional rounded corners
        painter.drawRoundedRect(self._border_thickness // 2,
                                self._border_thickness // 2,
                                self._width, self._height,
                                self._corner_radius, self._corner_radius)

    # Explicit getter and setter methods in snake_case
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

    def get_corner_radius(self):
        return self._corner_radius

    def set_corner_radius(self, corner_radius):
        self._corner_radius = corner_radius
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
    window = pv.PvWindow(title="PvRectangle Example")

    # Create a PvRectangle with no background and no border
    rectangle = PvRectangle(
        container=window,
        x=50,
        y=50,
        width=200,
        height=100,
        corner_radius=15,
        bg_color=None,           # No background fill
        border_color=None,       # No border color
        border_thickness=0,      # No border thickness
        is_visible=True,
        opacity=1
    )

    # Demonstrate usage of getters and setters
    print("Initial width:", rectangle.get_width())
    rectangle.set_width(250)
    print("Updated width:", rectangle.get_width())

    # Show the window
    window.show()

    # Run the application
    app.run()
