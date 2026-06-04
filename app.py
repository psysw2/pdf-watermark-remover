import streamlit as st
import fitz, re

st.set_page_config(page_title="PDF 去浮水印工具", page_icon="🧹")
st.title("🧹 PDF 去浮水印工具")
st.caption("針對「旋轉矩陣 + 文字裁剪填圖」型浮水印")

# 可自訂參數(預設就是你那份PDF的矩陣)
WM = st.text_input("浮水印旋轉矩陣特徵", "15.5564 15.5564 -15.5564 15.5564")
do_clip = st.checkbox("刪除文字裁剪(7 Tr)填色圖片", value=True)

uploaded = st.file_uploader("上傳 PDF", type="pdf")

# 診斷模式:先看看 BT 區塊長怎樣
if uploaded and st.button("🔍 診斷(列出文字區塊)"):
    doc = fitz.open(stream=uploaded.getvalue(), filetype="pdf")
    full = ""
    for xref in doc[0].get_contents():
        full += doc.xref_stream(xref).decode("latin-1")
    blocks = [m.group(0)[:120] for m in re.finditer(r"BT.{0,120}", full, flags=re.S)]
    st.code("\n---\n".join(blocks[:50]) or "(無)")

if uploaded and st.button("🚀 開始去水印", type="primary"):
    doc = fitz.open(stream=uploaded.getvalue(), filetype="pdf")
    for page in doc:
        for xref in page.get_contents():
            s = doc.xref_stream(xref).decode("latin-1")
            if do_clip:
                s = re.sub(
                    r"BT(?:(?!BT).)*?7 Tr(?:(?!BT).)*?/Im\d+\s+Do\s*Q",
                    " ", s, flags=re.S)
            def kill(m):
                return " " if WM in m.group(0) else m.group(0)
            s = re.sub(r"BT.*?ET", kill, s, flags=re.S)
            doc.update_stream(xref, s.encode("latin-1"))
    out = doc.tobytes(garbage=4, deflate=True, clean=True)
    st.success("完成!")
    st.download_button("⬇️ 下載去水印 PDF", out,
                       file_name="去水印.pdf", mime="application/pdf")
