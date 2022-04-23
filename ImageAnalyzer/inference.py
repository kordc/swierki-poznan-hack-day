import sys
sys.path.append(".")

import cv2 as cv
import numpy as np
from satellite import Satelite, CoordinateManager
from here.hereApi import hereApi
from statistics import normalized_green_level

def baseline_inference(img):
    #convert the BGR image to HSV colour space
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    #set the lower and upper bounds for the green hue
    lower_green = np.array([36,25,25])
    upper_green = np.array([70,255,100])

    #create a mask for green colour using inRange function
    mask = cv.inRange(hsv, lower_green, upper_green)

    #perform bitwise and on the original image arrays using the mask
    res = cv.bitwise_and(img, img, mask=mask)

    res = res[:,:,1] # take just the green channel
    kernel = np.ones((8,8),np.uint8) #
    res = cv.morphologyEx(res, cv.MORPH_OPEN, kernel) #perform some kind of morphological operation
    #res = cv.erode(res,kernel,iterations = 1)

    return res

class Inference:
    def __init__(self, satelite: Satelite, inference_function = baseline_inference, statistic_function=normalized_green_level):
        self.satelite = satelite
        self.inference_function = inference_function
        self.statistic_function = statistic_function

    
    def infer_bounding_box(self, coordinates, save=False):
        heatmap = np.zeros(satelite.get_shape_of_heap_map(coordinates))

        for coords, img in self.satelite.iterate_over_box(coordinates, save=False):
            inferenced_image = self.inference_function(img) #image returned from the model (image segmentation, bounding box etc)
            statistic = self.statistic_function(inferenced_image)
            
            

            curr_x, curr_y = coords
            
            heatmap[curr_y, curr_x] = statistic
            #yield self.inference_function(img)
        
        return heatmap
            


if __name__ == '__main__':
    coordinate = CoordinateManager(zoom=16)
    satelite = Satelite(accessToken = 'pk.eyJ1Ijoic2ViYXN0aWFuY2giLCJhIjoiY2wyOHVldzhyMGQxbzNybGc1NDVwazEwNSJ9.PjStIMIxWUiVb0-yWUc41A',
                coordinate_manager= coordinate, zoom=coordinate.zoom)
    inference = Inference(satelite, inference_function = baseline_inference)

    here = hereApi()
    coordinates = here.getData("Poznan, old market")[1]

    print(inference.infer_bounding_box(coordinates))

    # for i, img in enumerate(inference.infer_bounding_box(coordinates)):
    #     cv.imwrite(f"{i}.jpg", img)
    #     break
        






