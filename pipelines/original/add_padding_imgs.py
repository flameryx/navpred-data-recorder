import cv2
import os
import math
from argparse import ArgumentParser

# This script adds enough padding to each map image so that each image has the same number of pixels in width and height 

parser = ArgumentParser()
parser.add_argument(
    "--goal_width",
    action="store",
    dest="goal_width",
    default=150,
    help="What width do you want the map image to have.",
    required=False,
)

parser.add_argument(
    "--goal_height",
    action="store",
    dest="goal_height",
    default=150,
    help="What height do you want the map image to have.",
    required=False,
)
args = parser.parse_args()
goal_width = int(args.goal_width)
goal_height = int(args.goal_height)

maps = os.listdir("maps")
map_test = ""
for map_name in maps:
    image_path = f"maps/{map_name}/{map_name}.png"

    img = cv2.imread(image_path)
    img_height, img_width, channels = img.shape
    
    print(f"Map Name: {map_name}")
    map_test = map_name
    
    print(f"Height: {img_height} | Width: {img_width} | Channels: {channels}")
    width_padding = goal_width - img_width
    height_padding = goal_height - img_height
    image = cv2.copyMakeBorder(img, height_padding, 0, width_padding, 0, cv2.BORDER_CONSTANT)
    
    cv2.imwrite(image_path, image)
    
    print("After change:")
    img = cv2.imread(image_path)
    img_height, img_width, channels = img.shape

    print(f"Height: {img_height} | Width: {img_width} | Channels: {channels}")
    print()
