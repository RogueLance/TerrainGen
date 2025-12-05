# TerrainGen Usage Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python main.py
   ```

## Generating Terrain

### Step 1: Configure Size and Seed
- **Terrain Size**: Select from dropdown (512, 1024, 2048, or 4096)
  - Larger sizes provide more detail but take longer to process
  - 512 is recommended for quick iteration
  - 2048+ is suitable for final production heightmaps

- **Random Seed**: Enter a number (0-999999) or click "Random"
  - Same seed always produces the same terrain (reproducible)
  - Use this to save and restore specific terrain configurations

### Step 2: Choose Fractal Algorithm
Select one of four fractal types:

#### Diamond-Square
- Classic midpoint displacement algorithm
- Best for: Mountain ranges, dramatic elevation changes
- Characteristics: Can produce sharp features, highly controllable roughness
- Parameters:
  - **Roughness**: Higher = more dramatic elevation changes (0.0-1.0)

#### Perlin Noise
- Ken Perlin's classic gradient noise
- Best for: Rolling hills, natural-looking landscapes
- Characteristics: Smooth, organic transitions
- Parameters:
  - **Persistence**: Controls amplitude falloff per octave (0.0-1.0)
  - **Octaves**: Number of noise layers (1-12)
  - **Scale**: Size of terrain features (10-200)

#### Simplex Noise
- Improved version of Perlin noise
- Best for: Similar to Perlin but with less directional artifacts
- Characteristics: More isotropic (uniform in all directions)
- Parameters: Same as Perlin noise

#### Value Noise
- Simple interpolated random values
- Best for: Abstract or alien landscapes
- Characteristics: More blocky/geometric than Perlin/Simplex
- Parameters:
  - **Persistence**: Controls amplitude falloff (0.0-1.0)
  - **Octaves**: Number of noise layers (1-12)
  - **Scale**: Size of terrain features (10-200)

### Step 3: Adjust Parameters
Use the sliders to fine-tune your terrain:

- **Roughness/Persistence** (0.0-1.0):
  - Low (0.2-0.4): Smooth, gentle terrain
  - Medium (0.5-0.7): Balanced detail
  - High (0.8-1.0): Highly detailed, rough terrain

- **Octaves** (1-12):
  - Low (1-3): Large, simple features
  - Medium (4-6): Balanced detail levels
  - High (7-12): Maximum detail, can be noisy

- **Scale** (10-200):
  - Low (10-50): Small, frequent features
  - Medium (50-100): Balanced feature size
  - High (100-200): Large, sweeping features

### Step 4: Generate
Click "Generate Terrain" to create your heightmap.

## Erosion Simulation

### When to Use Erosion
Apply erosion to make terrain more realistic by simulating natural processes:
- Remove unrealistic sharp peaks
- Create valleys and drainage patterns
- Add weathering effects

### Basic Erosion
1. Set **Erosion Iterations** (0-200)
   - Low (10-30): Subtle weathering
   - Medium (50-100): Noticeable erosion
   - High (100-200): Heavy erosion, deep valleys

2. Click "Apply Erosion"

### Water-Guided Erosion
For more control over where erosion occurs:

1. Switch to **Water** paint mode
2. Paint blue "water" where you want more erosion
   - Brighter blue = more intense erosion
   - Darker blue = less intense erosion
3. Set erosion iterations
4. Click "Apply Erosion"

The water layer guides the hydraulic erosion simulation, creating more realistic drainage patterns.

## Painting and Editing

### Non-Destructive Workflow
The layer system allows you to:
- Keep original generated terrain intact (Base layer)
- Paint height modifications on a separate layer (Height layer)
- Paint water for erosion guidance (Water layer)
- Undo/redo any changes

### Brush Tools

#### Selecting Paint Layer
Choose which layer to paint on:
- **Height**: Modify terrain elevation non-destructively
- **Water**: Paint erosion guidance (blue overlay)

#### Brush Settings

**Brush Size** (5-100 pixels):
- Small (5-20): Detailed work, small features
- Medium (20-50): General terrain modification
- Large (50-100): Broad strokes, large changes

**Brush Hardness** (0.0-1.0):
- Soft (0.0-0.3): Smooth, gradual transitions
- Medium (0.4-0.7): Balanced edge
- Hard (0.8-1.0): Sharp, defined edges

**Brush Strength** (0.01-1.0):
- Low (0.01-0.2): Subtle changes, buildable
- Medium (0.2-0.5): Moderate changes
- High (0.5-1.0): Dramatic changes

#### Brush Modes

**Add Mode**:
- Raises terrain where you paint
- Use for: Creating hills, mountains, ridges

**Subtract Mode**:
- Lowers terrain where you paint
- Use for: Creating valleys, canyons, rivers

**Erase Mode**:
- Removes painted modifications
- Returns area to base terrain
- Only affects the current paint layer

### Painting Tips

1. **Build Up Gradually**: Use lower strength and paint multiple strokes
2. **Vary Brush Size**: Switch sizes for different levels of detail
3. **Use Soft Brushes**: For natural transitions
4. **Layer Workflow**:
   - Generate base terrain
   - Add major features with painting
   - Apply erosion for realism
   - Fine-tune with more painting

### Undo/Redo
- **Undo**: Reverts the last operation
- **Redo**: Restores an undone operation
- Stack holds up to 50 operations
- Each paint stroke, generation, or erosion is one operation

### Clearing Layers
- **Clear Height Layer**: Removes all height modifications, keeps base terrain
- **Clear Water Layer**: Removes all water paint

## Exporting

### Export Formats

#### PNG (Recommended)
- 8-bit grayscale
- Lossless compression
- Widely supported
- Good file size
- **Best for**: General use, game engines

#### JPG
- 8-bit grayscale
- Lossy compression
- Smallest file size
- Some quality loss
- **Best for**: Web preview, quick sharing

#### WEBP
- 8-bit grayscale
- Modern compression
- Better than JPG quality/size ratio
- **Best for**: Modern web applications

#### TIFF
- 16-bit grayscale
- Lossless
- Highest quality
- Largest file size
- **Best for**: Professional work, maximum precision

### Export Workflow

1. Ensure terrain looks correct in preview
2. Click appropriate export format button
3. Choose save location
4. Heightmap exports as grayscale image:
   - Black (0) = Lowest elevation
   - White (255 or 65535) = Highest elevation
   - Gray values = Intermediate elevations

### Using Exported Heightmaps

The exported images can be imported into:
- **Game Engines**: Unity, Unreal, Godot (as terrain heightmaps)
- **3D Software**: Blender, Maya, 3ds Max (as displacement maps)
- **GIS Software**: For topographic analysis
- **Custom Applications**: Any software that supports heightmap input

## Tips and Tricks

### Creating Realistic Terrain
1. Start with Perlin or Simplex noise (octaves: 6-8, persistence: 0.5-0.6)
2. Generate terrain
3. Apply moderate erosion (30-50 iterations)
4. Paint additional features (mountains, valleys)
5. Apply light erosion again (10-20 iterations)
6. Export as PNG or TIFF

### Creating Alien Landscapes
1. Use Value noise or Diamond-Square with high roughness
2. Extreme parameter values (high octaves, low/high persistence)
3. Skip erosion or use minimal erosion
4. Add dramatic painted features
5. Export

### Creating Islands
1. Generate terrain with any algorithm
2. Paint water layer in a circular or organic shape around edges
3. The water will "cut" valleys that can represent coastlines
4. Apply erosion with water layer active
5. Optionally, manually paint lower edges with subtract mode

### Performance Tips
- Use 512 size for iteration and testing
- Switch to larger sizes only for final export
- Perlin/Simplex with high octaves (10+) can be slow
- Erosion with 100+ iterations on large terrains takes time
- Diamond-Square is generally fastest for large sizes

### Reproducible Workflows
1. Note your seed value
2. Document your settings (fractal type, parameters)
3. You can always regenerate exact same base terrain
4. Painted modifications are manual and won't reproduce exactly
5. Save screenshots of settings for complex workflows

## Keyboard Shortcuts

Currently, the application uses mouse and buttons. Potential keyboard shortcuts:
- Click + Drag: Paint
- Ctrl+Z: Undo (use Undo button)
- Ctrl+Y: Redo (use Redo button)

## Troubleshooting

### Application won't start
- Check Python version (3.7+)
- Reinstall dependencies: `pip install -r requirements.txt`
- Try without PyOpenCL if installation fails

### Generation is slow
- Reduce terrain size
- Lower octaves parameter
- Use Diamond-Square instead of Perlin/Simplex
- Close other applications

### Erosion is very slow
- Reduce iterations
- Use smaller terrain size
- Thermal erosion is faster than hydraulic

### Exported image looks wrong
- Verify terrain looks correct before export
- Check you're using correct import settings in target software
- TIFF provides best quality, try that if others have issues

### Painting isn't working
- Check correct layer is selected (Height or Water)
- Increase brush strength if changes too subtle
- Ensure brush size isn't too small
- Try different brush mode

## Advanced Usage

### Combining Multiple Terrains
1. Generate and export first terrain
2. Generate different terrain with different seed
3. Use external image editor to blend/composite
4. Import result as texture in your 3D software

### Creating Matched Tilesets
1. Use noise-based algorithms (Perlin/Simplex)
2. Enable repeat flags in noise generation (code modification needed)
3. Export multiple terrains with adjacent seed values
4. Can tile seamlessly in some cases

### Batch Processing
- Application currently interactive only
- For batch work, consider scripting with the Python modules directly
- See `test_functionality.py` for examples of programmatic usage

## Getting Help

- Check this guide first
- Review `README.md` for installation issues
- Check `test_functionality.py` for code examples
- File issues on GitHub for bugs

## Workflow Examples

### Example 1: Mountain Range
```
1. Size: 1024
2. Seed: 42
3. Fractal: Perlin Noise
4. Persistence: 0.6
5. Octaves: 7
6. Scale: 100
7. Generate Terrain
8. Erosion: 40 iterations
9. Apply Erosion
10. Export as PNG
```

### Example 2: Rolling Hills
```
1. Size: 512
2. Seed: 1234
3. Fractal: Simplex Noise
4. Persistence: 0.4
5. Octaves: 5
6. Scale: 80
7. Generate Terrain
8. Erosion: 20 iterations
9. Apply Erosion
10. Paint Mode: Height, Add mode
11. Brush: Size 30, Hardness 0.3, Strength 0.15
12. Paint subtle hills
13. Export as PNG
```

### Example 3: Canyon System
```
1. Size: 1024
2. Seed: 7890
3. Fractal: Diamond-Square
4. Roughness: 0.5
5. Generate Terrain
6. Paint Mode: Water
7. Brush: Size 20, Strength 0.8
8. Paint meandering river paths in blue
9. Erosion: 80 iterations
10. Apply Erosion
11. Clear Water Layer
12. Export as TIFF
```
