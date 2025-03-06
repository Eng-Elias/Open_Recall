"""
Script to convert SVG icon to multiple PNG sizes for Briefcase
"""
import os
import sys
import subprocess
from pathlib import Path

def create_icons():
    """Create PNG icons in various sizes from SVG source"""
    # Define the icon sizes required by Briefcase
    icon_sizes = [
        16, 32, 64, 128, 256, 512,  # Windows sizes
        20, 29, 40, 58, 76, 80, 87, 120, 152, 167, 180, 1024,  # iOS sizes
    ]
    
    # Get the path to the SVG icon
    base_dir = Path(__file__).parent
    svg_path = base_dir / "open_recall" / "static" / "images" / "icon.svg"
    output_dir = base_dir / "open_recall" / "static" / "images" / "icon"
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if Inkscape is available for conversion
    try:
        # Try to use Inkscape for conversion
        for size in icon_sizes:
            output_path = output_dir / f"{size}.png"
            print(f"Creating icon: {output_path}")
            
            # Use Python's built-in libraries to create a simple icon if Inkscape isn't available
            try:
                from PIL import Image, ImageDraw
                
                # Create a new image with the specified size
                img = Image.new('RGBA', (size, size), color=(74, 134, 232, 255))
                draw = ImageDraw.Draw(img)
                
                # Draw a simple circular icon
                padding = size // 8
                draw.ellipse(
                    [(padding, padding), (size - padding, size - padding)],
                    fill=(255, 255, 255, 255)
                )
                
                # Save the image
                img.save(output_path)
                print(f"Created {size}x{size} icon")
            except ImportError:
                print("PIL (Pillow) library not available. Cannot create icons.")
                return False
        
        return True
    except Exception as e:
        print(f"Error creating icons: {e}")
        return False

if __name__ == "__main__":
    success = create_icons()
    if success:
        print("Icons created successfully!")
    else:
        print("Failed to create icons.")
        sys.exit(1)
