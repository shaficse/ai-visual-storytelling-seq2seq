from glob import glob
import os
import cv2
import numpy as np
import json

class ImageDataReader:
    def __init__(self, root_directory, mean_path="mean.json", batch_size=64, image_size=(227, 227)):
        self.root_directory = root_directory
        self.mean = self.get_bgr_channel_mean(mean_path)
        self.mean = np.array(self.mean)
        self.batch_size = batch_size
        self.image_size = image_size
        self.image_paths, self.image_ids = self.get_all_filenames(self.root_directory)
        self.current_index = 0

    def get_all_filenames(self, root_directory):
        images_path_names = [y for x in os.walk(root_directory) for y in glob(os.path.join(x[0], "*.jpg"))]
        image_index = []
        for i in range(len(images_path_names)):
            name = images_path_names[i].split("/")
            nm1 = name[len(name) - 1].split(".")
            image_index.append(nm1[0])
        return images_path_names, image_index

    def next_batch(self):

        result = []
        current_paths = self.image_paths[self.current_index:self.current_index + self.batch_size]
        current_image_ids = self.image_ids[self.current_index:self.current_index + self.batch_size]

        self.current_index += self.batch_size

        for i in range(len(current_paths)):
            image = cv2.imread(current_paths[i],1)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            image = self.resize_in_aspect_to_ration(image)
            image = self.center_crop_image(image).astype(float)
            print(self.mean.shape)
            image -= self.mean
            cv2.imshow("n",image)
            cv2.waitKey(0)
            result.append(image)

        return result, current_image_ids


    # Returns resized image in aspect to ratio
    def resize_in_aspect_to_ration(self, image):
        height = image.shape[0]
        width = image.shape[1]
        ratio = float(height) / float(width)
        if ratio > 1:
            new_width = self.image_size[0]
            new_height = new_width * ratio
        else:
            new_height = self.image_size[1]
            new_width = new_height / ratio

        dim = (int(new_width), int(new_height))
        image1 = cv2.resize(image, dim)
        return image1

    # Returns center cropped image
    def center_crop_image(self, image):
        height = image.shape[0]
        width = image.shape[1]

        if height >= width:
            center = height / 2
            left = center - width / 2
            right = center + width / 2
            crop_img = image[left:right + 1, 0:width]
        else:
            center = width / 2
            left = center - height / 2
            right = center + height / 2
            crop_img = image[0:height, left:right + 1]

        return crop_img

    def get_bgr_channel_mean(self, mean_path):
        mean = json.load(open(mean_path))
        red_mean = mean['red_mean']
        blue_mean = mean['blue_mean']
        green_mean = mean['green_mean']
        return blue_mean, green_mean, red_mean