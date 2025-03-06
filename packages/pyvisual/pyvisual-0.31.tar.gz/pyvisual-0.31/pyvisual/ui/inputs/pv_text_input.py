from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QLabel
from PySide6.QtGui import QFont, QPixmap, QPainter, QColor
from PySide6.QtSvgWidgets import QSvgWidget
from pyvisual.utils.helper_functions import add_shadow_effect, draw_border, update_svg_color
from PySide6.QtCore import Qt
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression

class PvTextInput(QWidget):
    def __init__(self, container, x=50, y=50, width=200, height=40, background_color=(255, 255, 255, 1),
                 visibility=True, placeholder="Enter your text here...", text_alignment="left",
                 default_text="", paddings=(10, 0, 20, 0), font="Roboto", font_size=10,
                 font_color=(0, 0, 0, 1), border_color=(0, 0, 0, 1), border_thickness=1,
                 corner_radius=5, box_shadow=None, icon_path=None, icon_scale=1.0, icon_position="left",
                 icon_spacing=10, icon_color=None,text_type="text",is_visible=True):
        super().__init__(container)

        self._border_thickness = border_thickness
        self._background_color = background_color
        self._placeholder = placeholder
        self._default_text = default_text
        self._paddings = paddings
        self._font = font
        self._font_size = font_size
        self._font_color = font_color
        self._border_color = border_color
        self._corner_radius = corner_radius
        self._box_shadow = None
        self._icon_path = icon_path
        self._icon_scale = icon_scale
        self._icon_position = icon_position
        self._icon_spacing = icon_spacing
        self._text_alignment = text_alignment
        self._text_type = text_type
        self._is_visible = is_visible

        max_corner_radius = (height / 2) - 1
        if self._corner_radius > max_corner_radius:
            self._corner_radius = max_corner_radius

        # Set widget geometry
        self.setGeometry(x, y, width, height)

        # Create layout
        self._layout = QHBoxLayout(self)
        # self._paddings is defined as (top, right, bottom, left)
        # top, right, bottom, left = self._paddings
        # # Rearrange to match Qt's order: left, top, right, bottom
        self._layout.setContentsMargins(*self._paddings)
        self._layout.setSpacing(self._icon_spacing)

        # Add icon if provided
        if self._icon_path:
            self._icon_widget = self._create_icon_widget()
            print(self._icon_widget)
            if icon_color:
                update_svg_color(self._icon_widget, icon_color)
            if self._icon_widget and self._icon_position == "left":
                self._layout.addWidget(self._icon_widget)

        # Create QLineEdit
        self._line_edit = QLineEdit(self)
        self._line_edit.setPlaceholderText(self._placeholder)
        self._line_edit.setText(self._default_text)


        # Set font
        font = QFont(self._font)
        font.setPixelSize(self._font_size)
        # font.setBold(self._bold)
        # font.setItalic(self._italic)
        # font.setUnderline(self._underline)
        # font.setStrikeOut(self._strikeout)

        self._line_edit.setFont(font)
        self._line_edit.setStyleSheet("background: transparent;")  # Make QLineEdit background transparent
        self._configure_text_type()

        # Set text alignment
        alignment_map = {
            "left": Qt.AlignLeft,
            "center": Qt.AlignCenter,
            "right": Qt.AlignRight
        }
        self._line_edit.setAlignment(alignment_map.get(self._text_alignment, Qt.AlignLeft))

        self._layout.addWidget(self._line_edit)

        # Add icon to the right if specified
        if self._icon_path:
            if self._icon_widget and self._icon_position == "right":
                self._layout.addWidget(self._icon_widget)

        # Set visibility
        self.setVisible(visibility)

        # Update styles
        self.update_style()

    def _create_icon_widget(self):
        """Creates the QLabel or QSvgWidget for the icon."""
        if self._icon_path.endswith(".svg"):
            try:
                with open(self._icon_path, "r") as file:
                    svg_content = file.read()
                    icon_widget = QSvgWidget(self)
                    icon_widget.load(svg_content.encode("utf-8"))
                    icon_widget._original_svg = svg_content  # Store the original SVG content
                    icon_size = int(24 * self._icon_scale)
                    icon_widget.setFixedSize(icon_size, icon_size)
                    icon_widget.setStyleSheet("background-color: transparent;")
                    return icon_widget
            except FileNotFoundError:
                print(f"SVG file '{self._icon_path}' not found.")
                return None
        else:
            icon_widget = QLabel(self)
            pixmap = QPixmap(self._icon_path)
            icon_size = int(24 * self._icon_scale)
            icon_widget.setPixmap(pixmap.scaled(icon_size, icon_size))
            icon_widget.setFixedSize(icon_size, icon_size)
            icon_widget.setStyleSheet("background: transparent;")
            return icon_widget

    def update_style(self):
        """Update the styles of the parent widget and QLineEdit."""
        # Apply background color to the parent widget
        r, g, b, a = self._background_color
        self.setStyleSheet(f"""
               background-color: rgba({r}, {g}, {b}, {a});
               border-radius: {self._corner_radius}px;
           """)

        # Apply styles to QLineEdit
        font_r, font_g, font_b, font_a = self._font_color
        self._line_edit.setStyleSheet(f"""
               QLineEdit {{
                   background-color: transparent;
                   color: rgba({font_r}, {font_g}, {font_b}, {font_a});
                   border: none;
               }}
           """)

        if self._box_shadow:
            add_shadow_effect(self, self._box_shadow)

    def paintEvent(self, event):
        """Override paint event to handle custom background and border."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background with rounded corners
        r, g, b, a = self._background_color
        color = QColor(r, g, b, int(a * 255))  # Convert alpha to 0-255 range
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        rect = self.rect()
        painter.drawRoundedRect(rect, self._corner_radius, self._corner_radius)

        # Draw border
        draw_border(self, painter, self._border_color, self._border_thickness, self._corner_radius)

        super().paintEvent(event)

    def _configure_text_type(self):
        """Configure the QLineEdit based on the text type."""
        if self._text_type == "Number":
            number_regex = QRegularExpression(r"^\d*$")  # Matches any sequence of digits, including empty input
            number_validator = QRegularExpressionValidator(number_regex, self._line_edit)
            self._line_edit.setValidator(number_validator)
            # self._line_edit.setPlaceholderText("e.g., 123456789")

        elif self._text_type == "Email":
            email_regex = QRegularExpression(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
            email_validator = QRegularExpressionValidator(email_regex, self._line_edit)
            self._line_edit.setValidator(email_validator)
            # self._line_edit.setPlaceholderText("e.g., example@domain.com")

        elif self._text_type == "Password":
            self._line_edit.setEchoMode(QLineEdit.Password)

        elif self._text_type == "CreditCard":
            # Use a validator that allows up to 16 digits with optional spaces.
            # This regex accepts 0-4 digits followed by up to three groups of an optional space and 0-4 digits.
            credit_card_regex = QRegularExpression(r"^\d{0,4}( ?\d{0,4}){0,3}$")
            credit_card_validator = QRegularExpressionValidator(credit_card_regex, self._line_edit)
            self._line_edit.setValidator(credit_card_validator)
            self._line_edit.setPlaceholderText("0000 0000 0000 0000")
            # Ensure left alignment so text doesn't start from the right.
            self._line_edit.setAlignment(Qt.AlignLeft)
            # Connect the textChanged signal to a slot that reformats the text.
            self._line_edit.textChanged.connect(self._format_credit_card)

        else:
            self._line_edit.setInputMask("")  # Clear any input mask

    def _format_credit_card(self, text):
        """
        Reformats the input text to insert a space after every 4 digits.
        This avoids using an input mask so that placeholder text or underscores are not shown.
        """
        # Remove any existing spaces
        digits = text.replace(" ", "")
        # Group digits into chunks of 4
        groups = [digits[i:i + 4] for i in range(0, len(digits), 4)]
        new_text = " ".join(groups)

        if new_text != text:
            # Optionally, preserve the cursor position. For simplicity, here we move it to the end.
            cursor_position = self._line_edit.cursorPosition()
            self._line_edit.blockSignals(True)  # Prevent recursive calls
            self._line_edit.setText(new_text)
            self._line_edit.setCursorPosition(len(new_text))
            self._line_edit.blockSignals(False)

    def get_text(self):
        return self._line_edit.text()

    def set_text(self,text):
        self._line_edit.setText(text)

    def set_cursor_position(self, position):
        """Set the cursor position in the text input."""
        self._line_edit.setCursorPosition(position)


# Example Usage
if __name__ == "__main__":
    import pyvisual as pv

    app = pv.PvApp()

    # Create a window
    window = pv.PvWindow(title="PvTextInput with Icon Example")

    # Create a PvTextInput with an icon
    text_input = PvTextInput(
        container=window,
        x=50,
        y=50,
        width=300,
        height=50,
        background_color=(240, 240, 240, 1),
        placeholder="Type here...",
        font_color=(0, 0, 0, 1),
        border_color=(0, 120, 215, 1),
        corner_radius=25,
        default_text="",
        border_thickness=0,
        icon_path="../../assets/icons/more/play.svg",
        # Replace with your icon path
        icon_position="right",
        icon_scale=1.2,
        icon_spacing=10,
        icon_color=(150, 0, 0, 1),
        paddings=(30,0,30,0),
        text_type="numbers"
    )

    # Create a PvTextInput with an icon
    text_input2 = PvTextInput(
        container=window,
        x=50,
        y=120,
        width=300,
        height=50,
        background_color=(240, 240, 240, 1),
        placeholder="Password",
        font_color=(0, 0, 0, 1),
        border_color=(0, 120, 215, 1),
        corner_radius=0,
        default_text="",
        border_thickness=0,
        icon_path="../../assets/icons/more/lock.svg",
        # Replace with your icon path
        icon_position="left",
        icon_scale=0.8,
        icon_spacing=10,
        icon_color=(150, 150, 150, 1),
        text_type="password"
    )

    text_input3 = PvTextInput(
        container=window,
        x=50,
        y=220,
        width=300,
        height=50,
        background_color=(245, 245, 245, 1),
        placeholder="Email",
        font_color=(0, 0, 0, 1),
        border_color=(0, 120, 215, 1),
        corner_radius=0,
        default_text="",
        border_thickness=(0, 0, 0, 3),
        icon_path="../../assets/icons/more/email.svg",
        icon_color=(150, 150, 150, 1),
        text_type="email"

    )

    # Show the window
    window.show()

    # Run the application
    app.run()
