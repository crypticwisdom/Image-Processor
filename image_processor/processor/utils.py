import cv2
from os import path
from os import listdir
from django.conf import settings
import blur_detector
import cv2

def variance_of_laplacian(image):
    # compute the Laplacian of the image and then return the focus
    # measure, which is simply the variance of the Laplacian
    return cv2.Laplacian(image, cv2.CV_64F).var()


def check_if_blur(cv_image_instance, image, image_path):
    image1 = cv2.imread(f"{image_path}/{image.name}")

    gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)

    fm = variance_of_laplacian(gray)

    # if the focus measure is less than the supplied threshold,
    # then the image should be considered "blurry"
    # if fm < 1:
    if fm < 6_5_0:
        return False, "Blurry"
    return True, "Not Blurry"

    # show the image
    # cv2.putText(image1, "{}: {:.2f}".format(text, fm), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 3)

