from PIL import Image, ImageFont, ImageDraw
from sending_mails import send_email
import gdown
import pandas as pd
from barcode import Gs1_128
from barcode.writer import ImageWriter
import os
import sys

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller. """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Use resource_path to access id_format/SampleIDCard.png
image_path = resource_path("id_format/SampleIDCard.png")

# x and y signifies location of 'Name'
# (x, y) for the first detail (i.e name), x -> const, y -> changes
X, Y = 330, 158
# line spacing, to update y
DIS = 21

# To create a folder in desktop
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
folder_name = "GeneratedIDCards"
folder_path = os.path.join(desktop_path, folder_name)

if not os.path.exists(folder_path):
    try:
        os.mkdir(folder_path)
    except Exception as e:
        print(f"Failed to create directory: {e}")
        sys.exit(1)

# Func imp -> If Residential Address is too long, it will wrap to next line
def wrap(text):
    wrapped_text = ""
    line_length = 0
    for word in text.split():
        if line_length + len(word) + 1 > 60:
            wrapped_text += "\n"
            line_length = 0
        wrapped_text += word + " "
        line_length += len(word) + 1
    return wrapped_text

# To generate barcodes
def barcode_gen(barcode_num):
    try:
        my_code = Gs1_128(barcode_num, writer=ImageWriter())
        my_code.save("images/amazingBarcode")
    except Exception as e:
        print(f"Failed to generate barcode: {e}")

def pic_download(url, filename):
    try:
        url = url.replace("open", "uc")
        output_path = f"{filename}.jpg"
        gdown.download(url, output_path)
        return True
    except Exception as e:
        print(f"Can't download file: {e}")
        return False

def pic_to_place(img, pic_name, resize_tuple, loc_tuple, output_name, to_crop=False):
    try:
        if isinstance(img, str):
            img = Image.open(f"{folder_path}/{img}.png")

        dp = Image.open(f"{pic_name}")

        if to_crop:
            dp = dp.crop((10, 150, 300, 180))

        dp = dp.resize(resize_tuple)  # To fill into the size
        new_image = img.copy()  # So that it doesn't affect the real image
        new_image.paste(dp, loc_tuple)  # Pasting the dp on new_img(copy of img), at (30, 160)
        filepath = os.path.join(folder_path, f"{output_name}.png")
        new_image.save(filepath)
    except Exception as e:
        print(f"Failed to place picture: {e}")

def generate(csv_path, batch_year):
    font = ImageFont.truetype("DejaVuSans.ttf", 14)
    # font = ImageFont.truetype("arial.ttf", 14)
    
    try:
        data = pd.read_csv(csv_path)
        df = pd.DataFrame(data)
        df = df.iloc[:, 1:]
    except Exception as e:
        print(f"Failed to read CSV file: {e}")
        return "Failed to read CSV file"

    for i in range(len(df)):
        try:
            rank = str(df.iloc[i, 3])
            mail = str(df.iloc[i, 9])
            name=df.iloc[i, 0]
            year = batch_year
            output_name = f"{name}-{rank}"

            img = Image.open(image_path)
            editing = ImageDraw.Draw(img)
            for j in range(len(df.iloc[i])):
                if j <= 4:
                    editing.text((X, Y + DIS * j), wrap(str(df.iloc[i,j])), (0, 0, 0), font)
                elif j == 5:
                    editing.text((X, Y + DIS * j), year, (0,0,0), font)
                elif j <= 7:
                    editing.text((X, Y + DIS * j), wrap(str(df.iloc[i,j-1])), (0,0,0), font)
                else:
                    # Download and place profile picture
                    url = df.iloc[i, 7]
                    can_download_pic = pic_download(url, "images/dp")
                    if not can_download_pic:
                        print(f"Skipping email for {mail}: Profile picture download failed.")
                        continue

                    pic_to_place(img, "images/dp.jpg", (144, 153), (30, 160), output_name)

                    # Download and place signature
                    url = df.iloc[i, 8]
                    can_download_sig = pic_download(url, "images/signature")
                    if not can_download_sig:
                        print(f"Skipping email for {mail}: Signature download failed.")
                        continue

                    pic_to_place(output_name, "images/signature.jpg", (150, 30), (26, 352), output_name)

            # Generate barcode
            year = "".join(year.split("-"))
            barcode_num = "0" * (10 - (len(rank) + 4)) + f"{rank}{year}"
            barcode_gen(barcode_num)

            # Placing the barcode
            pic_to_place(output_name, "images/amazingBarcode.png", (220, 40), (262, 352), output_name, True)

            # Adding the barcode number
            img = Image.open(f"{folder_path}/{output_name}.png")
            editing = ImageDraw.Draw(img)
            editing.text((320, 395), barcode_num, (0, 0, 0), font)
            filepath = os.path.join(folder_path, f"{output_name}.png")
            img.save(filepath)

            # Send email
            send_email(receiver_email=mail, attachment_path=filepath)

        except Exception as e:
            print(f"Failed to process row {i}: {e}")

    return "Completed"
