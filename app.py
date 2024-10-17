import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw
import io

st.title("背景透過＆自動トリミングアプリ")

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)

    with st.spinner("背景を透過中..."):
        output_image = remove(image)

    st.image(output_image, caption="背景が透過された画像", use_column_width=True)

    # 透過部分を検出し、正方形で切り取る処理
    def get_transparent_bounds(img):
        """透過部分の境界を取得する"""
        img = img.convert("RGBA")
        pixels = img.load()

        left, top = img.width, img.height
        right, bottom = 0, 0

        for x in range(img.width):
            for y in range(img.height):
                _, _, _, alpha = pixels[x, y]
                if alpha != 0:  # 透明でないピクセルを検出
                    left = min(left, x)
                    top = min(top, y)
                    right = max(right, x)
                    bottom = max(bottom, y)

        return left, top, right, bottom

    # 透過領域の境界取得
    left, top, right, bottom = get_transparent_bounds(output_image)

    # 正方形にトリミングするための座標計算
    width = right - left
    height = bottom - top
    square_size = max(width, height)  # 正方形のサイズは幅・高さの大きい方に合わせる

    # 正方形の中央を画像の透過部分に合わせる
    center_x = (left + right) // 2
    center_y = (top + bottom) // 2

    # 正方形の切り取り範囲を計算
    left = max(0, center_x - square_size // 2)
    top = max(0, center_y - square_size // 2)
    right = min(output_image.width, left + square_size)
    bottom = min(output_image.height, top + square_size)

    # 正方形にトリミング
    cropped_image = output_image.crop((left, top, right, bottom))

    st.image(cropped_image, caption="正方形にトリミングされた画像", use_column_width=True)

    # 画像をダウンロードできるようにする
    buf = io.BytesIO()
    cropped_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    st.download_button(
        label="透過画像をダウンロード",
        data=byte_im,
        file_name="cropped_transparent_image.png",
        mime="image/png"
    )
