import streamlit as st
import pandas as pd
import random
import json
import os
import time
from datetime import datetime

st.set_page_config(page_title="Супер Тренажер Имрона", page_icon="🚀", layout="wide")

# --- СИСТЕМА СОХРАНЕНИЯ ДАННЫХ ИМРОНА (КОПИЛКА) ---
DATA_FILE = "imron_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"total_sum": 0, "history": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "imron" not in st.session_state:
    st.session_state.imron = load_data()

def log_result(task_name, result_text, earned_sum):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.imron["total_sum"] += earned_sum
    st.session_state.imron["history"].insert(0, {
        "Дата и Время": now,
        "Задание": task_name,
        "Результат": result_text,
        "Заработано": f"{earned_sum} сум"
    })
    save_data(st.session_state.imron)

# --- БАЗА СЛОВ И ГРАММАТИКИ ИЗ FAMILY AND FRIENDS 2 ---
WORDS = [
    {"en": "mum", "ru": "мама"}, {"en": "dad", "ru": "папа"}, {"en": "brother", "ru": "брат"},
    {"en": "sister", "ru": "сестра"}, {"en": "grandma", "ru": "бабушка"}, {"en": "grandpa", "ru": "дедушка"},
    {"en": "classroom", "ru": "класс"}, {"en": "table", "ru": "стол"}, {"en": "computer", "ru": "компьютер"},
    {"en": "peg", "ru": "вешалка"}, {"en": "pencil case", "ru": "пенал"}, {"en": "board", "ru": "доска"},
    {"en": "hot", "ru": "жарко"}, {"en": "cold", "ru": "холодно"}, {"en": "hungry", "ru": "голодный"},
    {"en": "thirsty", "ru": "хочу пить"}, {"en": "happy", "ru": "счастливый"}, {"en": "sad", "ru": "грустный"},
    {"en": "ride a bike", "ru": "кататься на велосипеде"}, {"en": "skate", "ru": "кататься на коньках"},
    {"en": "skateboard", "ru": "скейтборд"}, {"en": "play tennis", "ru": "играть в теннис"},
    {"en": "salad", "ru": "салат"}, {"en": "fries", "ru": "картофель фри"}, {"en": "pizza", "ru": "пицца"},
    {"en": "milkshake", "ru": "молочный коктейль"}, {"en": "cheese sandwich", "ru": "бутерброд с сыром"},
    {"en": "art", "ru": "рисование"}, {"en": "maths", "ru": "математика"}, {"en": "English", "ru": "английский"},
    {"en": "science", "ru": "окружающий мир"}, {"en": "PE", "ru": "физкультура"}, {"en": "music", "ru": "музыка"},
    {"en": "chocolate", "ru": "шоколад"}, {"en": "sweets", "ru": "сладости"}, {"en": "balloon", "ru": "воздушный шар"},
    {"en": "get up", "ru": "вставать"}, {"en": "have breakfast", "ru": "завтракать"}, {"en": "go to school", "ru": "идти в школу"},
    {"en": "hospital", "ru": "больница"}, {"en": "school", "ru": "школа"}, {"en": "airport", "ru": "аэропорт"},
    {"en": "sunny", "ru": "солнечно"}, {"en": "windy", "ru": "ветрено"}, {"en": "raining", "ru": "идет дождь"},
    {"en": "skirt", "ru": "юбка"}, {"en": "scarf", "ru": "шарф"}, {"en": "gloves", "ru": "перчатки"},
    {"en": "wedding", "ru": "свадьба"}, {"en": "guests", "ru": "гости"}, {"en": "cake", "ru": "торт"},
    {"en": "cow", "ru": "корова"}, {"en": "goat", "ru": "коза"}, {"en": "horse", "ru": "лошадь"},
    {"en": "was", "ru": "был(а)"}, {"en": "were", "ru": "были"}, {"en": "wasn't", "ru": "не был(а)"},
    {"en": "children", "ru": "дети"}, {"en": "men", "ru": "мужчины"}, {"en": "women", "ru": "женщины"}
]

