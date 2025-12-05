"""
Layer system for non-destructive terrain editing.
"""
import numpy as np


class Layer:
    """Represents a single layer in the layer system."""
    
    def __init__(self, size, name="Layer", layer_type="height"):
        """Initialize a layer.
        
        Args:
            size: Size of the layer (square)
            name: Name of the layer
            layer_type: Type of layer ('height', 'water', 'base')
        """
        self.size = size
        self.name = name
        self.layer_type = layer_type
        self.data = np.zeros((size, size), dtype=np.float32)
        self.visible = True
        self.opacity = 1.0
    
    def clear(self):
        """Clear the layer data."""
        self.data = np.zeros((self.size, self.size), dtype=np.float32)
    
    def copy(self):
        """Create a copy of this layer."""
        new_layer = Layer(self.size, self.name, self.layer_type)
        new_layer.data = self.data.copy()
        new_layer.visible = self.visible
        new_layer.opacity = self.opacity
        return new_layer


class LayerSystem:
    """Manages multiple layers for non-destructive editing."""
    
    def __init__(self, size):
        """Initialize layer system.
        
        Args:
            size: Size of the layers (square)
        """
        self.size = size
        self.layers = []
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo = 50
        
        # Create base layer
        self.base_layer = Layer(size, "Base Terrain", "base")
        self.layers.append(self.base_layer)
        
        # Create height painting layer
        self.height_layer = Layer(size, "Height Paint", "height")
        self.layers.append(self.height_layer)
        
        # Create water layer
        self.water_layer = Layer(size, "Water", "water")
        self.layers.append(self.water_layer)
    
    def set_base_terrain(self, terrain):
        """Set the base terrain layer.
        
        Args:
            terrain: 2D numpy array of height values
        """
        self.save_state()
        self.base_layer.data = terrain.copy()
    
    def get_composite(self):
        """Get the composite of all visible layers.
        
        Returns:
            Composite terrain as numpy array
        """
        composite = np.zeros((self.size, self.size), dtype=np.float32)
        
        for layer in self.layers:
            if layer.visible and layer.layer_type in ['base', 'height']:
                composite += layer.data * layer.opacity
        
        # Normalize to [0, 1]
        composite = np.clip(composite, 0, 1)
        return composite
    
    def get_water_layer(self):
        """Get the water layer data.
        
        Returns:
            Water layer as numpy array
        """
        return self.water_layer.data if self.water_layer.visible else None
    
    def paint(self, x, y, value, brush_size, hardness, mode='add'):
        """Paint on the height layer.
        
        Args:
            x, y: Center coordinates to paint
            value: Value to paint (0-1)
            brush_size: Size of the brush in pixels
            hardness: Hardness of the brush (0-1)
            mode: Paint mode ('add', 'subtract', 'set')
        """
        self.save_state()
        
        # Ensure brush size is odd for symmetric brush
        if brush_size % 2 == 0:
            brush_size += 1
        
        # Create brush mask
        brush_mask = self._create_brush_mask(brush_size, hardness)
        
        # Calculate bounds
        half_size = brush_size // 2
        x_start = max(0, x - half_size)
        x_end = min(self.size, x + half_size + 1)
        y_start = max(0, y - half_size)
        y_end = min(self.size, y + half_size + 1)
        
        # Calculate the corresponding region in the brush mask
        brush_x_start = half_size - (x - x_start)
        brush_x_end = brush_x_start + (x_end - x_start)
        brush_y_start = half_size - (y - y_start)
        brush_y_end = brush_y_start + (y_end - y_start)
        
        brush_region = brush_mask[brush_y_start:brush_y_end, brush_x_start:brush_x_end]
        
        # Apply paint
        if mode == 'add':
            self.height_layer.data[y_start:y_end, x_start:x_end] += value * brush_region
        elif mode == 'subtract':
            self.height_layer.data[y_start:y_end, x_start:x_end] -= value * brush_region
        elif mode == 'set':
            current = self.height_layer.data[y_start:y_end, x_start:x_end]
            self.height_layer.data[y_start:y_end, x_start:x_end] = (
                current * (1 - brush_region) + value * brush_region
            )
        
        # Clamp values
        self.height_layer.data = np.clip(self.height_layer.data, -1, 1)
    
    def paint_water(self, x, y, value, brush_size, hardness):
        """Paint on the water layer.
        
        Args:
            x, y: Center coordinates to paint
            value: Value to paint (0-1)
            brush_size: Size of the brush in pixels
            hardness: Hardness of the brush (0-1)
        """
        self.save_state()
        
        # Ensure brush size is odd for symmetric brush
        if brush_size % 2 == 0:
            brush_size += 1
        
        # Create brush mask
        brush_mask = self._create_brush_mask(brush_size, hardness)
        
        # Calculate bounds
        half_size = brush_size // 2
        x_start = max(0, x - half_size)
        x_end = min(self.size, x + half_size + 1)
        y_start = max(0, y - half_size)
        y_end = min(self.size, y + half_size + 1)
        
        # Calculate the corresponding region in the brush mask
        brush_x_start = half_size - (x - x_start)
        brush_x_end = brush_x_start + (x_end - x_start)
        brush_y_start = half_size - (y - y_start)
        brush_y_end = brush_y_start + (y_end - y_start)
        
        brush_region = brush_mask[brush_y_start:brush_y_end, brush_x_start:brush_x_end]
        
        # Apply paint (set mode for water)
        current = self.water_layer.data[y_start:y_end, x_start:x_end]
        self.water_layer.data[y_start:y_end, x_start:x_end] = (
            current * (1 - brush_region) + value * brush_region
        )
        
        # Clamp values
        self.water_layer.data = np.clip(self.water_layer.data, 0, 1)
    
    def _create_brush_mask(self, size, hardness):
        """Create a circular brush mask.
        
        Args:
            size: Size of the brush
            hardness: Hardness (0=soft, 1=hard)
            
        Returns:
            2D numpy array with brush mask
        """
        center = size // 2
        y, x = np.ogrid[:size, :size]
        distance = np.sqrt((x - center)**2 + (y - center)**2)
        radius = size / 2
        
        # Apply hardness
        if hardness < 1.0:
            # Soft brush with falloff
            falloff = 1.0 - hardness
            mask = np.clip(1 - (distance / radius) ** (1 / (falloff + 0.1)), 0, 1)
        else:
            # Hard brush
            mask = (distance <= radius).astype(np.float32)
        
        return mask
    
    def save_state(self):
        """Save current state to undo stack."""
        # Save copies of all layers
        state = {
            'base': self.base_layer.data.copy(),
            'height': self.height_layer.data.copy(),
            'water': self.water_layer.data.copy()
        }
        self.undo_stack.append(state)
        
        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo:
            self.undo_stack.pop(0)
        
        # Clear redo stack
        self.redo_stack.clear()
    
    def undo(self):
        """Undo the last operation."""
        if len(self.undo_stack) > 0:
            # Save current state to redo stack
            state = {
                'base': self.base_layer.data.copy(),
                'height': self.height_layer.data.copy(),
                'water': self.water_layer.data.copy()
            }
            self.redo_stack.append(state)
            
            # Restore previous state
            prev_state = self.undo_stack.pop()
            self.base_layer.data = prev_state['base']
            self.height_layer.data = prev_state['height']
            self.water_layer.data = prev_state['water']
    
    def redo(self):
        """Redo the last undone operation."""
        if len(self.redo_stack) > 0:
            # Save current state to undo stack
            state = {
                'base': self.base_layer.data.copy(),
                'height': self.height_layer.data.copy(),
                'water': self.water_layer.data.copy()
            }
            self.undo_stack.append(state)
            
            # Restore next state
            next_state = self.redo_stack.pop()
            self.base_layer.data = next_state['base']
            self.height_layer.data = next_state['height']
            self.water_layer.data = next_state['water']
    
    def clear_height_layer(self):
        """Clear the height painting layer."""
        self.save_state()
        self.height_layer.clear()
    
    def clear_water_layer(self):
        """Clear the water layer."""
        self.save_state()
        self.water_layer.clear()
