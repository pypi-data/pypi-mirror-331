from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPixmap, QTransform, QPainterPath, QColor, QPen
from PySide6.QtCore import Qt, QEvent

class PvImage(QWidget):
    def __init__(self, container=None, x=0, y=0, image_path="", scale=1.0, corner_radius=0,
                 flip_v=False, flip_h=False, rotate=0, is_visible=True, opacity=1, tag=None,
                 border_color=None, border_hover_color=None, border_thickness=5):
        super().__init__(container)

        # Store properties
        self._x = x
        self._y = y
        self._image_path = image_path
        self._scale = scale
        self._corner_radius = corner_radius
        self._flip_v = flip_v
        self._flip_h = flip_h
        self._rotate = rotate
        self._is_visible = is_visible
        self._opacity = opacity
        self._tag = tag
        self._border_thickness = border_thickness*2
        self._hovered = False

        # Only create QColor if a color tuple is provided; otherwise, leave as None.
        self._border_color = QColor(border_color[0], border_color[1], border_color[2],
                                    int(border_color[3] * 255)) if border_color else None
        self._border_hover_color = (QColor(border_hover_color[0], border_hover_color[1], border_hover_color[2],
                                           int(border_hover_color[3] * 255))
                                    if border_hover_color else self._border_color)


        # Load image
        self._pixmap = QPixmap(image_path) if image_path else QPixmap()

        # Transform image
        self.apply_transformations()

        # Set visibility
        self.setVisible(is_visible)

        # Adjust widget size to fit the image
        self.adjust_size()

        # Enable mouse tracking
        self.setMouseTracking(True)

    def apply_transformations(self):
        """Apply scaling, flipping, and rotation to the pixmap."""
        if not self._pixmap.isNull():
            transform = QTransform()

            # Flip horizontally or vertically
            if self._flip_h:
                transform.scale(-1, 1)
            if self._flip_v:
                transform.scale(1, -1)

            # Rotate
            transform.rotate(self._rotate)

            # Apply transformations
            self._pixmap = self._pixmap.transformed(transform, Qt.SmoothTransformation)

            # Scale
            self._pixmap = self._pixmap.scaled(self._pixmap.width() * self._scale, self._pixmap.height() * self._scale, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def adjust_size(self):
        """Adjust the widget size to fit the image."""
        if not self._pixmap.isNull():
            self.setGeometry(self._x, self._y, self._pixmap.width(), self._pixmap.height())

    def paintEvent(self, event):
        if not self._is_visible or self._pixmap.isNull():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Set opacity
        painter.setOpacity(self._opacity)

        # Draw the image with rounded corners if needed
        if self._corner_radius > 0:
            path = QPainterPath()
            path.addRoundedRect(self.rect(), self._corner_radius, self._corner_radius)
            painter.setClipPath(path)

        # Draw image
        painter.drawPixmap(0, 0, self._pixmap)

        # Draw border only if a border color is provided
        border_color = self._border_hover_color if self._hovered else self._border_color
        if border_color:
            pen = QPen(border_color, self._border_thickness)
            painter.setPen(pen)
            painter.drawRoundedRect(self.rect(), self._corner_radius, self._corner_radius)

    def enterEvent(self, event):
        """Handle mouse hover enter event."""
        self._hovered = True
        self.update()

    def leaveEvent(self, event):
        """Handle mouse hover leave event."""
        self._hovered = False
        self.update()

    # Getters and Setters for new properties
    def get_border_color(self):
        return self._border_color

    def set_border_color(self, border_color):
        self._border_color = QColor(*border_color)
        self.update()

    def get_border_hover_color(self):
        return self._border_hover_color

    def set_border_hover_color(self, border_hover_color):
        self._border_hover_color = QColor(*border_hover_color)
        self.update()

    def get_border_thickness(self):
        return self._border_thickness

    def set_border_thickness(self, border_thickness):
        self._border_thickness = border_thickness
        self.update()


# Example Usage
if __name__ == "__main__":
    import pyvisual as pv

    app = pv.PvApp()

    # Create a window
    window = pv.PvWindow(title="PvImage Example")

    # Create a PvImage
    image = PvImage(
        container=window,
        x=50,
        y=50,
        image_path="C:/Users/Murtaza Hassan/Pictures/IMG_6006.JPG",  # Replace with your image path
        scale=0.5,
        corner_radius=60,
        opacity=1,
        border_color=(255, 10, 10, 255),
        border_hover_color=(0, 255, 0, 255),
        border_thickness=30
    )

    # Show the window
    window.show()

    # Run the application
    app.run()