# Грамматика теперь содержит правило (rule) для кнопки Помощи
GRAMMAR_TASKS = [
    {"task": "I [...] brown hair. (У меня каштановые волосы)", "answer": "'ve got", "rule": "Используй **'ve got** для I/we/they и **'s got** для he/she/it."},
    {"task": "He [...] green eyes. (У него зеленые глаза)", "answer": "'s got", "rule": "Используй **'ve got** для I/we/they и **'s got** для he/she/it."},
    {"task": "[...] is the new computer. (близко, ед.ч.)", "answer": "this", "rule": "This (это - ед.ч.), That (то - ед.ч.), These (эти - мн.ч.), Those (те - мн.ч.)."},
    {"task": "[...] are new tables. (близко, мн.ч.)", "answer": "these", "rule": "This (это - ед.ч.), That (то - ед.ч.), These (эти - мн.ч.), Those (те - мн.ч.)."},
    {"task": "Напишите сокращение для 'They are': [...]", "answer": "they're", "rule": "We're (Мы), They're (Они). Вопросы: Are they...?"},
    {"task": "He [...] ride a bike. (Умеет)", "answer": "can", "rule": "I can (умею), I can't (не умею)."},
    {"task": "He [...] ride a horse. (Не умеет)", "answer": "can't", "rule": "I can (умею), I can't (не умею)."},
    {"task": "Ответьте: Have you got a milkshake? Yes, I [...].", "answer": "have", "rule": "На вопрос Have you got...? отвечаем Yes, I have / No, I haven't."},
    {"task": "Ответьте: Has she got a pizza? No, she [...].", "answer": "hasn't", "rule": "На вопрос Has she got...? отвечаем Yes, she has / No, she hasn't."},
    {"task": "What have we got [...] Monday?", "answer": "on", "rule": "С днями недели всегда используй предлог **on** (on Monday)."},
    {"task": "These are [...] bags. (наши)", "answer": "our", "rule": "our (наш), their (их)."},
    {"task": "He [...] chocolate. (ему нравится)", "answer": "likes", "rule": "I like (мне нравится). He/She likes (ему/ей нравится)."},
    {"task": "He [...] like balloons. (ему не нравятся)", "answer": "doesn't", "rule": "I don't like. He/She doesn't like."},
    {"task": "[...] the time? (Который час?)", "answer": "what's", "rule": "Фраза для времени: What's the time?"},
    {"task": "Where [...] he work?", "answer": "does", "rule": "Where does he work? He works in a..."},
    {"task": "He [...] in a police station. (работает)", "answer": "works", "rule": "He works in a police station."},
    {"task": "What's the weather [...]?", "answer": "like", "rule": "Фраза о погоде: What's the weather like?"},
    {"task": "What [...] you wearing?", "answer": "are", "rule": "Вопрос: What are you wearing? Ответ: I'm wearing..."},
    {"task": "The sheep is [...] than the goat. (больше)", "answer": "bigger", "rule": "К коротким словам добавляй -er (big -> bigger, small -> smaller)."},
    {"task": "The boy is shorter [...] the girl. (чем)", "answer": "than", "rule": "При сравнении используй слово **than** (чем)."},
    {"task": "I [...] happy. (был)", "answer": "was", "rule": "I/he/she/it -> was (был). You/we/they -> were (были)."},
    {"task": "You [...] happy. (были)", "answer": "were", "rule": "I/he/she/it -> was (был). You/we/they -> were (были)."},
    {"task": "There weren't [...] men. (никаких)", "answer": "any", "rule": "В утверждениях: some. В отрицаниях: any."}
]

