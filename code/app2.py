import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
import os
import matplotlib.font_manager as fm
import folium 
import matplotlib
import requests
import numpy as np

matplotlib.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False


st.set_page_config(
    page_title="지역 경제 및 생산성",
    page_icon="💵",
    layout="wide",
    initial_sidebar_state="expanded")

# 사이드바 설정
st.sidebar.title("소상공인 폐업률 분석(2)")
st.sidebar.markdown("### 지역 경제 및 생산성")

# 첫 번째 토글 (상위 메뉴)
with st.sidebar.expander("지역 내 총생산 Dataset"):
    st.write("https://data.seoul.go.kr/dataList/11063/S/2/datasetView.do")
    st.write("https://www.index.go.kr/unity/potal/main/EachDtlPageDetail.do?idx_cd=2736")
# 두 번째 토글 (상위 메뉴)
with st.sidebar.expander("국민 총소득 Dataset"):
    st.write("https://www.index.go.kr/unify/idx-info.do?idxCd=8086")
# 세 번째 토글 (상위 메뉴)
with st.sidebar.expander("구별 종사자 수 Dataset"):
    st.write("https://data.seoul.go.kr/dataList/10940/S/2/datasetView.do")

data = pd.read_csv("지역내총생산_pre.csv")


# Streamlit에서 열을 3개로 나누기
col = st.columns((1.5, 1.5,1.5), gap='medium')

with col[0]:
    st.subheader("GDP/1인당 GDP 비교")
    # 선택할 년도 설정 (2019, 2020, 2021)
    year_options = ['2019', '2020', '2021']
    selected_year = st.selectbox("년도 선택", year_options)

    # 선택한 년도의 '지역내총생산(백만원)'과 '1인당 지역내총생산(천원)' 데이터 추출
    gdp_column = f"{selected_year} 지역내총생산(백만원)"
    gdp_per_capita_column = f"{selected_year} 1인당 지역내총생산(천원)"

    # 지역별 데이터 준비
    regions = data['Unnamed: 0'].tolist()  # 'Unnamed: 0' 열의 지역명
    gdp_values = data[gdp_column].tolist()  # 해당 년도의 지역내총생산 값
    gdp_per_capita_values = data[gdp_per_capita_column].tolist()  # 1인당 지역내총생산 값

    # 데이터 전처리 (천 단위 콤마 제거 후 실수로 변환)
    gdp_values = [float(value.replace(',', '')) / 1_000_000 for value in gdp_values]  # 100만으로 나누기
    gdp_per_capita_values = [float(value.replace(',', '')) / 1_000 for value in gdp_per_capita_values]  # 천원으로 나누기

    # 레이더 차트 (단순화된 형태로 막대 그래프 사용)
    fig, ax = plt.subplots(figsize=(15, 9))  # 그래프 크기 줄이기

    # 지역내총생산 및 1인당 지역내총생산을 수평 막대그래프로 그리기
    bars_gdp_per_capita = ax.barh(regions, gdp_per_capita_values, color='red', alpha=0.6, label=f'{selected_year} 1인당 지역내총생산(천원)')
    bars_gdp = ax.barh(regions, gdp_values, color='blue', alpha=0.6, left=gdp_per_capita_values, label=f'{selected_year} 지역내총생산(백만원)')

    # 수치를 그래프 옆에 표시 (GDP와 1인당 GDP의 비율로 표시)
    for i, region in enumerate(regions):
        # 빨간색 막대 옆에 수치 표시
        ax.text(bars_gdp[i].get_width() + bars_gdp_per_capita[i].get_width() + 0.5, i,
                f'{gdp_values[i]:,.2f} / {gdp_per_capita_values[i]:,.2f}',
                va='center', color='black', fontsize=8)

    ax.set_xlabel("금액 (백만원)")
    ax.set_ylabel("지역")
    ax.set_title(f'{selected_year} 년 지역별 GDP 및 1인당 GDP')

    ax.legend(loc='upper right')
    st.pyplot(fig, use_container_width=True)



