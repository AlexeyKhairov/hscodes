import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data
def load_database():
    try:
        # Загрузка данных с явным указанием типов
        df = pd.read_csv("hs_code_database.csv", dtype={'HS2': str, 'HS4': str, 'HS6': str})
        
        # Проверка структуры файла
        if not {'HS2', 'HS4', 'HS6'}.issubset(df.columns):
            raise ValueError("Некорректная структура CSV файла")
            
        # Удаляем строки с пустыми значениями в HS6
        df = df.dropna(subset=['HS6'])
        
        # Убираем дубликаты и создаем серию с уникальными HS6 кодами
        hs6_series = df['HS6'].drop_duplicates().reset_index(drop=True)
        
        return hs6_series
    
    except FileNotFoundError:
        st.error("Файл базы данных не найден!")
        st.stop()
    except Exception as e:
        st.error(f"Ошибка загрузки базы данных: {str(e)}")
        st.stop()

# Инициализация интерфейса
st.title("HS Code Transfiguration Tool - Расхлопушка версии 1.0")

# Добавление информационного текстового поля
st.markdown("""
<div style="background-color:#f0f2f6; padding:10px; border-radius:5px;">
    <p style="font-size:14px; color:#333; text-align:center;">
        Всего кодов на 6-ти знаках - 7059 шт.
        По отзывам работы программы и предложениям по её улучшению обращаться к Алексею Хаирову.
    </p>
</div>
""", unsafe_allow_html=True)

hs6_series = load_database()

# Элементы GUI
input_codes = st.text_input("Введите коды ТН ВЭД через пробел (на 2-х и/или 4-х знаках):")
process_btn = st.button("Расхлопнуть до 6-ти знаков")
output_area = st.empty()

if process_btn and input_codes:
    codes = input_codes.strip().split()
    results = []
    errors = []
    for code in codes:
        # Валидация кода
        if not code.isdigit():
            errors.append(f"🚫 Некорректный код: {code} (содержит нецифровые символы)")
            continue
            
        code_len = len(code)
        if code_len not in {2, 4}:
            errors.append(f"🚫 Недопустимая длина кода: {code} ({code_len} цифр)")
            continue
            
        # Поиск по префиксу
        try:
            # Фильтрация по начальным символам
            matches = hs6_series[hs6_series.str.startswith(code, na=False)].tolist()
            
            if not matches:
                errors.append(f"🔍 Не найдено совпадений для: {code}")
            else:
                results.extend(matches)
        except Exception as e:
            errors.append(f"⚠️ Ошибка обработки кода {code}: {str(e)}")
    
    # Обработка результатов
    output = []
    if results:
        unique_results = sorted(set(results))  # Удаление дубликатов и сортировка
        output.append(f"✅ Из базы ФТС вытащено {len(unique_results)} кодов на 6-ти знаках:")
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
        
elif process_btn and not input_codes:
    output_area.warning("Пожалуйста, введите коды для поиска")