def text_to_speech(text):
    return f"""<button onclick="let u = new SpeechSynthesisUtterance('{text}'); u.lang = 'en-US'; window.speechSynthesis.speak(u);" style="background-color:#008CBA; color:white; padding:5px 10px; border:none; border-radius:5px; cursor:pointer;">🔊</button>"""

# --- ШАПКА ---
st.markdown("<h1 style='text-align: center; color: #1f3a93;'>🚀 Супер Тренажер Имрона</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #2ecc71;'>💰 Твоя Копилка: {st.session_state.imron['total_sum']} сум</h3>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗂 1. Учить слова", "✍️ 2. Упражнения", "🏃 3. Марафон Слов", "🧠 4. Марафон Грамматики", "🏦 5. Копилка"])

# --- РАЗДЕЛ 1: КАРТОЧКИ ---
with tab1:
    st.subheader("🗂 Тренировка слов по карточкам")
    if "card_idx" not in st.session_state:
        st.session_state.card_idx = 0
    if "card_flipped" not in st.session_state:
        st.session_state.card_flipped = False

    card = WORDS[st.session_state.card_idx]
    
    col_c1, col_c2, col_c3 = st.columns([1,2,1])
    with col_c2:
        word_show = card["ru"] if st.session_state.card_flipped else card["en"]
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e8bc3 0%, #3498db 100%); color: white; padding: 40px; border-radius: 15px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
            <h1 style="font-size: 48px; margin:0;">{word_show}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.card_flipped:
            st.components.v1.html(text_to_speech(card["en"]), height=40)
            
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("🔄 Перевернуть"):
                st.session_state.card_flipped = not st.session_state.card_flipped
                st.rerun()
        with c_btn2:
            if st.button("➡️ Следующее слово"):
                st.session_state.card_idx = random.randint(0, len(WORDS)-1)
                st.session_state.card_flipped = False
                st.rerun()

# --- РАЗДЕЛ 2: ПРАКТИКА С ПОДСКАЗКОЙ ---
with tab2:
    st.subheader("✍️ Укрепление грамматики (С подсказками)")
    if "prac_idx" not in st.session_state:
        st.session_state.prac_idx = random.randint(0, len(GRAMMAR_TASKS)-1)
    
    t = GRAMMAR_TASKS[st.session_state.prac_idx]
    
    with st.expander("💡 Помощь (Вспомнить правило)"):
        st.info(f"**Правило урока:** {t['rule']}")

    st.markdown(f"**Задание:** {t['task']}")
    ans = st.text_input("Впиши пропущенное слово:")
    
    if st.button("Проверить ответ"):
        if ans.strip().lower() == t["answer"].lower():
            st.success("✅ Молодец! Все верно.")
            st.session_state.prac_idx = random.randint(0, len(GRAMMAR_TASKS)-1)
        else:
            st.error(f"❌ Ошибка. Правильный ответ: **{t['answer']}**")

# --- РАЗДЕЛ 3: МАРАФОН СЛОВ ---
with tab3:
    st.subheader("🏃 Марафон: 25 слов за 5 минут")
    st.write("Награда за 25 из 25 правильных ответов: **5000 сум**. Одна ошибка — марафон провален!")
    
    if "wm_active" not in st.session_state:
        st.session_state.wm_active = False

    if not st.session_state.wm_active:
        if st.button("🚀 Начать Марафон Слов!"):
            st.session_state.wm_active = True
            st.session_state.wm_start = time.time()
            st.session_state.wm_questions = random.sample(WORDS, 25)
            st.rerun()
    else:
        elapsed = int(time.time() - st.session_state.wm_start)
        left = 300 - elapsed
        if left <= 0:
            st.error("⏰ Время вышло!")
            st.session_state.wm_active = False
            if st.button("Попробовать снова"): st.rerun()
        else:
            mins, secs = divmod(left, 60)
            st.warning(f"⏳ Осталось времени: **{mins:02d}:{secs:02d}**")
            
            with st.form("wm_form"):
                answers = []
                for i, q in enumerate(st.session_state.wm_questions):
                    ans = st.text_input(f"{i+1}. Как будет по-английски: **{q['ru']}**?", key=f"wm_{i}")
                    answers.append(ans)
                
                submitted = st.form_submit_button("🏁 Завершить марафон")
                if submitted:
                    errors = 0
                    for i, q in enumerate(st.session_state.wm_questions):
                        if answers[i].strip().lower() != q['en'].lower():
                            errors += 1
                            st.write(f"Ошибка в №{i+1}: Нужно было **{q['en']}** (написано: {answers[i]})")
                    
                    if errors == 0:
                        st.balloons()
                        st.success("🏆 ИДЕАЛЬНО! Ни одной ошибки! Выдана награда: 5000 сум.")
                        log_result("Марафон Слов (25/25)", "Пройден идеально", 5000)
                    else:
                        st.error(f"❌ Допущено ошибок: {errors}. Награда не выдана. Нужно 100% правильных ответов!")
                        log_result("Марафон Слов", f"Провален (Ошибок: {errors})", 0)
                    
                    st.session_state.wm_active = False

