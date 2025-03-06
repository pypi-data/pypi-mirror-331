# Tsapp Wrapper

An extension for Pygame adding useful features, developed by Zephyros1938.

## Overview

This project provides additional functionality to Python and Pygame, enhancing the capabilities of the TechSmart Graphics Library (tsapp). It includes various graphical objects, utilities, and configurations to create and manage graphical applications more efficiently.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/tsapp_wrapper.git
    ```
2. Navigate to the project directory:
    ```sh
    cd tsapp_wrapper
    ```
3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Example

Here's a basic example of how to create a window and add a polygonal object:

```python
import zephyros1938.tsapp as tsapp
import zephyros1938.tsappMod as tsappMod

# Create a window
window = tsappMod.Surface(width=800, height=600, background_color=tsapp.WHITE, title="Example Window")

# Create a polygonal object
config = tsappMod.PolygonalObjectConfig(points=[[0, 0], [100, 0], [50, 100]], center=[400, 300], color=tsapp.RED)
polygon = tsappMod.PolygonalObject(config=config)

# Add the polygon to the window
window.add_object(polygon)

# Main loop
while window.is_running:
    window.finish_frame()
```

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contact

For any inquiries, please contact Zephyros1938 at [zephyros@zephyros1938.org](mailto:zephyros@zephyros1938.org).
