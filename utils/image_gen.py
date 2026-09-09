from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

def generate_start_image(pfp_path, user_name, output_path="start_img.jpg"):
    try:
        bg = Image.open("template.jpg").convert("RGBA")
    except FileNotFoundError:
        bg = Image.new("RGBA", (800, 800), (139, 0, 0, 255))
        draw = ImageDraw.Draw(bg)
        draw.rectangle([50, 50, 750, 750], outline="red", width=10)

    if pfp_path and os.path.exists(pfp_path):
        pfp = Image.open(pfp_path).convert("RGBA")
        pfp = pfp.resize((350, 350))
        mask = Image.new("L", (350, 350), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 350, 350), fill=255)
        pfp_circle = ImageOps.fit(pfp, mask.size, centering=(0.5, 0.5))
        pfp_circle.putalpha(mask)
        bg.paste(pfp_circle, (225, 100), pfp_circle)

    draw = ImageDraw.Draw(bg)
    try:
        font = ImageFont.truetype("graffiti.ttf", 90) 
    except IOError:
        font = ImageFont.load_default()

    display_name = user_name[:12].upper()
    draw.text((200, 480), display_name, fill="white", font=font, stroke_width=4, stroke_fill="red")
    
    try:
        font_small = ImageFont.truetype("graffiti.ttf", 40)
    except IOError:
        font_small = ImageFont.load_default()
    draw.text((150, 600), "WELCOME TO THE CLUB!", fill="white", font=font_small, stroke_width=2, stroke_fill="black")

    bg = bg.convert("RGB")
    bg.save(output_path)
    return output_path
