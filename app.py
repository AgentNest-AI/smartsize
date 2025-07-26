import streamlit as st
from PIL import Image, ImageOps, ImageFilter
import io

st.set_page_config(page_title="SmartSize", layout="centered")
st.title("📷 SmartSize – Intelligent Photo Resizer")
st.write("Resize your image to the ideal format with just one click.")

# Available options
options = {
    "Wallpaper (16:10)": (1280, 800),
    "Profile (1:1)": (400, 400),
    "LinkedIn Profile Photo (400x400)": (400, 400),
    "LinkedIn Cover Photo (1584x396)": (1584, 396),
    "Passport (600x600)": (600, 600),
    "Presentation Slide (16:9)": (1280, 720),
    "Custom Size": None
}

# Upload
uploaded_file = st.file_uploader("Upload your image", type=["png", "jpg", "jpeg"])

# Format selection
target_label = st.selectbox("Choose the target use", list(options.keys()))

# Resize mode
adjustment_mode = st.radio("Resize mode", ["With blurred background", "Crop proportionally (no background)"])

custom_width, custom_height = None, None
if target_label == "Custom Size":
    custom_width = st.number_input("Target width (px)", min_value=100, max_value=4000, value=800)
    custom_height = st.number_input("Target height (px)", min_value=100, max_value=4000, value=600)

def adjust_image(image: Image.Image, size: tuple[int, int], mode: str) -> Image.Image:
    orig_w, orig_h = image.size
    target_w, target_h = size

    if mode == "Crop proportionally (no background)":
        ratio = max(target_w / orig_w, target_h / orig_h)
        new_size = (int(orig_w * ratio), int(orig_h * ratio))
        resized = image.resize(new_size, Image.Resampling.LANCZOS)
        left = (resized.width - target_w) // 2
        top = (resized.height - target_h) // 2
        right = left + target_w
        bottom = top + target_h
        cropped = resized.crop((left, top, right, bottom))
        return cropped

    else:
        background = image.copy().resize((target_w, target_h), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(20))
        ratio = min(target_w / orig_w, target_h / orig_h)
        new_w, new_h = int(orig_w * ratio), int(orig_h * ratio)
        resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        x_offset = (target_w - new_w) // 2
        y_offset = (target_h - new_h) // 2
        background.paste(resized, (x_offset, y_offset))
        return background

# Processing
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")

    if target_label == "Custom Size":
        target_size = (custom_width, custom_height)
    else:
        target_size = options[target_label]

    result = adjust_image(image, target_size, adjustment_mode)
    st.image(result, caption="Resized Image", use_column_width=True)

    buf = io.BytesIO()
    result.save(buf, format="PNG")
    byte_im = buf.getvalue()
    st.download_button(label="📥 Download image", data=byte_im, file_name="resized_image.png", mime="image/png")
