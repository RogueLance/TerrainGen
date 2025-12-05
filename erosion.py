"""
Erosion simulation algorithms for terrain.
"""
import numpy as np
from scipy.ndimage import convolve


class ErosionSimulator:
    """Simulate erosion effects on terrain."""
    
    def __init__(self, terrain):
        """Initialize erosion simulator.
        
        Args:
            terrain: 2D numpy array of height values
        """
        self.terrain = terrain.copy()
        self.size = terrain.shape[0]
    
    def hydraulic_erosion(self, iterations=100, rain_amount=0.01, 
                         evaporation=0.5, capacity=0.01, deposition=0.1,
                         erosion=0.3, water_map=None):
        """Simulate hydraulic erosion.
        
        Args:
            iterations: Number of simulation iterations
            rain_amount: Amount of water added per iteration
            evaporation: Rate of water evaporation (0-1)
            capacity: Sediment carrying capacity
            deposition: Rate of sediment deposition
            erosion: Rate of terrain erosion
            water_map: Optional water layer to guide erosion intensity
            
        Returns:
            Eroded terrain as numpy array
        """
        terrain = self.terrain.copy()
        water = np.zeros_like(terrain)
        sediment = np.zeros_like(terrain)
        
        # Kernel for calculating flow direction
        kernel = np.array([
            [0.707, 1, 0.707],
            [1, 0, 1],
            [0.707, 1, 0.707]
        ])
        
        for iteration in range(iterations):
            # Add rain
            if water_map is not None:
                # Use water map to guide where rain falls (blue = more erosion)
                rain = rain_amount * (1 + water_map * 2)
                water += rain
            else:
                water += rain_amount
            
            # Calculate total height (terrain + water)
            total_height = terrain + water
            
            # Find flow direction (water flows to lower neighbors)
            for y in range(1, self.size - 1):
                for x in range(1, self.size - 1):
                    if water[y, x] <= 0:
                        continue
                    
                    current_height = total_height[y, x]
                    
                    # Check all neighbors
                    neighbors = []
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dy == 0 and dx == 0:
                                continue
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.size and 0 <= nx < self.size:
                                height_diff = current_height - total_height[ny, nx]
                                if height_diff > 0:
                                    neighbors.append((height_diff, ny, nx))
                    
                    if neighbors:
                        # Sort by height difference
                        neighbors.sort(reverse=True)
                        
                        # Flow to lower neighbors
                        total_diff = sum(n[0] for n in neighbors[:4])  # Top 4 neighbors
                        if total_diff > 0:
                            for height_diff, ny, nx in neighbors[:4]:
                                flow = water[y, x] * (height_diff / total_diff) * 0.5
                                
                                # Erode terrain
                                erode_amount = erosion * flow
                                terrain[y, x] -= erode_amount
                                sediment[y, x] += erode_amount
                                
                                # Transport water and sediment
                                water[ny, nx] += flow
                                water[y, x] -= flow
                                
                                if sediment[y, x] > capacity:
                                    # Deposit sediment
                                    deposit = (sediment[y, x] - capacity) * deposition
                                    terrain[ny, nx] += deposit
                                    sediment[y, x] -= deposit
            
            # Evaporation
            water *= (1 - evaporation)
            
            # Deposit remaining sediment
            terrain += sediment * deposition
            sediment *= (1 - deposition)
        
        # Normalize
        terrain = np.clip(terrain, 0, 1)
        return terrain
    
    def thermal_erosion(self, iterations=100, threshold=0.05, rate=0.5):
        """Simulate thermal erosion (talus angle).
        
        Args:
            iterations: Number of simulation iterations
            threshold: Height difference threshold for erosion
            rate: Rate of material transfer
            
        Returns:
            Eroded terrain as numpy array
        """
        terrain = self.terrain.copy()
        
        # Kernel for neighbors (4-connected)
        offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for _ in range(iterations):
            new_terrain = terrain.copy()
            
            for y in range(1, self.size - 1):
                for x in range(1, self.size - 1):
                    current = terrain[y, x]
                    max_diff = 0
                    
                    # Find maximum height difference
                    diffs = []
                    for dy, dx in offsets:
                        ny, nx = y + dy, x + dx
                        diff = current - terrain[ny, nx]
                        if diff > threshold:
                            diffs.append((diff, ny, nx))
                            max_diff = max(max_diff, diff)
                    
                    if diffs:
                        # Distribute material
                        total_diff = sum(d[0] for d in diffs)
                        for diff, ny, nx in diffs:
                            amount = rate * (diff / total_diff) * (max_diff - threshold)
                            new_terrain[y, x] -= amount
                            new_terrain[ny, nx] += amount
            
            terrain = new_terrain
        
        return terrain
    
    def combined_erosion(self, hydraulic_iterations=50, thermal_iterations=50,
                        water_map=None):
        """Apply both hydraulic and thermal erosion.
        
        Args:
            hydraulic_iterations: Number of hydraulic erosion iterations
            thermal_iterations: Number of thermal erosion iterations
            water_map: Optional water layer for hydraulic erosion
            
        Returns:
            Eroded terrain as numpy array
        """
        # Apply hydraulic erosion first
        self.terrain = self.hydraulic_erosion(
            iterations=hydraulic_iterations,
            water_map=water_map
        )
        
        # Then thermal erosion
        terrain = self.thermal_erosion(iterations=thermal_iterations)
        
        return terrain
