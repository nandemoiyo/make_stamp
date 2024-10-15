import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import io
import os

st.title("背景透過＆文字スタンプアプリ")

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)

    with st.spinner("背景を透過中..."):
        output_image = remove(image)

    st.image(output_image, caption="背景が透過された画像", use_column_width=True)

    st.subheader("文字スタンプを追加")
    custom_text = st.text_input("任意の文字列を入力", "ありがとう")

    st.subheader("文字の設定")

    col1, col2 = st.columns(2)
    with col1:
        x_position = st.slider("左右", 0, output_image.width, output_image.width // 2)
    with col2:
        y_position = st.slider("上下", 0, output_image.height, output_image.height // 2)

    col3, col4 = st.columns(2)
    with col3:
        font_size = st.slider("フォントサイズ", 10, 100, 50)
    with col4:
        angle = st.slider("角度", -180, 180, 0)

    font_color = st.color_picker("フォントカラー", "#000000")

    font_paths = [
        "C:/Windows/Fonts/meiryob.ttc",
        "C:/Windows/Fonts/yugothb.ttc",
    ]
    selected_font_path = st.selectbox("フォントを選択", font_paths)

    try:
        font = ImageFont.truetype(selected_font_path, font_size)
    except IOError:
        st.error(f"フォントファイルが見つかりません: {selected_font_path}")
        st.stop()

    draw = ImageDraw.Draw(output_image)

    rotated_text = Image.new('RGBA', (font_size * len(custom_text) * 2, font_size * 2))
    draw_rotated = ImageDraw.Draw(rotated_text)
    draw_rotated.text((0, 0), custom_text, font=font, fill=font_color)
    rotated_text = rotated_text.rotate(angle, expand=True, resample=Image.BICUBIC)

    text_width, text_height = rotated_text.size
    paste_x = x_position - text_width // 2
    paste_y = y_position - text_height // 2
    output_image.paste(rotated_text, (paste_x, paste_y), rotated_text)


    st.image(output_image, caption="文字が追加された画像", use_column_width=True)

    st.subheader("トリミング")

    # トリミング方法の選択
    trim_method = st.radio("トリミング方法", ("正方形", "上下左右"))

    if trim_method == "正方形":
        square_size = st.slider("正方形のサイズ", 0, min(output_image.width, output_image.height), min(output_image.width, output_image.height))
        center_x = output_image.width // 2
        center_y = output_image.height // 2
        left = center_x - square_size // 2
        top = center_y - square_size // 2
        right = center_x + square_size // 2
        bottom = center_y + square_size // 2
        cropped_image = output_image.crop((left, top, right, bottom))

    elif trim_method == "上下左右":
        left = st.number_input("左", min_value=0, max_value=output_image.width, value=0)
        top = st.number_input("上", min_value=0, max_value=output_image.height, value=0)
        right = st.number_input("右", min_value=0, max_value=output_image.width, value=output_image.width)
        bottom = st.number_input("下", min_value=0, max_value=output_image.height, value=output_image.height)
        cropped_image = output_image.crop((left, top, right, bottom))


    st.image(cropped_image, caption="トリミング後の画像", use_column_width=True)

    buf = io.BytesIO()
    cropped_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    st.download_button(
        label="透過画像をダウンロード",
        data=byte_im,
        file_name="transparent_image_with_text.png",
        mime="image/png"
    )
