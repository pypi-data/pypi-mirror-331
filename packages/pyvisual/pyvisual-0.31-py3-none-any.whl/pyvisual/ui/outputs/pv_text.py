from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont, QFontDatabase, Qt
from PySide6.QtCore import QRect


class PvText(QLabel):
    def __init__(self, container, text="Hello", x=50, y=50,
                 font="Roboto", font_size=20, font_color=(200, 200, 200, 1),
                 bold=False, italic=False, underline=False, strikethrough=False,
                 bg_color=(255, 255, 255, 0), width=300, height=None, text_alignment="left",  # Added height parameter
                 is_visible=True, opacity=1, tag=None, multiline=True,
                 paddings=[0, 0, 0, 0], line_spacing=1.0, **kwargs):
        super().__init__(text, container)
        self.move(x, y)
        self.setFixedWidth(width)

        # Font loading logic
        if isinstance(font, str) and (font.endswith('.ttf') or font.endswith('.otf')):
            font_id = QFontDatabase.addApplicationFont(font)
            families = QFontDatabase.applicationFontFamilies(font_id) if font_id != -1 else []
            font = families[0] if families else "Arial"

        # Font configuration
        self.font = QFont(font)
        self.font.setPixelSize(font_size)
        self.font.setBold(bold)
        self.font.setItalic(italic)
        self.font.setUnderline(underline)
        self.font.setStrikeOut(strikethrough)
        self.setFont(self.font)

        # Store internal values for explicit getters/setters
        self._font_color = font_color
        self._bg_color = bg_color
        self._text_alignment = text_alignment
        self._multiline = multiline
        self._line_spacing = line_spacing
        self._paddings = paddings
        self._tag = tag

        # Multiline setup
        if self._multiline:
            self.setWordWrap(True)

        # Height setup: use explicit height if provided, otherwise calculate based on text
        if height is not None:
            self.setFixedHeight(height)
        else:
            self._adjust_height(text, width, paddings)

        # Style sheet configuration
        font_r, font_g, font_b, font_a = font_color
        style = f"color: rgba({font_r}, {font_g}, {font_b}, {font_a});"
        if bg_color is not None:
            bg_r, bg_g, bg_b, bg_a = bg_color
            style += f" background-color: rgba({bg_r}, {bg_g}, {bg_b}, {bg_a});"
        self.setStyleSheet(style)

        # Alignment and layout: combine horizontal alignment with vertical centering
        alignment_map = {
            "left": Qt.AlignLeft | Qt.AlignVCenter,
            "center": Qt.AlignHCenter | Qt.AlignVCenter,
            "right": Qt.AlignRight | Qt.AlignVCenter
        }
        self.setAlignment(alignment_map.get(text_alignment, Qt.AlignLeft | Qt.AlignVCenter))
        self.setContentsMargins(*paddings)

        # Visibility and effects
        self.setVisible(is_visible)
        self.setWindowOpacity(opacity)

    def _adjust_height(self, text, width, paddings):
        font_metrics = self.fontMetrics()
        if self._multiline:
            rect = font_metrics.boundingRect(
                QRect(0, 0, width, 0),
                Qt.TextWordWrap | Qt.AlignLeft,
                text
            )
            adjusted_height = int(rect.height() * self._line_spacing + paddings[1] + paddings[3])
        else:
            adjusted_height = int(font_metrics.height() * self._line_spacing + paddings[1] + paddings[3])
        self.setFixedHeight(adjusted_height)

    # Explicit Getter and Setter Methods

    # Position X
    def get_x(self):
        return self.geometry().x()

    def set_x(self, value):
        self.move(value, self.geometry().y())

    # Position Y
    def get_y(self):
        return self.geometry().y()

    def set_y(self, value):
        self.move(self.geometry().x(), value)

    # Font Size
    def get_font_size(self):
        return self.font.pixelSize()

    def set_font_size(self, size):
        self.font.setPixelSize(size)
        self.setFont(self.font)
        self._adjust_height(self.text(), self.width(), self._paddings)

    # Bold
    def get_bold(self):
        return self.font.bold()

    def set_bold(self, value: bool):
        self.font.setBold(value)
        self.setFont(self.font)

    # Italic
    def get_italic(self):
        return self.font.italic()

    def set_italic(self, value: bool):
        self.font.setItalic(value)
        self.setFont(self.font)

    # Underline
    def get_underline(self):
        return self.font.underline()

    def set_underline(self, value: bool):
        self.font.setUnderline(value)
        self.setFont(self.font)

    # Strikethrough
    def get_strikethrough(self):
        return self.font.strikeOut()

    def set_strikethrough(self, value: bool):
        self.font.setStrikeOut(value)
        self.setFont(self.font)

    # Font Color
    def get_font_color(self):
        return self._font_color

    def set_font_color(self, value):
        self._font_color = value
        font_r, font_g, font_b, font_a = value
        new_style = f"color: rgba({font_r}, {font_g}, {font_b}, {font_a});"
        if self._bg_color is not None:
            bg_r, bg_g, bg_b, bg_a = self._bg_color
            new_style += f" background-color: rgba({bg_r}, {bg_g}, {bg_b}, {bg_a});"
        self.setStyleSheet(new_style)

    # Background Color
    def get_bg_color(self):
        return self._bg_color

    def set_bg_color(self, value):
        self._bg_color = value
        style = self.styleSheet()
        # Remove existing background color
        style = "\n".join([line for line in style.split(";") if "background-color" not in line])
        if value is not None:
            bg_r, bg_g, bg_b, bg_a = value
            style += f" background-color: rgba({bg_r}, {bg_g}, {bg_b}, {bg_a});"
        self.setStyleSheet(style)

    # Text Alignment
    def get_text_alignment(self):
        return self._text_alignment

    def set_text_alignment(self, value):
        self._text_alignment = value
        alignment_map = {
            "left": Qt.AlignLeft | Qt.AlignVCenter,
            "center": Qt.AlignHCenter | Qt.AlignVCenter,
            "right": Qt.AlignRight | Qt.AlignVCenter
        }
        self.setAlignment(alignment_map.get(value, Qt.AlignLeft | Qt.AlignVCenter))

    # Multiline
    def get_multiline(self):
        return self._multiline

    def set_multiline(self, value: bool):
        self._multiline = value
        self.setWordWrap(value)
        self._adjust_height(self.text(), self.width(), self._paddings)

    # Line Spacing
    def get_line_spacing(self):
        return self._line_spacing

    def set_line_spacing(self, value: float):
        self._line_spacing = value
        self._adjust_height(self.text(), self.width(), self._paddings)

    # Paddings
    def get_paddings(self):
        return self._paddings

    def set_paddings(self, value):
        self._paddings = value
        self.setContentsMargins(*value)
        self._adjust_height(self.text(), self.width(), value)

    # Tag
    def get_tag(self):
        return self._tag

    def set_tag(self, value):
        self._tag = value

    # Opacity
    def get_opacity(self):
        return self.windowOpacity()

    def set_opacity(self, value):
        self.setWindowOpacity(value)


# Example usage with an explicit height parameter and vertically centered text
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QWidget

    app = QApplication(sys.argv)
    window = QWidget()
    window.setGeometry(100, 100, 400, 300)

    text = PvText(window,
                  text="Transparent Background Exampledsfasdfasdfasdfasd adsfasdfa adsfasdfasdfasdfasd asdfasdfasdfasdf",
                  x=50, y=50,
                  font_size=14,
                  bg_color=None,  # No background color
                  width=300,
                  height=100,    # Explicit height parameter
                  text_alignment="left",  # Left aligned horizontally, vertically centered
                  multiline=True)

    # Using explicit getter and setter examples:
    print("Initial x position:", text.get_x())
    text.set_x(100)
    print("Updated x position:", text.get_x())

    print("Initial font size:", text.get_font_size())
    text.set_font_size(18)
    print("Updated font size:", text.get_font_size())

    print("Initial opacity:", text.get_opacity())
    text.set_opacity(0.8)
    print("Updated opacity:", text.get_opacity())

    print("Initial tag:", text.get_tag())
    text.set_tag("example_tag")
    print("Updated tag:", text.get_tag())

    window.show()
    sys.exit(app.exec())
