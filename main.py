"""
Main application for Terrain Generator.
"""
import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QSlider, QSpinBox, QGroupBox,
    QRadioButton, QButtonGroup, QFileDialog, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QColor
from PIL import Image

from terrain_generator import TerrainGenerator
from erosion import ErosionSimulator
from layer_system import LayerSystem


class TerrainCanvas(QWidget):
    """Canvas widget for displaying and editing terrain."""
    
    def __init__(self, size=512):
        super().__init__()
        self.size = size
        self.layer_system = LayerSystem(size)
        self.setFixedSize(size, size)
        
        # Brush settings
        self.brush_size = 20
        self.brush_hardness = 0.5
        self.brush_value = 0.1
        self.brush_mode = 'add'  # 'add', 'subtract', 'erase'
        self.paint_mode = 'height'  # 'height' or 'water'
        
        # Mouse state
        self.last_pos = None
        self.is_painting = False
        
        # Enable mouse tracking
        self.setMouseTracking(True)
    
    def set_terrain(self, terrain):
        """Set the base terrain."""
        self.layer_system.set_base_terrain(terrain)
        self.update()
    
    def get_composite_terrain(self):
        """Get the composite terrain."""
        return self.layer_system.get_composite()
    
    def get_water_layer(self):
        """Get the water layer."""
        return self.layer_system.get_water_layer()
    
    def paintEvent(self, event):
        """Paint the canvas."""
        painter = QPainter(self)
        
        # Get composite terrain
        terrain = self.layer_system.get_composite()
        
        # Convert to QImage
        terrain_uint8 = (terrain * 255).astype(np.uint8)
        
        # Create grayscale image
        height, width = terrain_uint8.shape
        bytes_per_line = width
        qimage = QImage(terrain_uint8.data, width, height, bytes_per_line, 
                       QImage.Format_Grayscale8)
        
        # Draw terrain
        painter.drawImage(0, 0, qimage)
        
        # Overlay water layer if visible
        water = self.layer_system.water_layer
        if water.visible and water.data.max() > 0:
            water_data = (water.data * 255).astype(np.uint8)
            # Create blue overlay
            water_rgba = np.zeros((height, width, 4), dtype=np.uint8)
            water_rgba[:, :, 2] = water_data  # Blue channel
            water_rgba[:, :, 3] = (water_data * 0.5).astype(np.uint8)  # Alpha
            
            water_qimage = QImage(water_rgba.data, width, height, width * 4,
                                 QImage.Format_RGBA8888)
            painter.drawImage(0, 0, water_qimage)
    
    def mousePressEvent(self, event):
        """Handle mouse press."""
        if event.button() == Qt.LeftButton:
            self.is_painting = True
            self.last_pos = event.pos()
            self._paint_at(event.pos())
    
    def mouseMoveEvent(self, event):
        """Handle mouse move."""
        if self.is_painting and event.buttons() & Qt.LeftButton:
            self._paint_at(event.pos())
            self.last_pos = event.pos()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release."""
        if event.button() == Qt.LeftButton:
            self.is_painting = False
            self.last_pos = None
    
    def _paint_at(self, pos):
        """Paint at the given position."""
        x, y = pos.x(), pos.y()
        
        # Clamp to canvas bounds
        x = max(0, min(self.size - 1, x))
        y = max(0, min(self.size - 1, y))
        
        if self.paint_mode == 'water':
            # Paint water
            self.layer_system.paint_water(x, y, self.brush_value, 
                                         self.brush_size, self.brush_hardness)
        else:
            # Paint height
            mode = 'subtract' if self.brush_mode == 'erase' else self.brush_mode
            self.layer_system.paint(x, y, self.brush_value, self.brush_size,
                                   self.brush_hardness, mode)
        
        self.update()
    
    def undo(self):
        """Undo last operation."""
        self.layer_system.undo()
        self.update()
    
    def redo(self):
        """Redo last operation."""
        self.layer_system.redo()
        self.update()
    
    def clear_height_layer(self):
        """Clear height layer."""
        self.layer_system.clear_height_layer()
        self.update()
    
    def clear_water_layer(self):
        """Clear water layer."""
        self.layer_system.clear_water_layer()
        self.update()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Terrain Generator")
        
        # Default settings
        self.current_size = 512
        self.current_seed = 12345
        
        # Initialize UI
        self.init_ui()
        
        # Generate initial terrain
        self.generate_terrain()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout()
        main_widget.setLayout(layout)
        
        # Left panel - Canvas
        self.canvas = TerrainCanvas(self.current_size)
        layout.addWidget(self.canvas)
        
        # Right panel - Controls (scrollable)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(350)
        scroll_area.setMaximumWidth(400)
        
        controls_widget = QWidget()
        controls_layout = QVBoxLayout()
        controls_widget.setLayout(controls_layout)
        scroll_area.setWidget(controls_widget)
        layout.addWidget(scroll_area)
        
        # Size selection
        size_group = QGroupBox("Terrain Size")
        size_layout = QVBoxLayout()
        size_group.setLayout(size_layout)
        
        self.size_combo = QComboBox()
        self.size_combo.addItems(["512", "1024", "2048", "4096"])
        self.size_combo.setCurrentText(str(self.current_size))
        size_layout.addWidget(self.size_combo)
        
        controls_layout.addWidget(size_group)
        
        # Seed input
        seed_group = QGroupBox("Random Seed")
        seed_layout = QHBoxLayout()
        seed_group.setLayout(seed_layout)
        
        self.seed_spin = QSpinBox()
        self.seed_spin.setRange(0, 999999)
        self.seed_spin.setValue(self.current_seed)
        seed_layout.addWidget(self.seed_spin)
        
        random_seed_btn = QPushButton("Random")
        random_seed_btn.clicked.connect(self.randomize_seed)
        seed_layout.addWidget(random_seed_btn)
        
        controls_layout.addWidget(seed_group)
        
        # Fractal type selection
        fractal_group = QGroupBox("Fractal Type")
        fractal_layout = QVBoxLayout()
        fractal_group.setLayout(fractal_layout)
        
        self.fractal_buttons = QButtonGroup()
        fractals = [
            ("Diamond-Square", "diamond_square"),
            ("Perlin Noise", "perlin"),
            ("Simplex Noise", "simplex"),
            ("Value Noise", "value")
        ]
        
        for name, value in fractals:
            radio = QRadioButton(name)
            radio.setProperty("fractal_type", value)
            self.fractal_buttons.addButton(radio)
            fractal_layout.addWidget(radio)
        
        self.fractal_buttons.buttons()[0].setChecked(True)
        
        controls_layout.addWidget(fractal_group)
        
        # Fractal parameters
        params_group = QGroupBox("Fractal Parameters")
        params_layout = QVBoxLayout()
        params_group.setLayout(params_layout)
        
        # Roughness/Persistence
        params_layout.addWidget(QLabel("Roughness/Persistence:"))
        self.roughness_slider = QSlider(Qt.Horizontal)
        self.roughness_slider.setRange(0, 100)
        self.roughness_slider.setValue(50)
        self.roughness_label = QLabel("0.50")
        self.roughness_slider.valueChanged.connect(
            lambda v: self.roughness_label.setText(f"{v/100:.2f}"))
        params_layout.addWidget(self.roughness_slider)
        params_layout.addWidget(self.roughness_label)
        
        # Octaves
        params_layout.addWidget(QLabel("Octaves:"))
        self.octaves_slider = QSlider(Qt.Horizontal)
        self.octaves_slider.setRange(1, 12)
        self.octaves_slider.setValue(6)
        self.octaves_label = QLabel("6")
        self.octaves_slider.valueChanged.connect(
            lambda v: self.octaves_label.setText(str(v)))
        params_layout.addWidget(self.octaves_slider)
        params_layout.addWidget(self.octaves_label)
        
        # Scale
        params_layout.addWidget(QLabel("Scale:"))
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(10, 200)
        self.scale_slider.setValue(100)
        self.scale_label = QLabel("100")
        self.scale_slider.valueChanged.connect(
            lambda v: self.scale_label.setText(str(v)))
        params_layout.addWidget(self.scale_slider)
        params_layout.addWidget(self.scale_label)
        
        controls_layout.addWidget(params_group)
        
        # Generate button
        generate_btn = QPushButton("Generate Terrain")
        generate_btn.clicked.connect(self.generate_terrain)
        controls_layout.addWidget(generate_btn)
        
        # Erosion controls
        erosion_group = QGroupBox("Erosion")
        erosion_layout = QVBoxLayout()
        erosion_group.setLayout(erosion_layout)
        
        erosion_layout.addWidget(QLabel("Erosion Iterations:"))
        self.erosion_slider = QSlider(Qt.Horizontal)
        self.erosion_slider.setRange(0, 200)
        self.erosion_slider.setValue(50)
        self.erosion_label = QLabel("50")
        self.erosion_slider.valueChanged.connect(
            lambda v: self.erosion_label.setText(str(v)))
        erosion_layout.addWidget(self.erosion_slider)
        erosion_layout.addWidget(self.erosion_label)
        
        apply_erosion_btn = QPushButton("Apply Erosion")
        apply_erosion_btn.clicked.connect(self.apply_erosion)
        erosion_layout.addWidget(apply_erosion_btn)
        
        controls_layout.addWidget(erosion_group)
        
        # Brush controls
        brush_group = QGroupBox("Brush Settings")
        brush_layout = QVBoxLayout()
        brush_group.setLayout(brush_layout)
        
        # Brush size
        brush_layout.addWidget(QLabel("Brush Size:"))
        self.brush_size_slider = QSlider(Qt.Horizontal)
        self.brush_size_slider.setRange(5, 100)
        self.brush_size_slider.setValue(20)
        self.brush_size_label = QLabel("20")
        self.brush_size_slider.valueChanged.connect(self.update_brush_size)
        brush_layout.addWidget(self.brush_size_slider)
        brush_layout.addWidget(self.brush_size_label)
        
        # Brush hardness
        brush_layout.addWidget(QLabel("Brush Hardness:"))
        self.brush_hardness_slider = QSlider(Qt.Horizontal)
        self.brush_hardness_slider.setRange(0, 100)
        self.brush_hardness_slider.setValue(50)
        self.brush_hardness_label = QLabel("0.50")
        self.brush_hardness_slider.valueChanged.connect(self.update_brush_hardness)
        brush_layout.addWidget(self.brush_hardness_slider)
        brush_layout.addWidget(self.brush_hardness_label)
        
        # Brush strength
        brush_layout.addWidget(QLabel("Brush Strength:"))
        self.brush_strength_slider = QSlider(Qt.Horizontal)
        self.brush_strength_slider.setRange(1, 100)
        self.brush_strength_slider.setValue(10)
        self.brush_strength_label = QLabel("0.10")
        self.brush_strength_slider.valueChanged.connect(self.update_brush_strength)
        brush_layout.addWidget(self.brush_strength_slider)
        brush_layout.addWidget(self.brush_strength_label)
        
        # Brush mode
        brush_layout.addWidget(QLabel("Brush Mode:"))
        self.brush_mode_buttons = QButtonGroup()
        modes = [("Add", "add"), ("Subtract", "subtract"), ("Erase", "erase")]
        for name, value in modes:
            radio = QRadioButton(name)
            radio.setProperty("brush_mode", value)
            self.brush_mode_buttons.addButton(radio)
            brush_layout.addWidget(radio)
        self.brush_mode_buttons.buttons()[0].setChecked(True)
        self.brush_mode_buttons.buttonClicked.connect(self.update_brush_mode)
        
        # Paint mode
        brush_layout.addWidget(QLabel("Paint Layer:"))
        self.paint_mode_buttons = QButtonGroup()
        paint_modes = [("Height", "height"), ("Water", "water")]
        for name, value in paint_modes:
            radio = QRadioButton(name)
            radio.setProperty("paint_mode", value)
            self.paint_mode_buttons.addButton(radio)
            brush_layout.addWidget(radio)
        self.paint_mode_buttons.buttons()[0].setChecked(True)
        self.paint_mode_buttons.buttonClicked.connect(self.update_paint_mode)
        
        controls_layout.addWidget(brush_group)
        
        # Layer controls
        layer_group = QGroupBox("Layer Controls")
        layer_layout = QVBoxLayout()
        layer_group.setLayout(layer_layout)
        
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.canvas.undo)
        layer_layout.addWidget(undo_btn)
        
        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.canvas.redo)
        layer_layout.addWidget(redo_btn)
        
        clear_height_btn = QPushButton("Clear Height Layer")
        clear_height_btn.clicked.connect(self.canvas.clear_height_layer)
        layer_layout.addWidget(clear_height_btn)
        
        clear_water_btn = QPushButton("Clear Water Layer")
        clear_water_btn.clicked.connect(self.canvas.clear_water_layer)
        layer_layout.addWidget(clear_water_btn)
        
        controls_layout.addWidget(layer_group)
        
        # Export controls
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout()
        export_group.setLayout(export_layout)
        
        export_formats = [
            ("Export as PNG", "png"),
            ("Export as JPG", "jpg"),
            ("Export as WEBP", "webp"),
            ("Export as TIFF", "tiff")
        ]
        
        for name, fmt in export_formats:
            btn = QPushButton(name)
            btn.setProperty("format", fmt)
            btn.clicked.connect(lambda checked, f=fmt: self.export_terrain(f))
            export_layout.addWidget(btn)
        
        controls_layout.addWidget(export_group)
        
        # Add stretch to push controls to top
        controls_layout.addStretch()
        
        # Set window size
        self.resize(self.current_size + 400, self.current_size + 50)
    
    def randomize_seed(self):
        """Randomize the seed value."""
        self.seed_spin.setValue(np.random.randint(0, 999999))
    
    def update_brush_size(self, value):
        """Update brush size."""
        self.brush_size_label.setText(str(value))
        self.canvas.brush_size = value
    
    def update_brush_hardness(self, value):
        """Update brush hardness."""
        hardness = value / 100.0
        self.brush_hardness_label.setText(f"{hardness:.2f}")
        self.canvas.brush_hardness = hardness
    
    def update_brush_strength(self, value):
        """Update brush strength."""
        strength = value / 100.0
        self.brush_strength_label.setText(f"{strength:.2f}")
        self.canvas.brush_value = strength
    
    def update_brush_mode(self, button):
        """Update brush mode."""
        self.canvas.brush_mode = button.property("brush_mode")
    
    def update_paint_mode(self, button):
        """Update paint mode."""
        self.canvas.paint_mode = button.property("paint_mode")
    
    def generate_terrain(self):
        """Generate new terrain."""
        # Get settings
        size = int(self.size_combo.currentText())
        seed = self.seed_spin.value()
        
        # Get fractal type
        fractal_type = None
        for button in self.fractal_buttons.buttons():
            if button.isChecked():
                fractal_type = button.property("fractal_type")
                break
        
        # Get parameters
        roughness = self.roughness_slider.value() / 100.0
        octaves = self.octaves_slider.value()
        scale = self.scale_slider.value()
        
        # Update canvas size if needed
        if size != self.current_size:
            self.current_size = size
            self.canvas.setParent(None)
            self.canvas = TerrainCanvas(size)
            # Re-add to layout
            main_layout = self.centralWidget().layout()
            main_layout.insertWidget(0, self.canvas)
            self.resize(size + 400, size + 50)
        
        # Generate terrain
        generator = TerrainGenerator(size, seed)
        
        if fractal_type == "diamond_square":
            terrain = generator.diamond_square(roughness=roughness)
        elif fractal_type == "perlin":
            terrain = generator.perlin_noise(octaves=octaves, 
                                            persistence=roughness,
                                            scale=scale)
        elif fractal_type == "simplex":
            terrain = generator.simplex_noise(octaves=octaves,
                                             persistence=roughness,
                                             scale=scale)
        elif fractal_type == "value":
            terrain = generator.value_noise(octaves=octaves,
                                           persistence=roughness,
                                           scale=scale)
        else:
            terrain = generator.diamond_square(roughness=roughness)
        
        self.canvas.set_terrain(terrain)
    
    def apply_erosion(self):
        """Apply erosion to the terrain."""
        iterations = self.erosion_slider.value()
        
        # Get current terrain
        terrain = self.canvas.get_composite_terrain()
        water_map = self.canvas.get_water_layer()
        
        # Apply erosion
        simulator = ErosionSimulator(terrain)
        eroded = simulator.combined_erosion(
            hydraulic_iterations=iterations,
            thermal_iterations=iterations // 2,
            water_map=water_map
        )
        
        # Update terrain
        self.canvas.set_terrain(eroded)
    
    def export_terrain(self, format_type):
        """Export terrain to file."""
        # Get save path
        filters = {
            'png': "PNG Image (*.png)",
            'jpg': "JPEG Image (*.jpg *.jpeg)",
            'webp': "WebP Image (*.webp)",
            'tiff': "TIFF Image (*.tiff *.tif)"
        }
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Terrain",
            f"terrain.{format_type}",
            filters.get(format_type, "Image (*.*)")
        )
        
        if filename:
            # Get composite terrain
            terrain = self.canvas.get_composite_terrain()
            
            # Convert to 8-bit or 16-bit
            if format_type in ['tiff']:
                # 16-bit for TIFF
                terrain_data = (terrain * 65535).astype(np.uint16)
            else:
                # 8-bit for other formats
                terrain_data = (terrain * 255).astype(np.uint8)
            
            # Save using PIL
            image = Image.fromarray(terrain_data)
            
            try:
                image.save(filename, format=format_type.upper())
                QMessageBox.information(self, "Export Successful",
                                      f"Terrain exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed",
                                   f"Failed to export terrain: {str(e)}")


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
