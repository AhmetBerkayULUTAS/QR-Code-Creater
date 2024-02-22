import qrcode
from tkinter import * 
from tkinter import filedialog
from PIL import Image,ImageTk
import os

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


def img_center_of_qr(img_path,qr):
    img=Image.open(img_path).convert("L")
    qr_size = qr.size[0]
    img.thumbnail((qr_size/4, qr_size/4))
    img_pos = ((qr_size-img.size[0]) // 2,(qr_size - img.size[1]) // 2)
    qr.paste(img,img_pos)


def save_and_show(qr,name):
    if not os.path.exists("./qrcodes"):
        os.makedirs("./qrcodes")

    qr.save(saved_path(name))
    
    qr_Image=ImageTk.PhotoImage(file=saved_path(name))
    ImageLabel.config(image=qr_Image)
    ImageLabel.image = qr_Image

    
def generate():
    global img_path, name

    name = str(TitleEntry.get()) 
    text = LinkEntry.get()
    qr=qrcode.make(text)
        
    if qr.size[0]>450:
       qr = qr.resize((450, 450))

    if img_path:
        img_center_of_qr(img_path,qr)

    save_and_show(qr,name)
    qr_color_changer(TRUE)
    img_path = ""


def qr_color_changer(_):

    r = int(slider_r.get())
    g = int(slider_g.get())
    b = int(slider_b.get())
    
    img_qr = Image.open(saved_path(name))
    
    img= img_qr.convert("RGB")
    width, height = img.size
    
    for x in range(width):
        for y in range(height):
            pixelr, pixelg, pixelb = img.getpixel((x, y))
            if pixelr != 255 and pixelg != 255 and pixelb != 255: 
                img.putpixel((x, y), (r, g, b))
    
    save_and_show(img,name)
    

def toggle_button():
    if check_var.get():
        Select_img_Button.config(state=NORMAL)  
    else:
        Select_img_Button.config(state=DISABLED) 


ImageLabel = Label(root,bg="#FFB266")
ImageLabel.pack(padx=20,pady=10,side=RIGHT)

slider_r = Scale(root, from_=0, to=250, orient="horizontal", label="QR Kırmızı", command=qr_color_changer)
slider_r.place(x=420, y=20)

slider_g = Scale(root, from_=0, to=250, orient="horizontal", label="QR Yeşil", command=qr_color_changer)
slider_g.place(x=420, y=75)

slider_b = Scale(root, from_=0, to=250, orient="horizontal", label="QR Mavi", command=qr_color_changer)
slider_b.place(x=420, y=130)

TitleLabel = Label(root,text="Title",bg="#FFB266",font="ariel 15 bold")
TitleLabel.place(x=50,y=180)

TitleEntry = Entry(root,width=15,font="arial 13")
TitleEntry.place(x=50,y=210)

LinkLabel =Label(root,text="Link",bg="#FFB266",font="ariel 15 bold")
LinkLabel.place(x=50,y=240)

LinkEntry=Entry(root,width=30,font="arial 13")
LinkEntry.place(x=50,y=270)

Select_img_Button=Button(root,text="Select Image",width=13,height=1,command=select_image)
Select_img_Button.place(x=50,y=300)
Select_img_Button.config(state=DISABLED) 

check_var = BooleanVar()
check_button = Checkbutton(root, text="with image", bg="#FFB266", variable=check_var, command=toggle_button)
check_button.place(x=150,y=300)

GeneratorButton=Button(root,text="Generate",width=25,height=3,bg="black",fg="white",command=generate)
GeneratorButton.place(x=50,y=330)

root.mainloop()