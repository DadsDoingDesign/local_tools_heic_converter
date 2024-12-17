#!/usr/bin/env python3
"""
Local Tools: HEIC Converter - CLI Application
A command-line interface for converting HEIC/HEIF images to JPG or PNG format.

This module provides a simple command-line interface for batch conversion
of HEIC/HEIF images while maintaining high quality.

Author: Denis Dukhvalov
Created with: Windsurf Editor
License: MIT
"""

import os
import sys
import argparse
from PIL import Image
from pillow_heif import register_heif_opener
from typing import List, Optional, Tuple

# Register HEIF opener
register_heif_opener()

def convert_file(file_path: str, output_format: str, output_dir: Optional[str] = None) -> Tuple[bool, str]:
    """
    Convert a single HEIC file to JPG or PNG format.
    
    Args:
        file_path: Path to the input HEIC file
        output_format: Output format ('jpg' or 'png')
        output_dir: Optional output directory. If None, uses the input file's directory
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Validate input file
        if not os.path.exists(file_path):
            return False, f"Input file does not exist: {file_path}"
        
        # Determine output directory
        if output_dir is None:
            output_dir = os.path.dirname(file_path)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create output path
        output_path = os.path.join(
            output_dir,
            f"{os.path.splitext(os.path.basename(file_path))[0]}.{output_format.lower()}"
        )
        
        # Convert image
        with Image.open(file_path) as img:
            # Convert to RGB mode if necessary
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                img = img.convert('RGB')
            
            # Save with appropriate quality
            if output_format.lower() == 'jpg':
                img.save(output_path, quality=95, optimize=True)
            else:
                img.save(output_path, optimize=True)
        
        return True, f"Successfully converted: {output_path}"
    
    except Exception as e:
        return False, f"Error converting {file_path}: {str(e)}"

def find_heic_files(directory: str) -> List[str]:
    """
    Recursively find all HEIC files in a directory.
    
    Args:
        directory: Directory to search in
    
    Returns:
        List of HEIC file paths
    """
    heic_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.heic'):
                heic_files.append(os.path.join(root, file))
    return heic_files

def main():
    parser = argparse.ArgumentParser(
        description="Convert HEIC/HEIF images to JPG or PNG format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Convert a single file:
    %(prog)s input.heic
  
  Convert multiple files:
    %(prog)s file1.heic file2.heic
  
  Convert all HEIC files in a directory:
    %(prog)s /path/to/directory
  
  Convert to PNG format:
    %(prog)s --format png input.heic
  
  Specify output directory:
    %(prog)s --output /path/to/output input.heic
"""
    )
    
    parser.add_argument(
        'inputs',
        nargs='+',
        help='Input HEIC file(s) or directory containing HEIC files'
    )
    
    parser.add_argument(
        '--format',
        choices=['jpg', 'png'],
        default='jpg',
        help='Output format (default: jpg)'
    )
    
    parser.add_argument(
        '--output',
        help='Output directory (default: same as input file)'
    )
    
    args = parser.parse_args()
    
    # Process inputs
    files_to_convert = []
    for input_path in args.inputs:
        if os.path.isfile(input_path):
            if input_path.lower().endswith('.heic'):
                files_to_convert.append(input_path)
            else:
                print(f"Warning: Skipping non-HEIC file: {input_path}")
        elif os.path.isdir(input_path):
            heic_files = find_heic_files(input_path)
            if heic_files:
                files_to_convert.extend(heic_files)
            else:
                print(f"Warning: No HEIC files found in directory: {input_path}")
        else:
            print(f"Warning: Input path does not exist: {input_path}")
    
    if not files_to_convert:
        print("Error: No HEIC files found to convert")
        sys.exit(1)
    
    # Convert files
    success_count = 0
    error_count = 0
    
    print(f"\nConverting {len(files_to_convert)} files to {args.format.upper()}...")
    for file_path in files_to_convert:
        success, message = convert_file(file_path, args.format, args.output)
        if success:
            success_count += 1
            print(f"✅ {message}")
        else:
            error_count += 1
            print(f"❌ {message}")
    
    # Print summary
    print(f"\nConversion complete!")
    print(f"Successfully converted: {success_count}")
    if error_count > 0:
        print(f"Failed to convert: {error_count}")
        sys.exit(1)

if __name__ == "__main__":
    main()
