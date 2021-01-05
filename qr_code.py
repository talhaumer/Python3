from qrcode import *

 


PNG = ".png"
FWD = "/"
BORDER = 1
BOX_SIZE = 5
QR_CODE_VER = 4
path = "/home/talha/Desktop"
identifier = "my name is talha"

 


def generate_qr_code(dir_path, identifier):
    qr = QRCode(version=QR_CODE_VER, error_correction=ERROR_CORRECT_H, box_size=BOX_SIZE, border=BORDER)
    qr.add_data(identifier)
    qr.make() # Generate the QRCode itself
    im = qr.make_image()
    im.save("".join([dir_path, FWD, identifier, PNG]))

 

 

generate_qr_code(path, identifier)