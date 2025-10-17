# Learn-Basics-task-
Implement a Python program that arranges images of random sizes and shapes into a PDF while minimizing wasted space and preserving aspect ratios.

## Algorithm
Uses **Next-Fit Decreasing Height (NFDH)** packing algorithm:
- Sorts images by height (tallest first)
- Packs images into horizontal shelves
- Creates new pages when needed
- Achieves ~70-80% space efficiency

## Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic usage:
```bash
python task_1_starter_code.py
```

### With custom options:
```bash
python task_1_starter_code.py -i input_images -o output.pdf -q 85
```

### Arguments:
- `-i, --input`: Input folder containing images (default: input_images)
- `-o, --output`: Output PDF file path (default: output.pdf)
- `-q, --quality`: JPEG compression quality 1-100 (default: 85)

## Features
✅ Automatic image preprocessing
✅ Transparent background removal
✅ Aspect ratio preservation
✅ Efficient space packing
✅ Multi-page support
✅ Image compression
✅ CLI interface
✅ Error handling
✅ Detailed logging

## Example
```bash
# Generate sample images
python sample_data_generation.py

# Pack images into PDF
python task_1_starter_code.py -i input_images -o result.pdf -q 90
```
Implementation Highlights
Class Structure
• ImagePacker - Main orchestrator class
• preprocess_image() - Handles transparency & cropping
• pack_images_nfdh() - NFDH algorithm implementation
• generate_pdf() - ReportLab PDF creation
Bonus Features Included
✅ Image compression with quality control
✅ Full CLI with argparse
✅ Comprehensive logging
✅ Error handling & validation
