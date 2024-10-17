import streamlit as st
from streamlit_drawable_canvas import st_canvas
from rembg import remove
from PIL import Image, ImageDraw
import io

st.title("背景透過・トリミング＆手書き文字アプリ")

# 1. 画像アップロード
uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # アップロード画像の表示
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)

    # 2. 背景透過処理
    with st.spinner("背景を透過中..."):
        output_image = remove(image)

    st.image(output_image, caption="背景が透過された画像", use_column_width=True)

    # 3. 透過部分のトリミング
    def get_transparent_bounds(img):
        """透過部分の境界を取得する関数"""
        img = img.convert("RGBA")
        pixels = img.load()

        left, top = img.width, img.height
        right, bottom = 0, 0

        # 透明でないピクセルの範囲をスキャン
        for x in range(img.width):
            for y in range(img.height):
                _, _, _, alpha = pixels[x, y]
                if alpha != 0:  # 透明でないピクセルを検出
                    left = min(left, x)
                    top = min(top, y)
                    right = max(right, x)
                    bottom = max(bottom, y)

        return left, top, right, bottom

    # トリミング処理
    left, top, right, bottom = get_transparent_bounds(output_image)
    width = right - left
    height = bottom - top
    square_size = max(width, height)

    # 正方形の中央が透過領域の中央になるように調整
    center_x = (left + right) // 2
    center_y = (top + bottom) // 2
    left = max(0, center_x - square_size // 2)
    top = max(0, center_y - square_size // 2)
    right = min(output_image.width, left + square_size)
    bottom = min(output_image.height, top + square_size)

    # トリミング後の画像生成
    cropped_image = output_image.crop((left, top, right, bottom))
    st.image(cropped_image, caption="正方形にトリミングされた画像", use_column_width=True)

    # 4. 手書きキャンバス
    st.subheader("手書きで描画")
    canvas_width = min(600, cropped_image.width)  # スマホ用に幅を調整
    canvas_height = int(canvas_width * cropped_image.height / cropped_image.width)

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",  # 透明な背景
        stroke_width=5,  # ペンの太さ
        stroke_color="#000000",  # ペンの色（黒）
        background_image=cropped_image,  # 背景にトリミング後の画像をセット
        update_streamlit=True,
        height=canvas_height,
        width=canvas_width,
        drawing_mode="freedraw",  # 自由描画モード
        key="canvas"
    )

    # 5. 手書き追加後の画像処理
    if canvas_result.image_data is not None:
        drawn_image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')

        # 表示
        st.image(drawn_image, caption="手書きが追加された画像", use_column_width=True)

        # ダウンロードボタン
        buf = io.BytesIO()
        drawn_image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(
            label="手書き画像をダウンロード",
            data=byte_im,
            file_name="handwritten_image.png",
            mime="image/png"
        )
