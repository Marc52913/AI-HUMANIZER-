import streamlit as st

st.set_page_config(
    page_title="AI Text Humanizer",
    page_icon="✍️"
)

st.title("AI Text Humanizer")
st.write("The website is working!")

text = st.text_area("Enter your text:")

if st.button("Process Text"):
    st.success("Text received!")
    st.write(text)
