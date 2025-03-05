import cv2

import numpy as np

from ..localizers import Find
from ..prepocessing import image_preprocessing

class HoughTransform():
    def __init__(self, mode: int,
                 hough_param2=30,
                 preprocess: bool = True) -> None:
        assert mode in [Find.Pupil, Find.Iris], "Wrong mode value. Use one of: irisloc.FIND_PUPIL, irisloc.FIND_IRIS"
        self.mode = mode
        
        self.hough_param2=hough_param2
        
        self.preprocess = preprocess
        
        if mode == Find.Pupil:
            self.min_radius=8
            self.max_radius=36
        elif mode == Find.Iris:
            self.min_radius=36
            self.max_radius=64
        
    def find(self, source):
        if self.preprocess:
            img = image_preprocessing(source)
        
        # canny = cv2.Canny(img.astype(np.uint8), 128, 255)
        # circles = cv2.HoughCircles(canny.astype(np.uint8), cv2.HOUGH_GRADIENT, 
        #                            1, 1, 
        #                            param1=128, param2=self.hough_param2, 
        #                            minRadius=self.hough_minRadius, maxRadius=self.hough_maxRadius)
        
        # # print(circles)
        
        # if circles == None:
        #     return (-1, -1), 0, []
        
        # circles_sorted = np.array(sorted(circles[0], key=lambda x: x[2], reverse=True))
        
        # radii = circles_sorted[:, 2]
        # hist, bin_edges = np.histogram(radii, bins=2)
        # threshold_radius = bin_edges[1]
        
        # if self.mode == FIND_PUPIL:
        #     result = circles_sorted[np.where(circles_sorted[:,2] < threshold_radius)][0]
        # elif self.mode == FIND_IRIS:
        #     result = circles_sorted[np.where(circles_sorted[:,2] > threshold_radius)][0]
        # result = circles_sorted[len(circles_sorted)//2]
        # return (result[0], result[1]), result[2], circles_sorted

        # Edge detection
        edges = cv2.Canny(img.astype(np.uint8), 128, 255)

        height, width = edges.shape
        accumulator = np.zeros((height, width, self.max_radius - self.min_radius))

        # Hough Transform for circles
        for y in range(height):
            for x in range(width):
                if edges[y, x] > 0:  # Edge point
                    for r in range(self.min_radius, self.max_radius):
                        for theta in range(0, 360):
                            a = int(x - r * np.cos(theta * np.pi / 180))
                            b = int(y - r * np.sin(theta * np.pi / 180))
                            if 0 <= a < width and 0 <= b < height:
                                accumulator[b, a, r - self.min_radius] += 1

        # Find the best circle
        max_accumulator = np.unravel_index(np.argmax(accumulator), accumulator.shape)
        best_y, best_x, best_r = max_accumulator
        best_r += self.min_radius

        return (best_x, best_y), best_r