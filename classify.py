import tkinter as tk
from PIL import Image, ImageTk
import os
import cv2
import glob
import numpy as np

SCREENTONE_DIR = "Flow2/3.5/sc"
IMG_DIR = "Flow2/2/img"
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class ScWindow:
    def __init__(self):
        self.labelTypes = []

        # set colorlist
        self.colorlist = [
            [234, 150, 150],
            [150, 234, 150],
            [150, 150, 234]
        ]

        # imgList
        self.imgList = glob.glob(os.path.join(IMG_DIR, "*.png"))
        self.imgList = [os.path.basename(img)[:-4] for img in self.imgList]
        self.imgIdx = 0

        # element in window
        self.window = tk.Tk()
        self.window.title('modify screentone classification')
        self.window.geometry('800x600')

        # self.lbl_1 = tk.Label(self.window, text='Hello World', bg='yellow', fg='#263238', font=('Arial', 12))
        # self.lbl_1.grid(column=0, row=0)
        # self.btn = tk.Button(self.window, text='Hello World', bg='yellow', fg='#263238', font=('Arial', 12), command=self.test)
        # self.btn.grid(column=1, row=0)
        div1 = tk.Frame(self.window, width=100, bg='white')
        div2 = tk.Frame(self.window, bg='orange')
        div3 = tk.Frame(self.window, width=100, bg='white')
        div1.grid(column=0, row=0, sticky='nwes')
        div2.grid(column=1, row=0, sticky='nwes')
        div3.grid(column=2, row=0, sticky='nwes')

        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1000)
        self.window.columnconfigure(2, weight=1)
        self.window.rowconfigure(0, weight=1)
        div2.rowconfigure(0, weight=1)
        
        # self.lbl_img = tk.Label(div2, image=imgTk)
        # self.lbl_img.grid(column=0, row=0, sticky='nwes')

        self.canvas = tk.Canvas(div2)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.canvas.update()
        self.canvas.bind("<Button-1>", self.drawStart)
        self.canvas.bind("<B1-Motion>", self.drawing)
        self.canvas.bind("<ButtonRelease-1>", self.drawEnd)
        canvasWidth, canvasHeight = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.imageContainer = self.canvas.create_image(canvasWidth//2, canvasHeight//2, anchor="center")
        self.changeImg(self.imgIdx)

        # full screen
        self.isFullScreen = False
        self.window.bind('<F12>', self.toggle_fullScreen)

        # key
        self.window.bind('<Key>', self.pressKey)

        self.window.mainloop()
    
    def loadAllImg(self, name):
        self.selectedMaskIdxs = []
        canvasWidth, canvasHeight = self.canvas.winfo_width(), self.canvas.winfo_height()
        # load image
        self.img = self.loadImg(canvasHeight, canvasWidth, IMG_DIR, name + ".png")
    
        # load mask
        masks = glob.glob(os.path.join(SCREENTONE_DIR, "*/" + name + "_*.png"))

        imgHeight, imgWidth, _ = self.img.shape
        self.imgStartX = (canvasWidth - imgWidth) / 2
        self.imgStartY = (canvasHeight - imgHeight) / 2
    
        self.masks = []
        self.maskImg = np.zeros((imgHeight, imgWidth, 4), np.uint8)
        for mask in masks:
            maskImg = self.loadImg(canvasHeight, canvasWidth, mask)
            rect = cv2.moments(maskImg[:, :, 3])
            if rect["m00"] != 0:
                centerX = rect["m10"] / rect["m00"]
                centerY = rect["m01"] / rect["m00"]
                labelType = int(os.path.basename(os.path.split(mask)[0]))
                if labelType not in self.labelTypes:
                    self.labelTypes.append(labelType)
                self.masks.append(((centerX, centerY), mask, labelType))
                self.maskImg[maskImg[:, :, 3] == 255, :] = self.getColor(labelType)
        
        maskNotEmptyNp = self.maskImg[:, :, 3] == 255
        self.img[maskNotEmptyNp, :3] = np.uint8(0.5 * self.img[maskNotEmptyNp, :3] + 0.5 * self.maskImg[maskNotEmptyNp, :3])
        self.imgTk =  ImageTk.PhotoImage(Image.fromarray(self.img))
        self.canvas.itemconfig(self.imageContainer, image=self.imgTk)
    
    def loadImg(self, maxHeight, maxWidth, path, filename=None):
        if filename is None:
            file = path
        else:
            file = os.path.join(path, filename)
        # img = Image.open(os.path.join(dir, filename)).convert("RGBA")
        img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
        height, width, _ = img.shape
        widthScale = width / maxWidth
        heightScale = height / maxHeight
        scale = heightScale if heightScale > widthScale else widthScale
        if scale > 1:
            imgWidth, imgHeight = int(width / scale), int(height / scale)
            img = cv2.resize(img, (imgWidth, imgHeight))
        return img

    def getImageCenter(self, img):
        (offset_w, offset_h) = font.getoffset(txt)
        (x, y, W_mask, H_mask) = font.getmask(txt).getbbox()
        drawer.text((10, 10 - offset_h), txt, align='center', font=font)
        drawer.rectangle((10, 10, W + offset_w, 10 + H - offset_h), outline='black')
        drawer.rectangle((x+10, y+10, W_mask+10, H_mask+10), outline='red')
        image.show()
        image.save('example.png', 'PNG')
        
    def drawStart(self, event):
        self.drawPoints = []
        self.draw_line_ids = []
        self.lastx, self.lasty = event.x, event.y
        self.drawPoints.append([self.lastx - self.imgStartX, self.lasty - self.imgStartY])
 
    def drawing(self, event):
        line_id = self.canvas.create_line((self.lastx, self.lasty, event.x, event.y))
        self.draw_line_ids.append(line_id)
        self.lastx, self.lasty = event.x, event.y
        self.drawPoints.append([self.lastx - self.imgStartX, self.lasty - self.imgStartY])

    def drawEnd(self, event):
        def is_in_poly(p, poly):
            px, py = p
            is_in = False
            for i, corner in enumerate(poly):
                next_i = i + 1 if i + 1 < len(poly) else 0
                x1, y1 = corner
                x2, y2 = poly[next_i]
                if (x1 == px and y1 == py) or (x2 == px and y2 == py):  # if point is on vertex
                    is_in = True
                    break
                if min(y1, y2) < py <= max(y1, y2):  # find horizontal edges of polygon
                    x = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
                    if x == px:  # if point is on edge
                        is_in = True
                        break
                    elif x > px:  # if point is on left-side of line
                        is_in = not is_in
            return is_in
        self.selectedMaskIdxs = []
        idx = 0
        for (centerX, centerY), mask, _ in self.masks:
            if is_in_poly([centerX, centerY], self.drawPoints):
                self.selectedMaskIdxs.append(idx)
            idx += 1
        for id in self.draw_line_ids:
            self.canvas.delete(id)
    
    def changeMaskType(self, labelType):
        if labelType in self.labelTypes and len(self.selectedMaskIdxs) > 0:
            for i in self.selectedMaskIdxs:
                (centerX, centerY), mask, _ = self.masks[i]
                self.masks[i] = ((centerX, centerY), mask, labelType)
                maskImg = self.loadImg(self.canvas.winfo_height(), self.canvas.winfo_width(), mask)
                maskIdx = maskImg[:, :, 3] == 255
                self.img[maskIdx, :] = 0.5 * maskImg[maskIdx, :] + 0.5 * np.array(self.getColor(labelType))
            self.imgTk =  ImageTk.PhotoImage(Image.fromarray(self.img))
            self.canvas.itemconfig(self.imageContainer, image=self.imgTk)
    
    def addNewMaskType(self):
        newNum = max(self.labelTypes) + 1
        self.labelTypes.append(newNum)
        return newNum

    def toggle_fullScreen(self, event):
        self.isFullScreen = not self.isFullScreen
        self.window.attributes('-fullscreen', self.isFullScreen)
    
    def getColor(self, index, alpha=True):
        if index >= len(self.colorlist):
            def createNewColor():
                return list(np.random.choice(range(256), size=3))
            for _ in range(index, len(self.colorlist) + 1):
                self.colorlist.append(createNewColor())
        if alpha:
            return [self.colorlist[index][0], self.colorlist[index][1], self.colorlist[index][2], 255]
        return self.colorlist[index]

    def save(self):
        idx = 0
        for c, mask, newLabelType in self.masks:
            oldLabelType = int(os.path.basename(os.path.split(mask)[0]))
            if oldLabelType != newLabelType:
                dir = os.path.join(SCREENTONE_DIR, str(newLabelType))
                if not os.path.isdir(dir):
                    print("create folder:", dir)
                    os.mkdir(dir)
                newPath = os.path.join(dir, os.path.split(mask)[1])
                print("move", mask, "to", newPath)
                os.rename(mask, newPath)
                self.masks[idx] = (c, newPath, newLabelType)
            idx += 1

    def changeImg(self, idx):
        if idx < 0 or idx >= len(self.imgList):
            return
        self.imgIdx = idx
        self.loadAllImg(self.imgList[idx])

    def pressKey(self, event):
        if event.char >= '0'and event.char <= '9':
            self.changeMaskType(int(event.char))
        elif event.char == '+':
            self.addNewMaskType()
        elif event.char == 's' or event.char == 'S':
            self.save()
        elif event.char == 'a' or event.char == 'A':
            self.changeImg(self.imgIdx - 1)
        elif event.char == 'd' or event.char == 'D':
            self.changeImg(self.imgIdx + 1)
        

if __name__ == "__main__":
    window = ScWindow()