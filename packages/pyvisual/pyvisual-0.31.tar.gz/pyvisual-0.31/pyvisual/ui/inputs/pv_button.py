from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont, QPainter
from PySide6.QtWidgets import QPushButton, QLabel, QHBoxLayout, QSizePolicy
from PySide6.QtSvgWidgets import QSvgWidget
from pyvisual.utils.helper_functions import add_shadow_effect, update_svg_color, draw_border
from PySide6.QtGui import QFontDatabase, QFont


class PvButton(QPushButton):
    def __init__(self, container, x=100, y=100, width=200, height=50, text="Submit",
                 font="Arial", font_size=16, font_color=(255, 255, 255, 1), font_color_hover=None,
                 bold=False, italic=False, underline=False, strikeout=False,
                 button_color=(56, 182, 255, 1), hover_color=None,
                 clicked_color=None, disabled_color=(200, 200, 200, 1),
                 border_color=(200, 200, 200, 1), border_color_hover=None,
                 border_thickness=0, corner_radius=0,
                 box_shadow=None, box_shadow_hover=None,
                 icon_path=None, icon_position="left", icon_spacing=10, icon_scale=1.0, icon_color=(255, 255, 255, 1),
                 icon_color_hover=None,is_visible=True, is_disabled=False, opacity=1, paddings=(0, 0, 0, 0),
                 on_hover=None, on_click=None, on_release=None, tag=None,
                 **kwargs):
        super().__init__(container)

        # Initialize attributes
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._text = text
        self._font = font
        self._font_size = int(font_size)
        self._font_color = font_color
        self._font_color_hover = font_color_hover
        self._bold = bold
        self._italic = italic
        self._underline = underline
        self._strikeout = strikeout
        self._button_color = button_color
        self._disabled_color = disabled_color
        self._border_color = border_color
        self._border_color_hover = border_color_hover or border_color
        self._border_thickness = border_thickness
        self._corner_radius = corner_radius
        self._box_shadow = None
        self._box_shadow_hover = None
        # self._box_shadow = box_shadow
        # self._box_shadow_hover = box_shadow_hover or box_shadow
        self._opacity = opacity
        self._is_visible = is_visible
        self._is_disabled = is_disabled
        self._paddings = paddings
        self._tag = tag
        self._icon_path = icon_path
        self._icon_position = icon_position
        self._icon_spacing = icon_spacing
        self._icon_scale = icon_scale
        self._icon_color = icon_color
        self._icon_color_hover = icon_color_hover

        self._hover_color = (
            hover_color if hover_color is not None else
            tuple(
                max(c - 15, 0) if button_color[:3] != (0, 0, 0) else min(c + 15, 255)
                for c in button_color[:3]
            ) + (button_color[3],)
        )
        self._clicked_color = (
            clicked_color if clicked_color is not None else
            tuple(
                max(c - 30, 0) if button_color[:3] != (0, 0, 0) else min(c + 30, 255)
                for c in button_color[:3]
            ) + (button_color[3],)
        )

        self.max_corner_radius = self._height // 2 - 1
        if self._corner_radius > self.max_corner_radius:
            self._corner_radius = self.max_corner_radius
        # Position and size
        self.setGeometry(self._x, self._y, self._width, self._height)
        self.setFixedSize(self._width, self._height)
        # Set up layout
        self.create_layout()

        # Style configuration
        self.update_style()

        # Visibility and interaction
        self.setVisible(self._is_visible)
        self.setEnabled(not self._is_disabled)

        # Opacity
        self.setWindowOpacity(self._opacity)

        # Callbacks
        self._on_hover = on_hover
        self._on_click = on_click
        self._on_release = on_release

        print(self._font_size)

    def enterEvent(self, event):

        """Handles hover (mouse enter) events."""
        super().enterEvent(event)

        # Apply hover shadow
        if self._box_shadow_hover:
            add_shadow_effect(self, self._box_shadow_hover)

        if self._font_color_hover:
            hover_font_color = f"rgba({self._font_color_hover[0]}, {self._font_color_hover[1]}, {self._font_color_hover[2]}, {self._font_color_hover[3]})"
            if hasattr(self, '_text_label'):
                self._text_label.setStyleSheet(f"color: {hover_font_color}; background: transparent;")
        if self._icon_color_hover:
            if hasattr(self, '_icon_label') and isinstance(self._icon_label, QSvgWidget):
                    update_svg_color(self._icon_label,self._icon_color_hover)
        if self._on_hover:
            self._on_hover()

    #
    def leaveEvent(self, event):
        """Handles hover (mouse leave) events."""
        super().leaveEvent(event)
        if self._box_shadow_hover:
            add_shadow_effect(self, self._box_shadow)

        default_font_color = f"rgba({self._font_color[0]}, {self._font_color[1]}, {self._font_color[2]}, {self._font_color[3]})"
        if hasattr(self, '_text_label'):
            self._text_label.setStyleSheet(f"color: {default_font_color}; background: transparent;")
        if hasattr(self, '_icon_label') and isinstance(self._icon_label, QSvgWidget):
            update_svg_color(self._icon_label, self._icon_color)

    #

    def update_style(self):
        r, g, b, a = self._button_color
        br, bg, bb, ba = self._border_color
        border_style = f"{self._border_thickness}px solid rgba({br}, {bg}, {bb}, {ba})" if self._border_thickness else "none"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba({r}, {g}, {b}, {a});
                border-radius: {self._corner_radius}px;
                border: {border_style};
            }}
            QPushButton:hover {{
                background-color: rgba({self._hover_color[0]}, {self._hover_color[1]}, {self._hover_color[2]}, {self._hover_color[3]});
            }}
            QPushButton:pressed {{
                background-color: rgba({self._clicked_color[0]}, {self._clicked_color[1]}, {self._clicked_color[2]}, {self._clicked_color[3]});
            }}
        """)
        # Apply shadow effect if needed
        if self._box_shadow:
            add_shadow_effect(self, self._box_shadow)

    # def paintEvent(self, event):
    #     super().paintEvent(event)
    #     painter = QPainter(self)
    #     draw_border(self, painter, self._border_color, self._border_thickness, self._corner_radius)

    def create_layout(self):
        """Creates the layout to include the icon and text."""
        layout = QHBoxLayout()  # Create a standalone layout
        layout.setContentsMargins(0, 0, 0, 0)  # No extra space
        layout.setSpacing(0)  # Force 0 spacing

        # self._paddings is defined as (top, right, bottom, left)
        # top, right, bottom, left = self._paddings
        # # Rearrange to match Qt's order: left, top, right, bottom
        layout.setContentsMargins(*self._paddings)
        layout.setSpacing(self._icon_spacing)  # Explicit control
        layout.setAlignment(Qt.AlignCenter)  # Center-align the content

        # Load custom font if a file path is provided
        if self._font.endswith('.ttf') or self._font.endswith('.otf'):
            self._qfont = self.load_custom_font(self._font)
            if self._qfont is None:
                print(f"Failed to load custom font: {self._font}")
                self._qfont = QFont("Arial")  # Fallback to default
        else:
            self._qfont = QFont(self._font)  # Standard system font

        # self._qfont.setPointSize(font_size)
        # self.setFont(self._qfont)

        # Set font
        font = self._qfont
        font.setPixelSize(self._font_size)
        # font.setPointSizeF(self._font_size)
        font.setBold(self._bold)
        font.setItalic(self._italic)
        font.setUnderline(self._underline)
        font.setStrikeOut(self._strikeout)

        # Add icon if available
        if self._icon_path:

            if self._icon_path.endswith('.svg'):
                try:
                    # Handle SVG icons
                    with open(self._icon_path, "r") as file:
                        svg_content = file.read()
                        self._icon_label = QSvgWidget(self)
                        self._icon_label._original_svg = svg_content  # Store the original SVG content
                        self._icon_label.load(svg_content.encode("utf-8"))
                        icon_size = int(24 * self._icon_scale)  # Scale the icon size dynamically
                        self._icon_label.setFixedSize(icon_size, icon_size)
                        self._icon_label.setStyleSheet("background: transparent;")
                        update_svg_color(self._icon_label, self._icon_color)

                except FileNotFoundError:
                    print(f"SVG file '{self._icon_path}' not found.")

            else:
                # Handle raster icons
                self._icon_label = QLabel(self)
                pixmap = QPixmap(self._icon_path)
                icon_size = int(24 * self._icon_scale)  # Scale the icon size dynamically
                self._icon_label.setPixmap(
                    pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self._icon_label.setFixedSize(icon_size, icon_size)
                self._icon_label.setStyleSheet("background: transparent;")  # Ensure icon label is transparent

            if self._icon_position == "left":
                layout.addWidget(self._icon_label)

        # Add text
        if self._text:
            self._text_label = QLabel(self._text, self)  # Assign to self._text_label
            self._text_label.setFont(font)  # Apply font settings
            self._text_label.setStyleSheet(
                f"color: rgba({self._font_color[0]}, {self._font_color[1]}, {self._font_color[2]}, {self._font_color[3]}); background: transparent;")

            layout.addWidget(self._text_label)

        # Add icon to the right if specified
        if self._icon_path and self._icon_position == "right":
            layout.addWidget(self._icon_label)

        # Apply the layout to the button
        self.setLayout(layout)

        # Set button background to transparent
        self.setStyleSheet("background: transparent;")
        #
        # self._text_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # self._icon_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def mousePressEvent(self, event):
        """Handles mouse press events."""
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton and self._on_click:
            self._on_click(self)
            self._on_click(self)

    def mouseReleaseEvent(self, event):
        """Handles mouse release events."""
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton and self._on_release:
            self._on_release()

    def load_custom_font(self, font_path):
        """Loads a custom font and returns the corresponding QFont object."""
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                return QFont(font_families[0])  # Return the first available font family
        return None  # Return None if the font fails to load

    # ............................................................................................
    # .........................Getters and Setters for all properties ............................
    # ............................................................................................
    def get_text(self):
        return self._text

    def set_text(self, value):
        """Sets the text of the button while retaining font and style settings."""
        self._text = value
        self._text_label.setText(value)

    def get_position(self):
        return self._x, self._y

    def set_position(self, x, y):
        self._x = x
        self._y = y
        self.setGeometry(self._x, self._y, self._width, self._height)

    def get_size(self):
        return self._width, self._height

    def set_size(self, pos):
        self._width = pos[0]
        self._height = pos[1]
        self.setGeometry(self._x, self._y, self._width, self._height)
        self.setFixedSize(pos[0], pos[1])

    def get_font(self):
        return self._font

    def set_font(self, font):
        self._font = font
        self.qfont.setFamily(font)
        self.setFont(self.qfont)

    def get_font_size(self):
        return self._font_size

    def set_font_size(self, size):
        self._font_size = size
        self.qfont.setPointSize(size)
        self.setFont(self.qfont)

    def get_font_color(self):
        return self._font_color

    def set_font_color(self, color):
        self._font_color = color
        self.update_style()

    def get_button_color(self):
        return self._button_color

    def set_button_color(self, color):
        self._button_color = color
        self.update_style()

    def get_hover_color(self):
        return self._hover_color

    def set_hover_color(self, color):
        self._hover_color = color
        self.update_style()

    def get_clicked_color(self):
        return self._clicked_color

    def set_clicked_color(self, color):
        self._clicked_color = color
        self.update_style()

    def get_disabled_color(self):
        return self._disabled_color

    def set_disabled_color(self, color):
        self._disabled_color = color
        self.update_style()

    def get_border_color(self):
        return self._border_color

    def set_border_color(self, color):
        self._border_color = color
        self.update_style()

    def get_border_thickness(self):
        return self._border_thickness

    def set_border_thickness(self, thickness):
        self._border_thickness = thickness
        self.update_style()

    def get_corner_radius(self):
        return self._corner_radius

    def set_corner_radius(self, radius):
        self._corner_radius = radius
        self.update_style()

    def get_opacity(self):
        return self._opacity

    def set_opacity(self, value):
        self._opacity = value
        self.setWindowOpacity(self._opacity)

    def get_is_visible(self):
        return self._is_visible

    def set_is_visible(self, visible):
        self._is_visible = visible
        self.setVisible(self._is_visible)

    def get_is_disabled(self):
        return self._is_disabled

    def set_is_disabled(self, disabled):
        """Sets the button's enabled/disabled state and updates its color."""
        self._is_disabled = disabled
        self.setEnabled(not self._is_disabled)
        self.update_style()

    def get_box_shadow(self):
        return self._box_shadow

    def set_box_shadow(self, shadow):
        self._box_shadow = shadow
        add_shadow_effect(self, self._box_shadow)

    def get_on_click(self):
        return self._on_click

    def set_on_click(self, callback):
        self._on_click = callback

    def get_on_hover(self):
        return self._on_hover

    def set_on_hover(self, callback):
        """Sets or updates the hover callback."""
        self._on_hover = callback

    def get_on_release(self):
        """Returns the current release callback."""
        return self._on_release

    def set_on_release(self, callback):
        """Sets or updates the release callback."""
        self._on_release = callback

    def get_tag(self):
        return self._tag

    def set_tag(self, tag):
        self._tag = tag

    def print_properties(self):
        """Prints all the current properties of the button."""
        print(f"""
        Button Properties:
        ------------------
        text: {self.get_text()}
        pos: {self.get_position()}
        size : {self.get_size()}
        font: {self.get_font()}
        font_size: {self.get_font_size()}
        font_color: {self.get_font_color()}
        button_color: {self.get_button_color()}
        hover_color: {self.get_hover_color()}
        clicked_color: {self.get_clicked_color()}
        disabled_color: {self.get_disabled_color()}
        border_color: {self.get_border_color()}
        border_thickness: {self.get_border_thickness()}
        corner_radius: {self.get_corner_radius()}
        opacity: {self.get_opacity()}
        is_visible: {self.get_is_visible()}
        is_disabled: {self.get_is_disabled()}
        box_shadow: {self.get_box_shadow()}
        on_click: {self.get_on_click()}
        on_hover: {self.get_on_hover()}
        on_release: {self.get_on_release()}
        tag: {self.get_tag()}
        
        """)


