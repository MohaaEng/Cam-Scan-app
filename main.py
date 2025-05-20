########################################################
######## Name: Mohand Aymn Abd El-kader ########
########		ID: 18P6298	########
######## Machine Vision Course (CSE480) ########
######## Submitted To : Dr. Hossam Hassan ######
######## Submitted To : Eng : Yehia     ########
#########################################################
import os
from kivy.app import App
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.core.window import Window
import time
import cv2
import numpy as np
import mapper
from PIL import Image
############################################################
Builder.load_file('main.kv')

############################################################
class MyLayout(TabbedPanel):
    def capture(self):  ### Button Function When it's pressed down ###
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M")
        filename = "IMG{}.png".format(timestr)
        camera.export_to_png(filename)
        img = cv2.imread(filename)
        return img
    
    ########################################################
    def rescale_frame(self, frame, percent=80):
        width = int(frame.shape[1] * percent / 50)
        height = int(frame.shape[0] * percent / 50)
        dim = (width, height)
        return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    
    ########################################################
    def processing(self, img):
        imggray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imggray, (5, 5), 1)
        imgCanny = cv2.Canny(imgBlur, 70, 100)
        kernel = np.ones((5, 5))
        imgDial = cv2.dilate(imgCanny, kernel, iterations=2)
        imgThres = cv2.erode(imgDial, kernel, iterations=1)
    
        cv2.imwrite('imggrayy.png', imggray)
        cv2.imwrite('imgblur.png', imgBlur)
        cv2.imwrite('imgcanny.png', imgCanny)
        return imgThres
    
    ########################################################
    def getContours(self, img):
        biggest = np.array([])
        maxArea = 0
        contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 5000:
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                if area > maxArea and len(approx) == 4:
                    biggest = approx
                    maxArea = area
        cv2.drawContours(imgContour, biggest, -1, (0, 0, 255), 30)
        return biggest
    
    ########################################################
    def reorder(self, points):
        points = points.reshape((4, 2))
        newPoints = np.zeros((4, 1, 2), np.int32)
        add = points.sum(1)
        newPoints[0] = points[np.argmin(add)]
        newPoints[3] = points[np.argmax(add)]
        diff = np.diff(points, axis=1)
        newPoints[1] = points[np.argmin(diff)]
        newPoints[2] = points[np.argmax(diff)]
        return newPoints
    
    ########################################################
    def wrap(self, img, biggest, imgSize):
        widthImg = imgSize[0]
        heightImg = imgSize[1]
        biggest = self.reorder(biggest)
        pts1 = np.float32(biggest)
        pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgOutput = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
        imgCropped = imgOutput[20:imgOutput.shape[0] - 20, 20:imgOutput.shape[1] - 20]
        imgCropped = cv2.resize(imgCropped, (widthImg, heightImg))
        return imgCropped
    
    ########################################################
    def scann(self):
        image_gray = self.ids['my_gray']
        image_blur = self.ids['my_blur']
        image_cany = self.ids['my_cany']
        image_final = self.ids['my_final']
    
    
        # Set the source property of the Image widget to display the imggray image
        image_gray.source = 'imggrayy.png'
        image_blur.source = 'imgblur.png'
        image_cany.source = 'imgcanny.png'
        image_final.source = 'Doc.png'
    
    
        # Force the Image widget to reload the image
        image_gray.reload()
        image_blur.reload()
        image_cany.reload()
        image_final.reload()
    
    ########################################################
    def savepdf(self):
        output_pdf_path = 'doc.pdf'
        imgpdf = Image.open('Doc.png')
        imgpdf.save(output_pdf_path, 'PDF',resolution=100.0)
        if os.path.exists(output_pdf_path):
            print("done,nice")
        else:
            print("no, please try again")
	########################################################
while True:
    layout = MyLayout()  ###Create an Instance of The Class To access the Functions Within later calling that Instance
    img = layout.capture()  ###Calling Capture Function
    imgSize = img.shape  ###Getting The size of the Original Image
    imgContour = img.copy()
    processdImg = layout.processing(img)  ###Getting Threshold image after Canny edge Detection
    biggest = layout.getContours(processdImg)  #### Getting biggest Rectangle Contours
    ###################################
    if biggest.size != 0:
        imgWarped = layout.wrap(img, biggest, imgSize)
        imggraysharp = cv2.cvtColor(imgWarped, cv2.COLOR_BGR2GRAY)
        imgBlursharp = cv2.GaussianBlur(imggraysharp, (5, 5), 1)
        highpass = cv2.subtract(imggraysharp, imgBlursharp)
        sharpened = cv2.add(imggraysharp, highpass)
        cv2.imwrite('Doc.png', sharpened)
    
    else:
        pass
####################################
class MyScanApp(App)
    def build(self):
        Window.clearcolor = (117.0 / 255.0, 107.0 / 255.0, 105.0 / 255.0, 1)
        Window.size = (600,650)
        return MyLayout()

if __name__ == '__main__':
	MyScanApp().run()