# --- РАЗДЕЛ 4: МАРАФОН ГРАММАТИКИ ---
with tab4:
    st.subheader("🧠 Марафон Грамматики: 20 вопросов за 7 минут")
    st.write("Награда за 20 из 20 правильных ответов: **10000 сум**. Только идеальный результат!")
    
    if "gm_active" not in st.session_state:
        st.session_state.gm_active = False

    if not st.session_state.gm_active:
        if st.button("🚀 Начать Марафон Грамматики!"):
            st.session_state.gm_active = True
            st.session_state.gm_start = time.time()
            q_pool = GRAMMAR_TASKS if len(GRAMMAR_TASKS) >= 20 else GRAMMAR_TASKS * 2
            st.session_state.gm_questions = random.sample(q_pool, 20)
            st.rerun()
    else:
        elapsed = int(time.time() - st.session_state.gm_start)
        left = 420 - elapsed
        if left <= 0:
            st.error("⏰ Время вышло!")
            st.session_state.gm_active = False
            if st.button("Попробовать снова"): st.rerun()
        else:
            mins, secs = divmod(left, 60)
            st.warning(f"⏳ Осталось времени: **{mins:02d}:{secs:02d}**")
            
            with st.form("gm_form"):
                answers = []
                for i, q in enumerate(st.session_state.gm_questions):
                    ans = st.text_input(f"{i+1}. {q['task']}", key=f"gm_{i}")
                    answers.append(ans)
                
                submitted = st.form_submit_button("🏁 Сдать работу")
                if submitted:
                    errors = 0
                    for i, q in enumerate(st.session_state.gm_questions):
                        if answers[i].strip().lower() != q['answer'].lower():
                            errors += 1
                            st.write(f"Ошибка в №{i+1}: Нужно было **{q['answer']}** (написано: {answers[i]})")
                    
                    if errors == 0:
                        st.balloons()
                        st.success("🏆 ГЕНИАЛЬНО! Вся грамматика верна! Выдана награда: 10000 сум.")
                        log_result("Марафон Грамматики (20/20)", "Пройден идеально", 10000)
                    else:
                        st.error(f"❌ Допущено ошибок: {errors}. Награда не выдана.")
                        log_result("Марафон Грамматики", f"Провален (Ошибок: {errors})", 0)
                    
                    st.session_state.gm_active = False

# --- РАЗДЕЛ 5: КОПИЛКА ---
with tab5:
    st.subheader("🏦 Копилка Имрона (Финансовый отчет)")
    st.markdown(f"### Всего заработано: **{st.session_state.imron['total_sum']} сум**")
    
    if st.session_state.imron["history"]:
        df = pd.DataFrame(st.session_state.imron["history"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Тут пока пусто. Пройди марафон, чтобы заработать первые деньги!")
