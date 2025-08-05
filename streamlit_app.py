import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data
def load_database():
    try:
        # Загрузка данных с явным указанием типов
        df = pd.read_csv("hs_code_database.csv", dtype={'HS2': str, 'HS4': str, 'HS6': str, 'HS8': str, 'HS10': str})
        
        # Проверка структуры файла
        required_columns = {'HS2', 'HS4', 'HS6', 'HS8', 'HS10'}
        if not required_columns.issubset(df.columns):
            raise ValueError("Некорректная структура CSV файла")
            
        # Удаляем строки с пустыми значениями
        df = df.dropna(subset=['HS6', 'HS8', 'HS10'])
        
        # Создаем серии с уникальными кодами
        hs6_series = df['HS6'].drop_duplicates().reset_index(drop=True)
        hs8_series = df['HS8'].drop_duplicates().reset_index(drop=True)
        hs10_series = df['HS10'].drop_duplicates().reset_index(drop=True)
        
        return hs6_series, hs8_series, hs10_series
    
    except FileNotFoundError:
        st.error("Файл базы данных не найден!")
        st.stop()
    except Exception as e:
        st.error(f"Ошибка загрузки базы данных: {str(e)}")
        st.stop()

# Инициализация интерфейса
st.title("HS Code Transfiguration Tool - Расхлопушка версии 2.0")

# Загрузка данных
hs6_series, hs8_series, hs10_series = load_database()

# Добавление информационного текстового поля
st.markdown(f"""
<div style="background-color:#f0f2f6; padding:10px; border-radius:5px;">
    <p style="font-size:14px; color:#333; text-align:center;">
        Всего уникальных кодов:<br>
        6-значных: 7183 шт.<br>
        8-значных: 17118 шт.<br>
        10-значных: 24339 шт.<br>
        По отзывам работы программы и предложениям по её улучшению обращаться к Алексею Хаирову.
    </p>
</div>
""", unsafe_allow_html=True)

# Элементы GUI
input_codes = st.text_input("Введите коды ТН ВЭД через пробел (на 2-х, 4-х или 6-ти знаках):")
col1, col2, col3 = st.columns(3)

with col1:
    process_btn6 = st.button("Расхлопнуть до 6-ти знаков")
with col2:
    process_btn8 = st.button("Расхлопнуть до 8-ти знаков")
with col3:
    process_btn10 = st.button("Расхлопнуть до 10-ти знаков")

output_area = st.empty()

def process_codes(codes, target_series, valid_lengths, level):
    results = []
    errors = []
    
    for code in codes:
        # Валидация кода
        if not code.isdigit():
            errors.append(f"🚫 Некорректный код: {code} (содержит нецифровые символы)")
            continue
            
        code_len = len(code)
        if code_len not in valid_lengths:
            errors.append(f"🚫 Недопустимая длина кода для {level}-знаков: {code} ({code_len} цифр)")
            continue
            
        # Поиск по префиксу
        try:
            # Фильтрация по начальным символам
            matches = target_series[target_series.str.startswith(code, na=False)].tolist()
            
            if not matches:
                errors.append(f"🔍 Не найдено совпадений для: {code}")
            else:
                results.extend(matches)
        except Exception as e:
            errors.append(f"⚠️ Ошибка обработки кода {code}: {str(e)}")
    
    return results, errors

def display_results(results, errors, level):
    output = []
    if results:
        unique_results = sorted(set(results))  # Удаление дубликатов и сортировка
        output.append(f"✅ Из базы ФТС вытащено {len(unique_results)} кодов на {level}-ти знаках:")
        output.extend(unique_results)
        
    if errors:
        output.append("\n---\nСообщения об ошибках:")
        output.extend(errors)
    
    # Вывод результатов
    if output:
        output_area.text_area("Результат поиска", 
                            value="\n".join(output), 
                            height=400,
                            help="Скопируйте результаты с помощью Ctrl+C и вставьте в Excel для дальнейшей работы")
    else:
        output_area.warning("Нет данных для отображения")

# Обработка кнопок
if input_codes:
    codes = input_codes.strip().split()
    
    if process_btn6:
        results, errors = process_codes(codes, hs6_series, {2, 4}, 6)
        display_results(results, errors, 6)
        
    elif process_btn8:
        results, errors = process_codes(codes, hs8_series, {2, 4, 6}, 8)
        display_results(results, errors, 8)
        
    elif process_btn10:
        results, errors = process_codes(codes, hs10_series, {2, 4, 6, 8}, 10)
        display_results(results, errors, 10)
        
else:
    if process_btn6 or process_btn8 or process_btn10:
        output_area.warning("Пожалуйста, введите коды для поиска")
