import streamlit as st
from PIL import Image, ImageOps, ImageFilter
import io

st.set_page_config(page_title="SmartSize", layout="centered")
st.title("📷 SmartSize – Intelligent Photo Resizer")
st.write("Resize your image to the ideal format with just one click.")

format_presets_by_region = {
    "Universal": {
        "LinkedIn Profile (400x400)": (400, 400),
        "LinkedIn Cover (1584x396)": (1584, 396),
        "Instagram Post (1080x1080)": (1080, 1080),
        "Instagram Story (1080x1920)": (1080, 1920),
        "YouTube Thumbnail (1280x720)": (1280, 720),
        "Presentation Slide (16:9)": (1280, 720),
        "Wallpaper (16:10)": (1920, 1200),
        "Profile (1:1)": (1000, 1000),
    },
    "Brazil": {
        "RG (Brasil - 700x1000)": (700, 1000),
        "CNH (Brasil - 1200x800)": (1200, 800),
    },
    "USA": {
        "Passport (US - 600x600)": (600, 600),
        "Driver License (US - 1280x800)": (1280, 800),
    },
    "Devices": {
        "iPhone 15 Pro Max": (1290, 2796),
        "iPad Pro 12.9\"": (2048, 2732),
        "Macbook Pro 16\"": (3456, 2234),
        "Galaxy S24 Ultra": (1440, 3120),
    },
    "Custom": {
        "Custom Size": None,
    }
}

region = st.selectbox("Choose format category", list(format_presets_by_region.keys()))
selected_format = st.selectbox("Choose the target use", list(format_presets_by_region[region].keys()))

if selected_format == "Custom Size":
    width = st.number_input("Target width (px)", min_value=100, max_value=4000, value=800)
    height = st.number_input("Target height (px)", min_value=100, max_value=4000, value=600)
else:
    width, height = format_presets_by_region[region][selected_format]

adjustment_mode = st.radio("Resize mode", ["With blurred background", "Crop proportionally (no background)"])

uploaded_file = st.file_uploader("Upload your image", type=["png", "jpg", "jpeg"])

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

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    target_size = (width, height)
    result = adjust_image(image, target_size, adjustment_mode)
    st.image(result, caption="Resized Image", use_column_width=True)

    buf = io.BytesIO()
    result.save(buf, format="PNG")
    byte_im = buf.getvalue()
    st.download_button(label="📥 Download image", data=byte_im, file_name="resized_image.png", mime="image/png")
