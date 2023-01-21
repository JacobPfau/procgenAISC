"""
Tool for stacking two images on top of each other. If one is colour and the
other is grayscale, the output image will be colour. If one of the image is
wider than the other, the narrower image is centered and padded with black.

Usage: 
    python3.9 stack_images.py top_image.png bottom_image.png output_image.png
"""
import sys
from PIL import Image

if __name__ == '__main__':
    top_image, bottom_image, output_path = sys.argv[1:]
    images = [Image.open(top_image), Image.open(bottom_image)]
    widths, heights = zip(*(i.size for i in images))
    
    height = sum(heights)
    width = max(widths)
    padding = [(width - w) // 2 for w in widths]

    output_image = Image.new('RGB', (width, height))

    y_offset = 0
    for i, im in enumerate(images):
        output_image.paste(im, (padding[i], y_offset))
        y_offset += heights[i]

    output_image.save(output_path)
