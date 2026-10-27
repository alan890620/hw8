# 整合 Streamlit 與 Groq API 的多模態聊天室

這是一個基於 **Streamlit** 與 **Groq API** 所打造的智慧聊天室應用程式。除了基本的文字對話與上下文記憶功能外，還支援**圖片上傳與多模態（Multimodal）提示詞分析**，讓使用者能夠同時傳送圖片與文字讓 AI 進行解析。

---

## 🚀 主要特色

1. **Groq API 整合**：利用 Groq 高效能推論服務，快速回應使用者訊息。
2. **多模態圖文分析**：支援上傳圖片（JPG, JPEG, PNG），並與文字提示詞一同送給模型進行分析。
3. **對話歷程保留**：透過 Streamlit 的 `st.session_state` 支援連續對話與上下文記憶，並提供「新聊天」按鈕一鍵清除記錄。
4. **簡易金鑰管理**：支援從專案根目錄的 `api_key.txt` 自動讀取 API Key，亦提供側邊欄手動輸入的防呆設計。

---

## 📦 系統需求與安裝

請確保您的電腦已安裝 Python。在終端機（Terminal）中執行以下指令來安裝必要的相依套件：

```bash
pip install streamlit groq pillow