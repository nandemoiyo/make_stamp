import streamlit as st
from streamlit_drawable_canvas import st_canvas
from rembg import remove
from PIL import Image, ImageDraw
import io

# セッション状態の初期化
if "drawn_image" not in st.session_state:
    st.session_state["drawn_image"] = None  # 手書き画像の初期化
if "final_image" not in st.session_state:
    st.session_state["final_image"] = None  # 合成後の画像の初期化

# アプリのタイトル
st.title("スタンプ作成アプリ")

# 1. 画像アップロード
uploaded_file = st.file_uploader(
    "背景を透過したい人物や物の画像をアップロードしてください", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)

    # 2. 背景透過処理
    with st.spinner("背景を透過中..."):
        output_image = remove(image)

    st.image(output_image, caption="背景が透過された画像", use_column_width=True)

    # 3. トリミング処理（ローディング表示）
    with st.spinner("トリミング中..."):
        def get_transparent_bounds(img):
            """透過部分の境界を取得する関数"""
            img = img.convert("RGBA")
            pixels = img.load()

            left, top = img.width, img.height
            right, bottom = 0, 0

            for x in range(img.width):
                for y in range(img.height):
                    _, _, _, alpha = pixels[x, y]
                    if alpha != 0:
                        left = min(left, x)
                        top = min(top, y)
                        right = max(right, x)
                        bottom = max(bottom, y)

            return left, top, right, bottom

        # トリミング後の画像生成
        left, top, right, bottom = get_transparent_bounds(output_image)
        square_size = max(right - left, bottom - top)

        center_x, center_y = (left + right) // 2, (top + bottom) // 2
        left = max(0, center_x - square_size // 2)
        top = max(0, center_y - square_size // 2)
        right = min(output_image.width, left + square_size)
        bottom = min(output_image.height, top + square_size)

        cropped_image = output_image.crop((left, top, right, bottom))

    st.image(cropped_image, caption="正方形にトリミングされた画像", use_column_width=True)

    # 4. 手書きキャンバスの設定 (横長4:1サイズ)
    st.subheader("手書きで描画")
    canvas_width = min(800, cropped_image.width)
    canvas_height = int(canvas_width / 4)

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=5,
        stroke_color="#000000",
        background_image=cropped_image,
        height=canvas_height,
        width=canvas_width,
        drawing_mode="freedraw",
        update_streamlit=False,
        key="canvas"
    )

    # 手書きの決定ボタン
    if st.button("手書きを適用"):
        if canvas_result.image_data is not None:
            drawn_image = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')
            st.session_state["drawn_image"] = drawn_image

            # トリミング画像と手書き画像を合成
            final_image = Image.alpha_composite(cropped_image.convert("RGBA"), drawn_image)
            st.session_state["final_image"] = final_image

    # 5. 位置調整用スライダー
    st.subheader("文字位置の調整")
    if st.session_state["final_image"] is not None:
        col1, col2 = st.columns(2)
        with col1:
            x_position = st.slider("左右の位置", 0, canvas_width, canvas_width // 2)
        with col2:
            y_position = st.slider("上下の位置", 0, canvas_height, canvas_height // 2)

        # 文字の追加
        draw = ImageDraw.Draw(st.session_state["final_image"])
        draw.text((x_position, y_position), "手書き文字", fill="black")

        # 最終画像の表示とダウンロード
        st.image(st.session_state["final_image"], caption="手書きが追加された画像", use_column_width=True)

        buf = io.BytesIO()
        st.session_state["final_image"].save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="手書き画像をダウンロード",
            data=byte_im,
            file_name="handwritten_image.png",
            mime="image/png"
        )
