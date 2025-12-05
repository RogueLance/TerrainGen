# TerrainGen

A Python-based terrain heightmap generator with GPU-accelerated erosion simulation and non-destructive layer-based editing.

## Features

- **Multiple Fractal Algorithms**:
  - Diamond-Square
  - Perlin Noise
  - Simplex Noise
  - Value Noise

- **Configurable Terrain Sizes**: 512x512, 1024x1024, 2048x2048, 4096x4096

- **Seed-Based Generation**: Reproducible terrain generation with custom seeds

- **Erosion Simulation**:
  - Hydraulic erosion
  - Thermal erosion
  - Water layer-guided erosion intensity

- **Non-Destructive Layer System**:
  - Base terrain layer
  - Height painting layer
  - Water layer for erosion guidance

- **Advanced Brush Tools**:
  - Adjustable brush size
  - Brush hardness control
  - Add/Subtract/Erase modes
  - Undo/Redo stack

- **Multiple Export Formats**: PNG, JPG, WEBP, TIFF

## Installation

1. Clone the repository:
```bash
git clone https://github.com/RogueLance/TerrainGen.git
cd TerrainGen
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Note: PyOpenCL is optional and only needed for GPU-accelerated erosion features.

## Usage

Run the application:
```bash
python main.py
```

### Generating Terrain

1. Select terrain size from the dropdown (512, 1024, 2048, or 4096)
2. Choose or randomize a seed value
3. Select a fractal type (Diamond-Square, Perlin, Simplex, or Value Noise)
4. Adjust fractal parameters using the sliders:
   - **Roughness/Persistence**: Controls terrain detail (0.0-1.0)
   - **Octaves**: Number of noise layers (1-12)
   - **Scale**: Size of terrain features (10-200)
5. Click "Generate Terrain"

### Applying Erosion

1. Set erosion iterations (0-200)
2. Optionally paint water layer to guide erosion intensity
3. Click "Apply Erosion"

### Painting on Terrain

1. Select paint layer (Height or Water)
2. Configure brush settings:
   - **Size**: Brush diameter in pixels (5-100)
   - **Hardness**: Brush edge falloff (0.0-1.0)
   - **Strength**: Paint intensity (0.01-1.0)
   - **Mode**: Add, Subtract, or Erase
3. Click and drag on the canvas to paint

### Layer Controls

- **Undo**: Revert last operation
- **Redo**: Restore undone operation
- **Clear Height Layer**: Remove all height paint
- **Clear Water Layer**: Remove all water paint

### Exporting

1. Click desired export format button (PNG, JPG, WEBP, or TIFF)
2. Choose save location
3. Heightmap will be exported as a grayscale image

## Technical Details

- Terrain data is stored as normalized floating-point values (0.0-1.0)
- Non-destructive editing through layer compositing
- Water layer uses blue channel intensity to guide erosion
- TIFF exports use 16-bit precision for maximum quality
- Undo stack supports up to 50 operations

## Requirements

- Python 3.7+
- PyQt5
- NumPy
- Pillow (PIL)
- noise
- scipy
- numba (optional, for performance)
- pyopencl (optional, for GPU acceleration)

## License

MIT License