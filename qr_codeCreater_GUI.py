import qrcode
from tkinter import * 
from tkinter import filedialog
from PIL import Image,ImageTk
import os
import cv2
import numpy as np

root = Tk()
root.title("QR code Genetator")
root.geometry("1000x600")
root.config(bg="#FFB266")
root.resizable(False,False)

global img_path
img_path = ""
def select_image():
    global img_path
    img_path = filedialog.askopenfilename(title="Select an image file",filetypes=[("Image files", "*.jpg *.jpeg *.png")])

    
global name
name=""
def saved_path(name):
    qr_saved_path="./qrcodes/"+name+".png"
    return qr_saved_path


def img_center_of_qr(img_path):
    img = cv2.imread(img_path)
    qr = cv2.imread(saved_path(name))

    qr_height, qr_width, _ = qr.shape

    min_width = qr_width // 4
    min_height = qr_height // 4

    if img.shape[0] >= min_height and img.shape[1] >= min_width:
        img_resized = cv2.resize(img, (min_width, min_height))
    else:
        img_resized = img

    img_height, img_width, _ = img_resized.shape
    qr_height, qr_width, _ = qr.shape

    x_offset = (qr_width - img_width) // 2
    y_offset = (qr_height - img_height) // 2

    qr[y_offset:y_offset+img_height, x_offset:x_offset+img_width] = img_resized
    
    image_rgb = cv2.cvtColor(qr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)

    return pil_image


