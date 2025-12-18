from PIL import Image, ImageTk

_IMAGES = {}

def load_icon(key, path, size):
    if key in _IMAGES:
        return _IMAGES[key]
    
    img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(img)
    _IMAGES[key] = photo
    return photo
def load_all_icons():
    load_icon("eye_p", "icon/buttonImg/eyeP.png", (30, 30))
    load_icon("eye_s", "icon/buttonImg/eyeS.png", (30, 30))

    load_icon("hidden_p", "icon/buttonImg/hiddenP.png", (30, 30))
    load_icon("hidden_s", "icon/buttonImg/hiddenS.png", (30, 30))

    load_icon("edit_p", "icon/buttonImg/editP.png", (58, 58))
    load_icon("edit_s", "icon/buttonImg/editS.png", (58, 58))

    load_icon("bin_p", "icon/buttonImg/binP.png", (58, 58))
    load_icon("bin_s", "icon/buttonImg/binS.png", (58, 58))
def icon(name):
    return _IMAGES[name]
