import streamlit as st
import requests
import random
import json
from datetime import datetime

TIME_API_URL = "https://www.timeapi.io/api/Time/current/zone?timeZone=Asia/Ho_Chi_Minh"

def get_today_date():
    try:
        response = requests.get(TIME_API_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        return datetime.strptime(data["date"], "%m/%d/%Y").strftime("%Y-%m-%d")  # Chuyển về YYYY-MM-DD
    except requests.exceptions.RequestException:
        return datetime.now().strftime("%Y-%m-%d")  # Format giống file JSON


# Load dữ liệu món ăn từ file
def load_food_data():
    try:
        with open("food_data.json", "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"food_list": ["Cơm tấm", "Bún bò", "Phở", "Hủ tiếu", "Gà rán"], "history": {}}

# Lưu dữ liệu vào file
def save_food_data(data):
    with open("food_data.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

# Load dữ liệu
food_data = load_food_data()
today = get_today_date()
today_date = datetime.strptime(today, "%Y-%m-%d")

# Sidebar: Danh sách món ăn
st.sidebar.header("📝 Danh sách món ăn")

# Thêm món mới
new_food = st.sidebar.text_input("➕ Thêm món ăn mới")
if st.sidebar.button("Thêm món"):
    if new_food and new_food not in food_data["food_list"]:
        food_data["food_list"].append(new_food)
        save_food_data(food_data)
        st.sidebar.success(f"✅ Đã thêm món: {new_food}")
    else:
        st.sidebar.error("⚠️ Món ăn đã có hoặc trống!")

# Hiển thị danh sách món ăn
st.sidebar.write("🍛 **Danh sách món ăn hiện tại:**")
for food in food_data["food_list"]:
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(f"🍽 {food}")
    if col2.button("❌", key=food):
        food_data["food_list"].remove(food)
        save_food_data(food_data)
        st.rerun()

# Main content
st.title("🍽 Hôm Nay Ăn Gì?")
col1, col2, col3 = st.columns(3)
year = col1.number_input("Năm", min_value=2000, max_value=2100, value=today_date.year, step=1)
month = col2.selectbox("Tháng", list(range(1, 13)), index=today_date.month - 1)
day = col3.number_input("Ngày", min_value=1, max_value=31, value=today_date.day, step=1)

# Xác định ngày được chọn
selected_date = datetime(year, month, day)
selected_date_str = selected_date.strftime("%Y-%m-%d")

# Lịch sử món ăn
history = food_data.get("history", {})

if selected_date < today_date:
    st.subheader(f"📅 {selected_date_str}")
    if selected_date_str in history:
        st.write("🍜 Món ăn đã chọn:")
        for i, food in enumerate(history[selected_date_str]):
            st.write(f"✅ Lần {i+1}: {food}")
    else:
        st.write("🚫 Ngày này bạn chưa chọn món ăn nào.")
else:
    st.subheader(f"🎲 Chọn món cho ngày {selected_date_str}")
    remaining_spins = 5 - len(history.get(selected_date_str, []))

    if remaining_spins > 0:
        if st.button("🔄 Bấm vào đây để chọn món!"):
            chosen_food = random.choice(food_data["food_list"])
            history.setdefault(selected_date_str, []).append(chosen_food)
            save_food_data(food_data)
            st.success(f"🎉 Bạn đã chọn: {chosen_food}")
            remaining_spins -= 1
        st.write(f"🔢 Số lần quay còn lại: {remaining_spins}")
    else:
        st.warning("⚠️ Hết lượt quay trong ngày!")

    if selected_date_str in history:
        st.write("📜 Lịch sử món ăn hôm nay:")
        foods = history[selected_date_str]
        cols = st.columns(2)  # Chia thành 2 cột
        for i, food in enumerate(foods):
            with cols[i % 2]:  # Xen kẽ giữa 2 cột
                st.write(f"✅ Lần {i+1}: {food}")
                
                
# ====== Thêm phần Chat với trợ lý AI ======

st.subheader("💬 Trò chuyện với trợ lý AI")

# Khởi tạo lịch sử tin nhắn trong session_state nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử tin nhắn với giới hạn (chỉ hiện 10 tin nhắn gần nhất)
MAX_MESSAGES = 10
messages_to_show = st.session_state.messages[-MAX_MESSAGES:]

with st.container():
    chat_placeholder = st.container()
    with chat_placeholder:
        for msg in messages_to_show:
            st.chat_message(msg["role"]).write(msg["content"])

# Input gửi tin nhắn
user_input = st.text_input("Nhập tin nhắn", key="chat_input")

if st.button("Gửi"):
    if user_input:
        # Thêm tin nhắn của người dùng vào lịch sử
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Gửi tin nhắn đến OpenAI và nhận phản hồi
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages],
        )

        bot_reply = response["choices"][0]["message"]["content"]

        # Thêm phản hồi của AI vào lịch sử
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        # Cập nhật giao diện chat
        st.rerun()