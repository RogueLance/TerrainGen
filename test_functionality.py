"""
Test script to validate core terrain generation functionality.
"""
import numpy as np
from terrain_generator import TerrainGenerator
from erosion import ErosionSimulator
from layer_system import LayerSystem


def test_terrain_generation():
    """Test all terrain generation methods."""
    print("Testing terrain generation...")
    
    size = 256
    seed = 12345
    generator = TerrainGenerator(size, seed)
    
    # Test Diamond-Square
    print("  - Diamond-Square...", end=" ")
    terrain_ds = generator.diamond_square(roughness=0.5)
    assert terrain_ds.shape == (size, size), "Wrong shape"
    assert 0 <= terrain_ds.min() <= 1, "Values out of range"
    assert 0 <= terrain_ds.max() <= 1, "Values out of range"
    print("OK")
    
    # Test Perlin noise
    print("  - Perlin noise...", end=" ")
    terrain_perlin = generator.perlin_noise(octaves=6, persistence=0.5, scale=100)
    assert terrain_perlin.shape == (size, size), "Wrong shape"
    assert 0 <= terrain_perlin.min() <= 1, "Values out of range"
    assert 0 <= terrain_perlin.max() <= 1, "Values out of range"
    print("OK")
    
    # Test Simplex noise
    print("  - Simplex noise...", end=" ")
    terrain_simplex = generator.simplex_noise(octaves=6, persistence=0.5, scale=100)
    assert terrain_simplex.shape == (size, size), "Wrong shape"
    assert 0 <= terrain_simplex.min() <= 1, "Values out of range"
    assert 0 <= terrain_simplex.max() <= 1, "Values out of range"
    print("OK")
    
    # Test Value noise
    print("  - Value noise...", end=" ")
    terrain_value = generator.value_noise(octaves=6, persistence=0.5, scale=50)
    assert terrain_value.shape == (size, size), "Wrong shape"
    assert 0 <= terrain_value.min() <= 1, "Values out of range"
    assert 0 <= terrain_value.max() <= 1, "Values out of range"
    print("OK")
    
    return terrain_ds


def test_erosion(terrain):
    """Test erosion simulation."""
    print("\nTesting erosion simulation...")
    
    # Test hydraulic erosion
    print("  - Hydraulic erosion...", end=" ")
    simulator = ErosionSimulator(terrain)
    eroded_hydraulic = simulator.hydraulic_erosion(iterations=10)
    assert eroded_hydraulic.shape == terrain.shape, "Wrong shape"
    assert 0 <= eroded_hydraulic.min(), "Values out of range"
    assert eroded_hydraulic.max() <= 1, "Values out of range"
    print("OK")
    
    # Test thermal erosion
    print("  - Thermal erosion...", end=" ")
    simulator = ErosionSimulator(terrain)
    eroded_thermal = simulator.thermal_erosion(iterations=10)
    assert eroded_thermal.shape == terrain.shape, "Wrong shape"
    print("OK")
    
    # Test combined erosion
    print("  - Combined erosion...", end=" ")
    simulator = ErosionSimulator(terrain)
    eroded_combined = simulator.combined_erosion(
        hydraulic_iterations=5,
        thermal_iterations=5
    )
    assert eroded_combined.shape == terrain.shape, "Wrong shape"
    print("OK")


def test_layer_system():
    """Test layer system."""
    print("\nTesting layer system...")
    
    size = 256
    layer_system = LayerSystem(size)
    
    # Test base terrain
    print("  - Set base terrain...", end=" ")
    terrain = np.random.random((size, size))
    layer_system.set_base_terrain(terrain)
    assert np.allclose(layer_system.base_layer.data, terrain), "Base terrain not set correctly"
    print("OK")
    
    # Test painting
    print("  - Paint height...", end=" ")
    layer_system.paint(128, 128, 0.5, 20, 0.5, mode='add')
    assert layer_system.height_layer.data[128, 128] > 0, "Paint didn't work"
    print("OK")
    
    # Test water painting
    print("  - Paint water...", end=" ")
    layer_system.paint_water(64, 64, 0.8, 15, 0.7)
    assert layer_system.water_layer.data[64, 64] > 0, "Water paint didn't work"
    print("OK")
    
    # Test composite
    print("  - Get composite...", end=" ")
    composite = layer_system.get_composite()
    assert composite.shape == (size, size), "Wrong composite shape"
    print("OK")
    
    # Test undo/redo
    print("  - Undo/Redo...", end=" ")
    initial_state = layer_system.height_layer.data.copy()
    layer_system.paint(100, 100, 0.3, 10, 0.5, mode='add')
    after_paint = layer_system.height_layer.data.copy()
    layer_system.undo()
    after_undo = layer_system.height_layer.data.copy()
    
    assert not np.allclose(initial_state, after_paint), "Paint should change data"
    assert np.allclose(initial_state, after_undo), "Undo should restore state"
    
    layer_system.redo()
    after_redo = layer_system.height_layer.data.copy()
    assert np.allclose(after_paint, after_redo), "Redo should restore painted state"
    print("OK")


def test_seed_reproducibility():
    """Test that same seed produces same terrain."""
    print("\nTesting seed reproducibility...")
    
    size = 128
    seed = 42
    
    gen1 = TerrainGenerator(size, seed)
    terrain1 = gen1.diamond_square(roughness=0.5)
    
    gen2 = TerrainGenerator(size, seed)
    terrain2 = gen2.diamond_square(roughness=0.5)
    
    assert np.allclose(terrain1, terrain2), "Same seed should produce same terrain"
    print("  - Reproducibility verified: OK")


def main():
    """Run all tests."""
    print("=" * 60)
    print("TerrainGen Functionality Tests")
    print("=" * 60)
    
    try:
        terrain = test_terrain_generation()
        test_erosion(terrain)
        test_layer_system()
        test_seed_reproducibility()
        
        print("\n" + "=" * 60)
        print("All tests passed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
