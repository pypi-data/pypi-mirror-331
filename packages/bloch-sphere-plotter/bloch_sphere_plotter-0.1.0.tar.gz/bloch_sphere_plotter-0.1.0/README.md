# Bloch Sphere Plotter

A Python package for visualizing quantum states on the Bloch sphere with high-quality, customizable plots.

![Bloch Sphere Example](tests/reference_images/bloch_sphere_reference.png)

## Overview

The Bloch sphere is a geometrical representation of the pure state space of a two-level quantum mechanical system (qubit). This package provides tools to easily visualize quantum states on the Bloch sphere using matplotlib.

## Features

- Clean, publication-quality Bloch sphere visualizations
- Simple API for plotting quantum states
- Customizable appearance with proper 3D rendering
- Includes coordinate axes, meridian circles, and equator
- Clear state vector representation with directional arrows

## Installation

### From PyPI

```bash
pip install bloch-sphere-plotter
```

### From Source

```bash
git clone https://github.com/yourusername/bloch-sphere-plotter.git
cd bloch-sphere-plotter
pip install -e .
```

## Usage

### Basic Example

```python
import numpy as np
from bloch_sphere_plotter.plot import plot_bloch_sphere

# Plot a state using spherical coordinates (theta, phi)
plot_bloch_sphere((np.pi/3, np.pi/4))
```

### Parameters

- `state`: A tuple `(theta, phi)` representing the qubit state in spherical coordinates
  - `theta`: Polar angle (0 to π)
  - `phi`: Azimuthal angle (0 to 2π)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/bloch-sphere-plotter.git
cd bloch-sphere-plotter

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=bloch_sphere_plotter

# Run only tests suitable for CI environments (no GUI)
pytest -m ci
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The matplotlib team for their excellent 3D plotting capabilities
- The quantum computing community for inspiration