def bw_img_center_of_qr(img_path,qr):
    img=Image.open(img_path).convert("L")
    qr_size = qr.size[0]
    img.thumbnail((qr_size/4, qr_size/4))
    img_pos = ((qr_size-img.size[0]) // 2,(qr_size - img.size[1]) // 2)
    qr.paste(img,img_pos)
    return qr


def img_bg_of_qr(img_path,qr):########
    img = Image.open(img_path)
    return qr##########


def save_and_show(qr,name):
    if not os.path.exists("./qrcodes"):
        os.makedirs("./qrcodes")

    qr.save(saved_path(name))
    
    qr_Image=ImageTk.PhotoImage(file=saved_path(name))
    ImageLabel.config(image=qr_Image)
    ImageLabel.image = qr_Image

global mod_no
mod_no = 0    
def generate():
    global img_path, name,mod_no
    
    name = str(TitleEntry.get()) 
    text = LinkEntry.get()
    qr=qrcode.make(text)
    
    qr = qr.resize((450, 450))


    if img_path:

        if mod_no == 1:
            qr=bw_img_center_of_qr(img_path,qr)
            save_and_show(qr,name)
            qr_color_changer(TRUE)
        elif  mod_no== 2:
            save_and_show(qr,name)
            qr=img_center_of_qr(img_path)
            save_and_show(qr,name)
            
    save_and_show(qr,name)
    img_path = ""


def qr_color_changer(_):

    r = int(slider_r.get())
    g = int(slider_g.get())
    b = int(slider_b.get())
    
    img_qr = Image.open(saved_path(name))
    
    qr= img_qr.convert("RGB")
    width, height = qr.size
    
    for x in range(width):
        for y in range(height):
            pixelr, pixelg, pixelb = qr.getpixel((x, y))
            if pixelr != 255 and pixelg != 255 and pixelb != 255: 
                qr.putpixel((x, y), (r, g, b))
    
    save_and_show(qr,name)
    

def toggle_button(button_clicked):
    global mod_no
    
    if button_clicked == 1:

        Button1.place_forget()
        Button2.place_forget()
        Button3.place_forget()
        Button4.place_forget()
        ButtonBack.place(x=10,y=10)
        TitleLabel.place(x=50,y=180)
        TitleEntry.place(x=50,y=210)

        LinkLabel.place(x=50,y=240)
        LinkEntry.place(x=50,y=270)

        ImageLabel.place(x=500, y=75)

        GeneratorButton.place(x=50,y=300)

    elif button_clicked == 2:

        Button1.place_forget()
        Button2.place_forget()
        Button3.place_forget()
        Button4.place_forget()
        ButtonBack.place(x=10,y=10)
        TitleLabel.place(x=50,y=180)
        TitleEntry.place(x=50,y=210)

        LinkLabel.place(x=50,y=240)
        LinkEntry.place(x=50,y=270)

        slider_r.place(x=380, y=20)
        slider_g.place(x=380, y=75)
        slider_b.place(x=380, y=130)

        ImageLabel.place(x=500, y=75)

        GeneratorButton.place(x=50,y=300)

    elif button_clicked == 3:

        Button1.place_forget()
        Button2.place_forget()
        Button3.place_forget()
        Button4.place_forget()
        ButtonBack.place(x=10,y=10)
        TitleLabel.place(x=50,y=180)
        TitleEntry.place(x=50,y=210)

        LinkLabel.place(x=50,y=240)
        LinkEntry.place(x=50,y=270)

        Select_img_Button.place(x=50,y=300)

        ImageLabel.place(x=500, y=75)

        GeneratorButton.place(x=50,y=335)
        mod_no = 1

    elif button_clicked == 4:

        Button1.place_forget()
        Button2.place_forget()
        Button3.place_forget()
        Button4.place_forget()
        ButtonBack.place(x=10,y=10)
        TitleLabel.place(x=50,y=180)
        TitleEntry.place(x=50,y=210)

        LinkLabel.place(x=50,y=240)
        LinkEntry.place(x=50,y=270)

        Select_img_Button.place(x=50,y=300)

        ImageLabel.place(x=500, y=75)

        GeneratorButton.place(x=50,y=335)
        mod_no = 2

    elif button_clicked == 5:

        Button1.place(x=200, y=50)
        Button2.place(x=550, y=50)   
        Button3.place(x=200, y=300)
        Button4.place(x=550, y=300)
        ButtonBack.place_forget()
        TitleLabel.place_forget()
        TitleEntry.place_forget()

        LinkLabel.place_forget()
        LinkEntry.place_forget()

        Select_img_Button.place_forget()

        slider_r.place_forget()
        slider_g.place_forget()
        slider_b.place_forget()

        ImageLabel.place_forget()

        GeneratorButton.place_forget()



Button1 = Button(root, text="QR", width=20, height=10, font="ariel 12 bold", command= lambda: toggle_button(1))
Button1.place(x=200, y=50)

Button2 = Button(root, text="COLORFUL-QR", width=20, height=10, font="ariel 12 bold", command= lambda: toggle_button(2))
Button2.place(x=550, y=50)

Button3 = Button(root, text="BW-İMG-CENTER-OF-QR", width=20, height=10, font="ariel 12 bold", command= lambda: toggle_button(3))
Button3.place(x=200, y=300)

Button4 = Button(root, text="İMG-CENTER-OF-QR", width=20, height=10, font="ariel 12 bold", command= lambda: toggle_button(4))
Button4.place(x=550, y=300)


ButtonBack = Button(root, text="Back", width=10, height=1, font="ariel 12 bold", command= lambda: toggle_button(5))

ImageLabel = Label(root,bg="#FFB266")


slider_r = Scale(root, from_=0, to=250, orient="horizontal", label="QR Kırmızı", command=qr_color_changer)
slider_g = Scale(root, from_=0, to=250, orient="horizontal", label="QR Yeşil", command=qr_color_changer)
slider_b = Scale(root, from_=0, to=250, orient="horizontal", label="QR Mavi", command=qr_color_changer)

TitleLabel = Label(root,text="Title",bg="#FFB266",font="ariel 15 bold")

TitleEntry = Entry(root,width=15,font="arial 13")

LinkLabel =Label(root,text="Link",bg="#FFB266",font="ariel 15 bold")

LinkEntry=Entry(root,width=30,font="arial 13")

Select_img_Button=Button(root,text="Select Image",width=13,height=1,command=select_image)

GeneratorButton=Button(root,text="Generate",width=25,height=3,bg="black",fg="white",command= generate)

root.mainloop() 