import os
from pathlib import Path
from pillow_heif import register_heif_opener
from PIL import Image
from tqdm import tqdm
import argparse

# Register HEIF opener
register_heif_opener()

def convert_heic(input_path, output_format='jpg', output_dir=None):
    """Convert HEIC file to JPG or PNG format."""
    try:
        # Create output directory if it doesn't exist
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Get the input file path
        input_path = Path(input_path)
        
        # Determine output path
        if output_dir:
            output_path = Path(output_dir) / f"{input_path.stem}.{output_format}"
        else:
            output_path = input_path.with_suffix(f".{output_format}")
        
        # Open and convert the image
        with Image.open(input_path) as img:
            # Convert to RGB mode (removing alpha channel if present)
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert('RGB')
            
            # Save with appropriate quality for JPG
            if output_format.lower() == 'jpg':
                img.save(output_path, quality=95, optimize=True)
            else:
                img.save(output_path, optimize=True)
            
        return True
    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert HEIC images to JPG or PNG format.')
    parser.add_argument('input', help='Input directory containing HEIC files or single HEIC file')
    parser.add_argument('--format', choices=['jpg', 'png'], default='jpg', help='Output format (jpg or png)')
    parser.add_argument('--output', help='Output directory (optional)')
    
    args = parser.parse_args()
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Convert single file
        if input_path.suffix.lower() in ('.heic', '.heif'):
            success = convert_heic(input_path, args.format, args.output)
            print(f"Conversion {'successful' if success else 'failed'}")
    else:
        # Convert all HEIC files in directory
        heic_files = list(input_path.glob('*.heic')) + list(input_path.glob('*.HEIC'))
        heic_files.extend(list(input_path.glob('*.heif')) + list(input_path.glob('*.HEIF')))
        
        if not heic_files:
            print("No HEIC/HEIF files found in the specified directory.")
            return
        
        print(f"Found {len(heic_files)} HEIC/HEIF files")
        successful = 0
        
        for file in tqdm(heic_files, desc="Converting"):
            if convert_heic(file, args.format, args.output):
                successful += 1
        
        print(f"\nConversion completed: {successful}/{len(heic_files)} files converted successfully")

if __name__ == '__main__':
    main()
