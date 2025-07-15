from PIL import Image, ImageEnhance, ImageOps
import numpy as np
from streamlit_drawable_canvas import st_canvas
import streamlit as st
from typing import Optional

def enhance_image(image: Image.Image) -> Image.Image:
    """Görüntüyü kontrast, siyah-beyaz ve otomatik kontrast ile iyileştirir."""
    if not isinstance(image, Image.Image):
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        else:
            raise ValueError("Desteklenmeyen görüntü formatı")
    image = ImageEnhance.Contrast(image).enhance(2.0)
    image = ImageOps.grayscale(image)
    image = ImageOps.autocontrast(image)
    return image

def show_canvas_and_crop(image: Image.Image, key: str = "canvas") -> Optional[Image.Image]:
    """
    Streamlit canvas ile kullanıcıya kutu çizdirir ve seçilen alanı kırpar.
    Seçili alan yoksa None döner.
    """
    if not isinstance(image, Image.Image):
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        else:
            raise ValueError("Desteklenmeyen görüntü formatı")
    if image.mode != "RGBA":
        image_rgba = image.convert("RGBA")
    else:
        image_rgba = image
    np_image = np.array(image_rgba)
    canvas_result = st_canvas(
        fill_color="rgba(255, 0, 0, 0.3)",
        stroke_width=2,
        background_image=np_image,  # type: ignore
        update_streamlit=True,
        height=image.height if image is not None and hasattr(image, 'height') else 400,
        width=image.width if image is not None and hasattr(image, 'width') else 600,
        drawing_mode="rect",
        key=key,
    )
    cropped = None
    if canvas_result.json_data and len(canvas_result.json_data["objects"]) > 0:
        obj = canvas_result.json_data["objects"][-1]
        left = int(obj["left"])
        top = int(obj["top"])
        width = int(obj["width"])
        height = int(obj["height"])
        cropped = image.crop((left, top, left + width, top + height))
        st.image(cropped, use_container_width=True)
    return cropped 