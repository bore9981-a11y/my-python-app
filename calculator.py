import streamlit as st

st.title("这是我的移动端 App")
st.write("如果你能看到这行字，说明封装已经彻底成功了！")
if st.button("点我庆祝一下"):
    st.balloons() # 屏幕会飘气球
