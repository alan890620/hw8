import streamlit as st
from groq import Groq
import os
import io
import base64
from PIL import Image

# 設定網頁標題
st.title("Gork聊天室")
st.write("同時支援文字與圖片同時上傳並作為提示詞送出的聊天介面。")

# 1. 嘗試從根目錄的 api_key.txt 讀取 API Key
api_key_file = "api_key.txt"
groq_api_key = None

if os.path.exists(api_key_file):
    try:
        with open(api_key_file, "r", encoding="utf-8") as f:
            groq_api_key = f.read().strip()  # 讀取並去除前後空白與換行
    except Exception as e:
        st.error(f"讀取 {api_key_file} 時發生錯誤：{str(e)}")
else:
    st.warning(f"找不到 `{api_key_file}` 檔案，請確保它與此程式放在同一個資料夾下！")

# 如果檔案讀不到金鑰，提供側邊欄手動輸入作為備用防呆
if not groq_api_key:
    groq_api_key = st.sidebar.text_input("請手動輸入您的 Groq API Key", type="password")

# 檢查是否有成功取得金鑰
if not groq_api_key:
    st.info("請在專案根目錄建立 `api_key.txt` 並填入金鑰，或從側邊欄輸入後才能開始聊天。")
    st.stop()

# 初始化 Groq 客戶端
client = Groq(api_key=groq_api_key)

# 輔助函式：將圖片轉為 Base64 編碼
def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# 使用 Groq API 呼叫模型的函式
def call_groq_model(messages):
    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.8-27b",  # 支援多模態視覺與文字的模型
            messages=messages,
            temperature=0.7,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Groq API 錯誤: {str(e)}"

# 按鈕：建立新聊天（清除記錄）
if st.button("新聊天"):
    st.session_state.messages = []  # 清空聊天記錄
    st.rerun()

# 初始化聊天記錄狀態
if "messages" not in st.session_state:
    st.session_state.messages = []

# 顯示歷史聊天記錄
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        content = message["content"]
        if isinstance(content, list):
            for item in content:
                if item.get("type") == "text":
                    st.markdown(item["text"])
                elif item.get("type") == "image_url":
                    st.image(item["image_url"]["url"], caption="上傳的圖片", width=300)
        else:
            st.markdown(content)

# ==========================================
# 視覺化整合輸入區塊（將圖片上傳與文字框包在一起）
# ==========================================
with st.container():
    st.markdown("---")
    # 圖片上傳按鈕（緊鄰輸入區上方）
    uploaded_file = st.file_uploader("📎 點此附加圖片（選填，支援 jpg, jpeg, png）", type=["jpg", "jpeg", "png"])
    
    # 若有選取圖片，立即顯示縮圖預覽
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="準備發送的圖片預覽", width=120)

    # 聊天輸入框
    user_input = st.chat_input("請輸入您的訊息...")

# 當使用者送出訊息時
if user_input:
    # 判斷是否有夾帶圖片
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        base64_image = encode_image(image)
        
        # 建立多模態結構 (Text + Image URL)
        image_content_dict = {
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
        }
        
        # 畫面顯示使用者輸入（包含圖文）
        with st.chat_message("user"):
            st.markdown(user_input)
            st.image(image, caption="上傳的圖片", width=300)
            
        user_message_content = [
            {"type": "text", "text": user_input},
            image_content_dict
        ]
    else:
        # 純文字訊息
        with st.chat_message("user"):
            st.markdown(user_input)
        user_message_content = user_input

    # 紀錄至對話歷程
    st.session_state.messages.append({"role": "user", "content": user_message_content})
    
    # 準備傳送給 API 的完整對話記錄
    messages_to_send = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in st.session_state.messages
    ]
    
    # 呼叫 API 取得回應並顯示
    with st.chat_message("assistant"):
        with st.spinner("AI 正在分析您的訊息與圖片..."):
            ai_response = call_groq_model(messages_to_send)
            st.markdown(ai_response)
            
    # 將 AI 回應加入聊天記錄
    st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # 重新整理以清空當次上傳檔案，避免重複傳送
    st.rerun()