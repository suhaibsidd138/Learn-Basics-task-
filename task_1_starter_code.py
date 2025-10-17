Image Packing PDF Generator
Author: Task Solution
Description: Packs images of random sizes into PDF using NFDH algorithm
"""

import os
import argparse
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# PDF page configuration (A4)
PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 10 * mm
PADDING = 5 * mm


class ImagePacker:
    """Handles image preprocessing and packing into PDF"""
    
    def __init__(self, input_folder, output_file, quality=85):
        self.input_folder = input_folder
        self.output_file = output_file
        self.quality = quality
        self.images = []
        
    def preprocess_image(self, img_path):
        """
        Preprocess image: remove transparency, crop to bounding box
        Returns: (processed_image, width, height)
        """
        try:
            img = Image.open(img_path)
            
            # Convert RGBA to RGB (remove transparency)
            if img.mode == 'RGBA':
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Crop to bounding box (remove extra whitespace)
            bbox = img.getbbox()
            if bbox:
                img = img.crop(bbox)
            
            # Save preprocessed image
            temp_path = img_path.replace('.png', '_processed.jpg')
            img.save(temp_path, 'JPEG', quality=self.quality, optimize=True)
            
            return temp_path, img.width, img.height
            
        except Exception as e:
            logger.error(f"Error processing {img_path}: {str(e)}")
            return None, 0, 0
    
    def load_images(self):
        """Load and preprocess all images from input folder"""
        logger.info(f"Loading images from {self.input_folder}")
        
        if not os.path.exists(self.input_folder):
            raise FileNotFoundError(f"Input folder not found: {self.input_folder}")
        
        image_files = [f for f in os.listdir(self.input_folder) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
        if not image_files:
            raise ValueError(f"No images found in {self.input_folder}")
        
        for img_file in image_files:
            img_path = os.path.join(self.input_folder, img_file)
            processed_path, width, height = self.preprocess_image(img_path)
            
            if processed_path:
                self.images.append({
                    'path': processed_path,
                    'original_path': img_path,
                    'width': width,
                    'height': height,
                    'name': img_file
                })
        
        logger.info(f"Loaded {len(self.images)} images")
        return self.images
    
    def pack_images_nfdh(self):
        """
        Pack images using Next-Fit Decreasing Height (NFDH) algorithm
        Returns: List of pages, each containing positioned images
        """
        # Sort images by height (tallest first)
        sorted_images = sorted(self.images, key=lambda x: x['height'], reverse=True)
        
        pages = []
        current_page = []
        
        # Available space on current page
        available_width = PAGE_WIDTH - 2 * MARGIN
        available_height = PAGE_HEIGHT - 2 * MARGIN
        
        # Current shelf (row) position
        current_x = MARGIN
        current_y = PAGE_HEIGHT - MARGIN
        shelf_height = 0
        
        for img in sorted_images:
            # Calculate scaled dimensions to fit page
            scale = min(
                (available_width - PADDING) / img['width'],
                (available_height - PADDING) / img['height']
            )
            scaled_width = img['width'] * scale
            scaled_height = img['height'] * scale
            
            # Check if image fits on current shelf
            if current_x + scaled_width + PADDING > PAGE_WIDTH - MARGIN:
                # Move to next shelf
                current_x = MARGIN
                current_y -= (shelf_height + PADDING)
                shelf_height = 0
            
            # Check if new shelf fits on page
            if current_y - scaled_height < MARGIN:
                # Start new page
                if current_page:
                    pages.append(current_page)
                current_page = []
                current_x = MARGIN
                current_y = PAGE_HEIGHT - MARGIN
                shelf_height = 0
            
            # Add image to current shelf
            current_page.append({
                'path': img['path'],
                'name': img['name'],
                'x': current_x,
                'y': current_y - scaled_height,
                'width': scaled_width,
                'height': scaled_height
            })
            
            current_x += scaled_width + PADDING
            shelf_height = max(shelf_height, scaled_height)
        
        # Add last page
        if current_page:
            pages.append(current_page)
        
        logger.info(f"Packed images into {len(pages)} pages")
        return pages
    
    def generate_pdf(self, pages):
        """Generate PDF from packed pages"""
        logger.info(f"Generating PDF: {self.output_file}")
        
        c = canvas.Canvas(self.output_file, pagesize=A4)
        
        for page_num, page in enumerate(pages, 1):
            logger.info(f"Rendering page {page_num}/{len(pages)} with {len(page)} images")
            
            for img_data in page:
                try:
                    c.drawImage(
                        img_data['path'],
                        img_data['x'],
                        img_data['y'],
                        width=img_data['width'],
                        height=img_data['height'],
                        preserveAspectRatio=True
                    )
                except Exception as e:
                    logger.error(f"Error drawing image {img_data['name']}: {str(e)}")
            
            if page_num < len(pages):
                c.showPage()
        
        c.save()
        logger.info(f"PDF saved successfully: {self.output_file}")


def main():
    """Main function with CLI"""
    parser = argparse.ArgumentParser(
        description='Pack images into PDF using efficient packing algorithm'
    )
    parser.add_argument(
        '-i', '--input',
        default='input_images',
        help='Input folder containing images (default: input_images)'
    )
    parser.add_argument(
        '-o', '--output',
        default='output.pdf',
        help='Output PDF file path (default: output.pdf)'
    )
    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        help='JPEG quality for compression (1-100, default: 85)'
    )
    
    args = parser.parse_args()
    
    try:
        # Create packer instance
        packer = ImagePacker(args.input, args.output, args.quality)
        
        # Load and preprocess images
        packer.load_images()
        
        # Pack images using NFDH algorithm
        pages = packer.pack_images_nfdh()
        
        # Generate PDF
        packer.generate_pdf(pages)
        
        logger.info("Process completed successfully!")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
