import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw, ImageFont
import io

# アプリのタイトル
st.title("スタンプ作成アプリ")

# 画像アップロードセクション
uploaded_file = st.file_uploader(
    "背景を透過したい人物や物の画像をアップロードしてください", type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # アップロードされた画像を開く
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)

    # 背景を透過する処理
    with st.spinner("背景を透過中..."):
        output_image = remove(image)

    st.image(output_image, caption="背景が透過された画像", use_column_width=True)

    # ユーザーからのテキスト入力
    text_input = st.text_input("スタンプに追加する文字を入力してください", value="サンプル文字")

    # 確定ボタン
    if st.button("確定"):
        center_x, center_y = output_image.width // 2, output_image.height // 2

        # デフォルトフォントを使用
        font = ImageFont.load_default()
        draw = ImageDraw.Draw(output_image)
        text_width, text_height = draw.textsize(text_input, font=font)

        # 中央に文字を描画
        draw.text(
            (center_x - text_width // 2, center_y - text_height // 2),
            text_input,
            font=font,
            fill="black"
        )

        # 画像を保存して表示
        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        byte_im = buf.getvalue()

        # JavaScriptでドラッグ可能にする
        st.markdown(
            f"""
            <div id="draggable" style="position: absolute; top: {center_y}px; left: {center_x}px; font-size: 24px; color: black; cursor: move;">
                {text_input}
            </div>

            <script>
            var dragItem = document.getElementById("draggable");
            var container = document.body;

            var active = false;
            var currentX, currentY, initialX, initialY;
            var xOffset = 0, yOffset = 0;

            container.addEventListener("touchstart", dragStart, false);
            container.addEventListener("touchend", dragEnd, false);
            container.addEventListener("touchmove", drag, false);

            container.addEventListener("mousedown", dragStart, false);
            container.addEventListener("mouseup", dragEnd, false);
            container.addEventListener("mousemove", drag, false);

            function dragStart(e) {{
                if (e.type === "touchstart") {{
                    initialX = e.touches[0].clientX - xOffset;
                    initialY = e.touches[0].clientY - yOffset;
                }} else {{
                    initialX = e.clientX - xOffset;
                    initialY = e.clientY - yOffset;
                }}

                if (e.target === dragItem) {{
                    active = true;
                }}
            }}

            function dragEnd() {{
                active = false;
            }}

            function drag(e) {{
                if (active) {{
                    e.preventDefault();

                    if (e.type === "touchmove") {{
                        currentX = e.touches[0].clientX - initialX;
                        currentY = e.touches[0].clientY - initialY;
                    }} else {{
                        currentX = e.clientX - initialX;
                        currentY = e.clientY - initialY;
                    }}

                    xOffset = currentX;
                    yOffset = currentY;

                    setTranslate(currentX, currentY, dragItem);
                }}
            }}

            function setTranslate(xPos, yPos, el) {{
                el.style.transform = "translate3d(" + xPos + "px, " + yPos + "px, 0)";
            }}
            </script>
            """,
            unsafe_allow_html=True
        )

        # ダウンロードボタンを表示
        st.download_button(
            label="画像をダウンロード",
            data=byte_im,
            file_name="stamped_image.png",
            mime="image/png"
        )
