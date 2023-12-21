import cv2                              # py -m pip install opencv-python
import numpy as np                      # py -m pip install numpy
from skimage.registration import phase_cross_correlation #  py -m pip install scikit-image
import os


def CalculateDeltaXY(bild1, bild2, pathname=None):

    # optionaler Pfadname
    # ohne Angabe Pfadname wird im aktuellen Verzeichnis gesucht
    if pathname != None:
        bild1 = os.path.join(pathname, bild1)
        bild2 = os.path.join(pathname, bild2)
   

    # Lade das erste Bild
    image = cv2.imread(bild1, 0)

    # Setze die Variablen X und Y
    Y, X = image.shape

    # Berechne die neuen Dimensionen des Rechtecks
    new_X = int(X - 0.1 * X)
    new_Y = int(Y - 0.1 * Y)

    # Berechne die Koordinaten des oberen linken und unteren rechten Punktes des Rechtecks
    top_left = (X - new_X) // 2, (Y - new_Y) // 2
    bottom_right = top_left[0] + new_X, top_left[1] + new_Y

    # Zeichne das Rechteck in das Bild ein
    cv2.rectangle(image, top_left, bottom_right, (255, 0, 0), 2)

    # Lade das zweite Bild
    image2 = cv2.imread(bild2, 0)

    # Extrahiere den relevanten Bereich aus beiden Bildern
    image_cropped = image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
    image2_cropped = image2[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

    # Berechne die Verschiebung zwischen den beiden Bildern
    shift, error, diffphase = phase_cross_correlation(image_cropped, image2_cropped)

    # print(f"Das Bild {bild2} ist um {shift[1]} Pixel in X-Richtung und {shift[0]} Pixel in Y-Richtung gegenüber dem Bild {bild1} verschoben.")

    return shift




if __name__ == '__main__':

    bild_X0Y0 = "3PunkteX0Y0.png"
    bild_XNYN = "3PunkteXNYN.png"
    shift = CalculateDeltaXY(bild_XNYN, bild_X0Y0)
    print(f"Das Bild {bild_XNYN} ist um {shift[1]} Pixel in X-Richtung und {shift[0]} Pixel in Y-Richtung gegenüber dem Bild {bild_X0Y0} verschoben.")
