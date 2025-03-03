# TimePicker Control for PySide6

A modern, customizable time picker widget for PySide6 applications, inspired by iOS-style time pickers. Developed and maintained by [Next Wave Tech Solutions](https://github.com/nextwavetchsolutions).

## Features

- Modern, smooth scrolling time picker
- Customizable themes (Light/Dark/Custom)
- Adjustable size and appearance
- Configurable scrolling physics and animations
- Auto-saving settings
- Easy integration with existing PySide6 applications
- Professional support available

## Installation

```bash
pip install timepicker-control
```

## Quick Start

```python
from PySide6.QtWidgets import QApplication
from timepicker_control import TimePicker

app = QApplication([])
time_picker = TimePicker()
time_picker.show()

# Get the selected time
selected_time = time_picker.get_time()  # Returns a datetime.time object
```

## Advanced Usage

### Basic Integration

```python
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from timepicker_control import TimePicker

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create and add the time picker
        self.time_picker = TimePicker()
        layout.addWidget(self.time_picker)
        
        # Connect to time change events
        self.time_picker.timeChanged.connect(self.on_time_changed)
    
    def on_time_changed(self, time):
        print(f"Selected time: {time.strftime('%I:%M %p')}")
```

### Customization

```python
# Set custom colors
time_picker.set_custom_colors(
    text_color="#000000",
    background_color="#FFFFFF",
    highlight_color="#E3F2FD"
)

# Set size
time_picker.set_size(width=320, height=500)

# Configure wheel appearance
time_picker.set_wheel_size(
    item_height=50,
    visible_items=7
)

# Adjust scrolling behavior
time_picker.set_scroll_settings(
    speed=18.0,
    smoothness=0.90
)

# Set animation duration
time_picker.set_animation_duration(950)
```

## Settings Persistence

The TimePicker automatically saves user preferences and restores them between sessions. To reset to defaults:

```python
time_picker.reset_to_defaults()
```

## Requirements

- Python 3.6+
- PySide6 6.0.0+

## Support

For bug reports and feature requests, please use our [GitHub Issues](https://github.com/nextwavetchsolutions/timepicker-control/issues) page.

For professional support and custom development, please contact us at:
- Email: nextwavetchsolutions@gmail.com
- GitHub: [@nextwavetchsolutions](https://github.com/nextwavetchsolutions)

## Contributing

We welcome contributions! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## About Next Wave Tech Solutions

Next Wave Tech Solutions specializes in developing high-quality Python packages and custom software solutions. Visit our [GitHub profile](https://github.com/nextwavetchsolutions) to see our other projects. 