with col[0]:


    # 원형 그래프 (지역별 GDP 비율)
    # 각 지역의 GDP 합계로 비율을 계산
    total_gdp = sum(gdp_values)
    gdp_percentages = [value / total_gdp * 100 for value in gdp_values]

    fig_pie, ax_pie = plt.subplots(figsize=(8, 8))  # 그래프 크기 줄이기
    ax_pie.pie(gdp_percentages, labels=regions, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    ax_pie.set_title(f'{selected_year} 지역별 GDP 비율')
    st.pyplot(fig_pie, use_container_width=True)


location_data = pd.DataFrame({
    '지역': ['종로구', '중구', '용산구', '성동구', '광진구', '동대문구', '중랑구', '성북구', '강북구', '도봉구', '노원구', '은평구', 
            '서대문구', '마포구', '양천구', '강서구', '구로구', '금천구', '영등포구', '동작구', '관악구', '서초구', '강남구', '송파구', '강동구'],
    'lat': [37.5723, 37.5642, 37.5313, 37.5668, 37.5397, 37.5745, 37.5940, 37.5892, 37.6371, 37.6535, 37.6549, 37.6066, 
            37.5712, 37.5492, 37.5125, 37.5482, 37.4865, 37.4707, 37.5201, 37.5097, 37.4817, 37.4958, 37.4979, 37.5017, 37.5541],
    'lon': [126.9796, 126.9977, 126.9654, 127.0385, 127.0723, 127.0378, 127.0720, 127.0226, 127.0354, 127.0360, 127.0564, 126.9249, 
            126.9316, 126.9316, 126.8793, 126.8491, 126.8745, 126.8831, 126.9061, 126.9365, 126.9512, 127.0310, 127.0292, 127.1059, 127.1231]
})

# 예시로 사용된 데이터
df = pd.read_csv('./사업체종사자수_pre.csv')
df.columns = ['지역'] + list(df.columns[1:])

# 위도와 경도 데이터를 원본 데이터와 병합
df1 = pd.merge(df, location_data, on='지역')

# Folium 지도 생성
my_map = folium.Map(
    location=[df1['lat'].mean(), df1['lon'].mean()],
    zoom_start=12
)

# Streamlit UI 생성
with col[1]:
    st.subheader("종사자수/사업체수 비교")

    with st.expander('범례', expanded=True):
        st.write('''
            - :blue[**사업체수**]
            - :red[**종사자수**]
            ''')
        
    # 연도 선택
    selected_year = st.selectbox(
        "년도 선택",
        options=["2019", "2020", "2021", "2022"]  # 선택할 수 있는 연도 열
    )

    # 선택된 연도에 맞는 데이터로 'value' 열 설정
    df1['value'] = df1[selected_year + " 사업체수"].apply(lambda x: float(x.replace(',', '')))  # 사업체수 숫자로 변환
    df1['employee_value'] = df1[selected_year + " 종사자수"].apply(lambda x: float(x.replace(',', '')))  # 종사자수 숫자로 변환

    # 각 구의 위치에 원형 마커 추가 및 마커 표시
    for _, row in df1.iterrows():
        # 사업체수에 해당하는 파란 원형 마커 추가
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['value'] * 0.0010,  # 원 크기 조정 (값에 비례)
            color='blue',  # 원 테두리 색깔
            fill=True,
            fill_color='blue',  # 원 내부 색깔
            fill_opacity=0.1  # 원의 투명도 설정 (거의 투명하게)
        ).add_to(my_map)

        # 종사자수에 해당하는 빨간 원형 마커 추가
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=row['employee_value'] * 0.00005,  # 원 크기 조정 (값에 비례)
            color='red',  # 원 테두리 색깔
            fill=True,
            fill_color='red',  # 원 내부 색깔
            fill_opacity=0.1  # 원의 투명도 설정 (거의 투명하게)
        ).add_to(my_map)

        # 값 표시 마커 추가 (사업체수와 종사자수 모두 표시)
        folium.Marker(
            location=[row['lat'], row['lon']],
            icon=folium.DivIcon(html=f"""
                <div style="font-size: 12px; color: black; text-align: center; white-space: nowrap;">
                    <b>{row['지역']}<br>
                    사업체수: {round(row['value'], 2)}<br>
                    종사자수: {round(row['employee_value'], 2)}</b>
                </div>
            """)
        ).add_to(my_map)

    # 지도 렌더링
    st.components.v1.html(my_map._repr_html_(), width=1000, height=500)


