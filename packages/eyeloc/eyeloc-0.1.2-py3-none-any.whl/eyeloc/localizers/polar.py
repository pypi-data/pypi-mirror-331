import cv2

import numpy as np

from .peaks import *

from ..fitting import fitCircleLS
from ..filters import SimpleMedian, CircleRANSAC
from ..prepocessing import image_preprocessing
from ..localizers import Find
from ..center_estimation import CenterEstimation, darkestPixel, largestComponentCentroid


class PolarFinder():
    def __init__(self, mode: int, 
                 center_estimation_mode: int = CenterEstimation.Min,
                 angles: list[int] = None,
                 peaks_find_method: int = PolarPeaks.Gradient,
                 filter_model = None,
                 fitting_method: callable = fitCircleLS) -> None:
        
        assert mode in [Find.Pupil, Find.Iris], "Wrong mode value. Use one of: irisloc.FIND_PUPIL, irisloc.FIND_IRIS"
        self.mode = mode
        self.center_estimation_mode = center_estimation_mode
        self.peaks_find_method = peaks_find_method
        if angles == None:
            self.angles = range(128)
            # if mode == Find.Pupil:
            #     self.angles = range(128)
            # elif mode == Find.Iris:
            #     self.angles = list([*range(0, 16), *range(48, 80), *range(112, 128)])
        else:
            self.angles = angles
            
        if filter_model == None:
            if mode == Find.Pupil:
                self.filter_model = SimpleMedian(1)
            elif mode == Find.Iris:
                self.filter_model = SimpleMedian(0.7)
            
        else:
            self.filter_model = filter_model
            
        self.fitting_method = fitting_method

    def find(self, source):
        if self.mode == Find.Pupil:
            mode_func = np.min
        elif self.mode== Find.Iris:
            mode_func = np.max
        else:
            raise KeyError("Wrong mode value. Use one of: irisloc.FIND_PUPIL, irisloc.FIND_IRIS")
        
        img, inp = image_preprocessing(source)
        
        # CENTER ESTIMATION
        if self.center_estimation_mode == CenterEstimation.Min:
            self.center_estimation = darkestPixel(img)
        elif self.center_estimation_mode == CenterEstimation.LargestComponentCentroid:
            self.center_estimation = largestComponentCentroid(inp)
        
        # POLAR WARP
        maxRad = 90.50966799187809
        img = img.astype(np.float32)
        polar = cv2.linearPolar(img, self.center_estimation, maxRad, cv2.WARP_FILL_OUTLIERS).astype(np.uint8)
        
        polar = cv2.medianBlur(polar, 9)
        
        # PEAKS SEARCHING
        if  self.peaks_find_method == PolarPeaks.Gradient:
            peaks = grad_peaks(polar, self.angles, mode_func)
                    
        elif self.peaks_find_method == PolarPeaks.Canny:
            peaks = canny_peaks(polar, self.angles, mode_func)
            
        elif self.peaks_find_method == PolarPeaks.FuncFitting:
            peaks = curvefit_peaks(polar, self.angles, mode_func)
                
        normalized_peaks = np.array([peak*maxRad/128 for peak in peaks])
        angles_rad = np.array(self.angles)*2*np.pi/128
        
        xs = np.full((len(self.angles),), self.center_estimation[1])+np.sin(angles_rad)*normalized_peaks
        ys = np.full((len(self.angles),), self.center_estimation[0])+np.cos(angles_rad)*normalized_peaks
        edge_points = np.vstack([ys, xs]).T
        
        # SIMPLE FILTERING
        edge_points = np.where(edge_points < 128, edge_points, -1)
        edge_points = edge_points[edge_points[:, 0] > 0]
        edge_points = edge_points[edge_points[:, 1] > 0]
        edge_points = edge_points[edge_points[:, 0] < 127]
        edge_points = edge_points[edge_points[:, 1] < 127]
        
        if self.fitting_method == fitCircleLS:
            if len(edge_points) < 3:
                return ((-1, -1), 0), []
        elif self.fitting_method in [cv2.fitEllipse, cv2.fitEllipseAMS, cv2.fitEllipseDirect]:
            if len(edge_points) < 5:
                return ((-1, -1), (0, 0), 0), []
        
        filtered_points = self.filter_model.filter(edge_points)
        
        if len(filtered_points) == 0:
            # print()
            # print("WARNING! Choosen filter_method in TwoGradMax returned 0 points.")
            # print()
            if self.fitting_method == fitCircleLS:
                return (-1, -1), 0
            elif self.fitting_method in [cv2.fitEllipse, cv2.fitEllipseAMS, cv2.fitEllipseDirect]:
                return (-1, -1), (0, 0), 0

        return self.fitting_method(filtered_points.astype(np.float32))
