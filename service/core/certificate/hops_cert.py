"""
Author: Nuriddin Muhammadjanov
Design & python implementation are both suggested & done by author
"""

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

font_bold = ImageFont.truetype('service/core/certificate/fonts/Montserrat-Bold.ttf', 56)
font_medium = ImageFont.truetype('service/core/certificate/fonts/Montserrat-Medium.otf', 40)

color_name = (83, 158, 254)
color_white = (255, 255, 255)


def create_certificate(first_name, last_name, degree, result, date):
    """
    first_name: STRING, MAX LENGTH = 20
    last_name: STRING, MAX LENGTH = 20
    degree: ENUM: A, B, C, D, E
    result: NUMBER
    date: STRING
    """

    img = Image.open(f"service/core/certificate/templates/{degree}.png")
    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Add first name
    draw.text((160, 417), first_name.upper(), font=font_bold, fill=color_name)

    # Add last name
    draw.text((160, 487), last_name.upper(), font=font_bold, fill=color_name)

    # Add result
    draw.text((160, 774), f"{result}%", font=font_medium, fill=color_white)

    # Add date
    draw.text((362, 774), date, font=font_medium, fill=color_white)

    # Save final image
    buffer = BytesIO()
    buffer.name = f"{first_name}-{last_name}-{degree}-{date}.png"
    img.save(buffer, format=img.format)

    return buffer, buffer.name