with col[0]:
    # 데이터 입력
    years = [1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    income = [133, 136, 138, 149, 157, 165, 182, 196, 217, 242, 256, 273, 285, 321, 336, 345, 397, 445, 493, 523, 486, 505, 546, 614, 670, 708, 799, 910, 1021, 1100, 1192, 1310, 1375, 1460, 1581, 1702, 1798, 1853, 1699, 1868, 1972, 2034, 2197, 2244, 2331, 2383, 2465, 2592, 2582, 2633, 2808, 2832, 2900, 2998, 3083, 3260, 3391, 3493, 3532, 3532, 3530, 3657, 3639, 3703]

    # DataFrame 생성
    chart_data = pd.DataFrame({
        "Year": years,
        "Income": income
    })

    # Matplotlib로 차트 그리기
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(chart_data["Year"], chart_data["Income"], marker='o', color='b', label="1인당 실질 국민총소득")

    # x축에 10년 간격의 수치만 표시
    ax.set_xticks([year for year in years if year % 10 == 0])
    ax.set_xticklabels([str(year) for year in years if year % 10 == 0])
    
    # 제목과 레이블 설정
    ax.set_title("1인당 실질 국민총소득 (만 원)", fontsize=14)
    ax.set_xlabel("연도", fontsize=12)
    ax.set_ylabel("1인당 실질 국민총소득 (만 원)", fontsize=12)

    # grid 추가
    ax.grid(True)

    # 10년 간격의 데이터 포인트에 수치 표시
    for i, txt in enumerate(chart_data["Income"]):
        if chart_data["Year"][i] % 10 == 0:  # 10년 간격에만 표시
            ax.annotate(f'{txt}', (chart_data["Year"][i], chart_data["Income"][i]), textcoords="offset points", xytext=(0, 10), ha='center')

    # 차트 표시
    st.subheader("1인당 실질 국민총소득 (만 원)")
    st.pyplot(fig)
with col[2]:
    st.markdown("<div style='height: 800px;'></div>", unsafe_allow_html=True)
with col[2]:
    # CSV 데이터 불러오기
    data = pd.read_csv("사업체수_pre.csv", encoding='utf-8')

    # 열 이름 정리 (공백 제거)
    data.columns = data.columns.str.strip()

    # '구' 열을 인덱스로 설정
    data.set_index("구", inplace=True)

    # 쉼표 제거하고 숫자 형식으로 변환
    data = data.replace({',': ''}, regex=True).apply(pd.to_numeric)

    # 각 구별로 최대값에서 최소값을 뺀 차이 계산
    data_diff = data.max(axis=1) - data.min(axis=1)

    # 그래프 크기 설정
    plt.figure(figsize=(10, 6))

    # 막대차트 그리기
    plt.bar(data_diff.index, data_diff.values, color='blue')

    # 제목과 레이블 설정
    plt.title("구별 사업체 수 차이 (최대값 - 최소값) (2019-2022)", fontsize=14)
    plt.xlabel("구", fontsize=12)
    plt.ylabel("사업체 수 차이", fontsize=12)

    # x축 레이블 회전
    plt.xticks(rotation=90)

    # 그래프의 크기를 적당하게 설정
    plt.tight_layout()

    # Streamlit을 통해 차트 표시
    st.subheader("구별 사업체 수 차이")
    st.pyplot(plt)

with col[1]:
    # CSV 데이터 불러오기
    data = pd.read_csv("종사자수_pre.csv", encoding='utf-8')

    # 열 이름 정리 (공백 제거)
    data.columns = data.columns.str.strip()

    # '구' 열을 인덱스로 설정
    data.set_index("구", inplace=True)

    # 쉼표 제거하고 숫자 형식으로 변환
    data = data.replace({',': ''}, regex=True).apply(pd.to_numeric)

    # 각 구별로 최대값에서 최소값을 뺀 차이 계산
    data_diff = data.max(axis=1) - data.min(axis=1)

    # 그래프 크기 설정
    plt.figure(figsize=(10, 6))

    # 막대차트 그리기
    plt.bar(data_diff.index, data_diff.values, color='blue')

    # 제목과 레이블 설정
    plt.title("구별 종사자 수 차이 (최대값 - 최소값) (2019-2022)", fontsize=14)
    plt.xlabel("구", fontsize=12)
    plt.ylabel("종사자 수 차이", fontsize=12)

    # x축 레이블 회전
    plt.xticks(rotation=90)

    # 그래프의 크기를 적당하게 설정
    plt.tight_layout()

    # Streamlit을 통해 차트 표시
    st.subheader("구별 종사자 수 차이")
    st.pyplot(plt)