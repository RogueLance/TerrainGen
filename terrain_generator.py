"""
Terrain generation algorithms including various fractal methods.
"""
import numpy as np
from noise import pnoise2, snoise2
from scipy.ndimage import gaussian_filter


class TerrainGenerator:
    """Generate terrain using various fractal algorithms."""
    
    def __init__(self, size=512, seed=None):
        """Initialize terrain generator.
        
        Args:
            size: Size of the terrain map (will be square)
            seed: Random seed for reproducible generation
        """
        self.size = size
        self.seed = seed if seed is not None else np.random.randint(0, 10000)
        np.random.seed(self.seed)
    
    def diamond_square(self, roughness=0.5, smoothing=0):
        """Generate terrain using Diamond-Square algorithm.
        
        Args:
            roughness: Controls terrain roughness (0.0-1.0)
            smoothing: Amount of Gaussian smoothing to apply (0 = none)
            
        Returns:
            numpy array of height values normalized to [0, 1]
        """
        # Ensure size is power of 2 + 1
        power = int(np.log2(self.size - 1))
        size = 2**power + 1
        
        terrain = np.zeros((size, size))
        
        # Initialize corners
        terrain[0, 0] = np.random.random()
        terrain[0, size-1] = np.random.random()
        terrain[size-1, 0] = np.random.random()
        terrain[size-1, size-1] = np.random.random()
        
        step_size = size - 1
        scale = roughness
        
        while step_size > 1:
            half_step = step_size // 2
            
            # Diamond step
            for y in range(0, size - 1, step_size):
                for x in range(0, size - 1, step_size):
                    avg = (terrain[y, x] + 
                          terrain[y, x + step_size] +
                          terrain[y + step_size, x] +
                          terrain[y + step_size, x + step_size]) / 4.0
                    
                    terrain[y + half_step, x + half_step] = avg + (np.random.random() - 0.5) * scale
            
            # Square step
            for y in range(0, size, half_step):
                for x in range((y + half_step) % step_size, size, step_size):
                    count = 0
                    total = 0.0
                    
                    if y >= half_step:
                        total += terrain[y - half_step, x]
                        count += 1
                    if y + half_step < size:
                        total += terrain[y + half_step, x]
                        count += 1
                    if x >= half_step:
                        total += terrain[y, x - half_step]
                        count += 1
                    if x + half_step < size:
                        total += terrain[y, x + half_step]
                        count += 1
                    
                    if count > 0:
                        terrain[y, x] = total / count + (np.random.random() - 0.5) * scale
            
            step_size = half_step
            scale *= roughness
        
        # Normalize to [0, 1]
        terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
        
        # Resize if needed
        if size != self.size:
            from scipy.ndimage import zoom
            zoom_factor = self.size / size
            terrain = zoom(terrain, zoom_factor, order=1)
        
        # Apply smoothing if requested
        if smoothing > 0:
            terrain = gaussian_filter(terrain, sigma=smoothing)
            terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
        
        return terrain
    
    def perlin_noise(self, octaves=6, persistence=0.5, lacunarity=2.0, scale=100.0):
        """Generate terrain using Perlin noise.
        
        Args:
            octaves: Number of noise octaves
            persistence: Amplitude multiplier per octave
            lacunarity: Frequency multiplier per octave
            scale: Scale of the noise
            
        Returns:
            numpy array of height values normalized to [0, 1]
        
        Note:
            For large terrain sizes, this may be slow. Consider using smaller
            sizes or optimizing with vectorized operations for production use.
        """
        terrain = np.zeros((self.size, self.size))
        
        for y in range(self.size):
            for x in range(self.size):
                terrain[y, x] = pnoise2(
                    x / scale,
                    y / scale,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                    repeatx=self.size,
                    repeaty=self.size,
                    base=self.seed
                )
        
        # Normalize to [0, 1]
        terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
        return terrain
    
    def simplex_noise(self, octaves=6, persistence=0.5, lacunarity=2.0, scale=100.0):
        """Generate terrain using Simplex noise.
        
        Args:
            octaves: Number of noise octaves
            persistence: Amplitude multiplier per octave
            lacunarity: Frequency multiplier per octave
            scale: Scale of the noise
            
        Returns:
            numpy array of height values normalized to [0, 1]
        
        Note:
            For large terrain sizes, this may be slow. Consider using smaller
            sizes or optimizing with vectorized operations for production use.
        """
        terrain = np.zeros((self.size, self.size))
        
        for y in range(self.size):
            for x in range(self.size):
                terrain[y, x] = snoise2(
                    x / scale,
                    y / scale,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                    repeatx=self.size,
                    repeaty=self.size,
                    base=self.seed
                )
        
        # Normalize to [0, 1]
        terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
        return terrain
    
    def value_noise(self, octaves=6, persistence=0.5, scale=50.0):
        """Generate terrain using Value noise.
        
        Args:
            octaves: Number of noise octaves
            persistence: Amplitude multiplier per octave
            scale: Scale of the noise
            
        Returns:
            numpy array of height values normalized to [0, 1]
        """
        np.random.seed(self.seed)
        
        def interpolate(a, b, t):
            # Smooth interpolation
            t = t * t * (3 - 2 * t)
            return a * (1 - t) + b * t
        
        terrain = np.zeros((self.size, self.size))
        
        for octave in range(octaves):
            frequency = 2 ** octave / scale
            amplitude = persistence ** octave
            
            # Generate random grid
            grid_size = int(self.size * frequency) + 2
            grid = np.random.random((grid_size, grid_size))
            
            for y in range(self.size):
                for x in range(self.size):
                    # Sample position in grid
                    gx = x * frequency
                    gy = y * frequency
                    
                    # Grid cell
                    x0 = int(gx)
                    y0 = int(gy)
                    x1 = x0 + 1
                    y1 = y0 + 1
                    
                    # Interpolation weights
                    sx = gx - x0
                    sy = gy - y0
                    
                    # Interpolate
                    n0 = interpolate(grid[y0, x0], grid[y0, x1], sx)
                    n1 = interpolate(grid[y1, x0], grid[y1, x1], sx)
                    value = interpolate(n0, n1, sy)
                    
                    terrain[y, x] += value * amplitude
        
        # Normalize to [0, 1]
        terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
        return terrain
