import sys
import random
from PIL import Image

ROWS = 3
IMG_COUNT = 30

if __name__ == '__main__':
    scored_images_filepath = sys.argv[1]
    output_path = sys.argv[2]
    image_scores = []
    with open(scored_images_filepath, 'r') as f:
        for line in f:
            score, file = line.split(',')
            score = float(score)
            file = file.strip()
            image_scores.append((score, file))
    image_scores = random.sample(image_scores, IMG_COUNT)
    image_scores = sorted(image_scores, key=lambda tup: tup[0])

    height, width = Image.open(image_scores[0][1]).size
    output_image = Image.new('RGB', (width * len(image_scores) // ROWS, height * ROWS))

    for i, ims in enumerate(image_scores):
        im = Image.open(ims[1])
        output_image.paste(im, (width*(i // ROWS), i % ROWS * height))

    output_image.save(output_path)