# Example Usage
if __name__ == "__main__":
    import pyvisual as pv

    app = pv.PvApp()

    # Create a window
    window = pv.PvWindow(title="PvApp Example", is_resizable=True)

    # Create a PvButton
    button1 = PvButton(window, x=50, y=50)
    button2 = PvButton(window, x=300, y=50, width=50, height=50, corner_radius=25, text="GO", font_size=10)

    button3 = PvButton(window, x=50, y=150, border_color=(56, 182, 255, 1), border_thickness=2,
                       button_color=(255, 255, 255, 1), font_color=(56, 182, 255, 1), hover_color=(56, 182, 255, 1),
                       clicked_color=(225, 225, 225, 1), font_color_hover=(255, 255, 255, 1))
    button4 = PvButton(window, x=300, y=150, width=50, height=50, corner_radius=25, text="GO", font_size=10,
                       border_color=(56, 182, 255, 1), border_thickness=2,
                       button_color=(255, 255, 255, 1), font_color=(56, 182, 255, 1), hover_color=(56, 182, 255, 1),
                       clicked_color=(225, 225, 225, 1), font_color_hover=(255, 255, 255, 1))

    button5 = PvButton(window, x=400, y=50, width=50, height=50, corner_radius=10, text="GO", font_size=10)

    button6 = PvButton(window, x=400, y=150, width=50, height=50, corner_radius=10, text="GO", font_size=10,
                       border_color=(56, 182, 255, 1), border_thickness=2,
                       button_color=(255, 255, 255, 1), font_color=(56, 182, 255, 1), hover_color=(56, 182, 255, 1),
                       clicked_color=(225, 225, 225, 1), font_color_hover=(255, 255, 255, 1))

    button7 = PvButton(window, x=500, y=50, corner_radius=25)
    button8 = PvButton(window, x=500, y=150, corner_radius=25, text="Submit", font_size=16,
                       border_color=(56, 182, 255, 1),
                       border_thickness=2,
                       button_color=(255, 255, 255, 1), font_color=(56, 182, 255, 1), hover_color=(56, 182, 255, 1),
                       clicked_color=(225, 225, 225, 1), font_color_hover=(255, 255, 255, 1))

    button9 = PvButton(window, x=50, y=250, width=100, height=40, text="Like",
                       icon_path="../../assets/icons/like/like.svg", button_color=(255, 255, 255, 1),
                       hover_color=(255, 255, 255, 1), font_color_hover=(56, 182, 255, 1),
                       clicked_color=(245, 245, 245, 1), bold=True, border_thickness=1, corner_radius=10,
                       font_color=(136, 136, 136, 1), font_size=14, icon_scale=1, icon_spacing=10,
                       icon_position="right", border_color_hover=(56, 182, 255, 1),
                       box_shadow_hover="2px 2px 5px 0px rgba(56,182,255,0.5)")  # Red border on hover)

    button10 = PvButton(window, x=200, y=250, width=50, height=50, text="",
                        icon_path="../../assets/icons/more/shopping.svg", button_color=(161, 80, 157, 1),
                        hover_color=(255, 255, 255, 1), font_color_hover=(161, 80, 157, 1),
                        clicked_color=(161, 80, 157, 1), bold=True, border_thickness=1,
                        font_color=(255, 255, 255, 1), font_size=14, icon_scale=1, icon_spacing=10,
                        icon_position="right")

    button11 = PvButton(window, x=300, y=250, width=150, height=50, text="Next",
                        icon_path="../../assets/icons/more/arrow_right.svg", button_color=(255, 255, 255, 1),
                        font_color_hover=(255, 255, 255, 1),
                        hover_color=(161, 80, 157, 1), corner_radius=0,
                        clicked_color=(255, 255, 255, 1), bold=True, border_thickness=1, border_color=(161, 80, 157, 1),
                        font_color=(161, 80, 157, 1), font_size=14, icon_scale=1, icon_spacing=30,
                        icon_position="right")

    button12 = PvButton(window, x=500, y=250, width=135, height=50, text="Play",
                        icon_path="../../assets/icons/more/play.svg", icon_scale=1.7, icon_position="left",
                        icon_spacing=15, paddings=(0, 0, 23, 0),
                        button_color=(255, 255, 255, 1), hover_color=(161, 80, 157, 1),
                        font_color_hover=(255, 255, 255, 1), clicked_color=(255, 255, 255, 1),
                        corner_radius=25,
                        bold=True, border_thickness=2, border_color=(161, 80, 157, 1),
                        font_color=(161, 80, 157, 1), font_size=14,
                        )

    button13 = PvButton(window, x=300, y=325, width=150, height=50, text="Next",
                        icon_path="../../assets/icons/more/arrow_right.svg", button_color=(255, 255, 255, 1),
                        corner_radius=0,
                        bold=True, border_thickness=(0, 0, 2, 0), border_color=(161, 80, 157, 1),
                        font_color=(161, 80, 157, 1), font_size=14, icon_scale=1, icon_spacing=30,
                        icon_position="right")

    button14 = PvButton(window, x=50, y=400, button_color=(200, 0, 200, 1))

    button14.set_position(100, 450)

    # Show the window
    window.show()

    # Run the application
    app.run()
