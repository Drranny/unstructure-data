"""
공통 UI 컴포넌트: CSS 스타일 및 사이드바
"""
import streamlit as st
import pandas as pd
import io
from PIL import Image, ImageDraw


def apply_custom_css():
    """블루/화이트 테마 CSS 적용"""
    st.markdown("""
    <style>
    /*전반적인블루/화이트테마*/
    .main{
    background-color: #FFFFFF;
    }

    /*제목스타일*/
    h1{
    color: #1f4e79;
    border-bottom: 3px solid#4472c4;
    padding-bottom: 10px;
    margin-bottom: 20px;
    }

    h2,h3{
    color: #2e75b6;
    }

    /*버튼스타일*/
    .stButton>button{
    background-color: #4472c4;
    color:white;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    font-weight: 500;
    }

    .stButton>button:hover{
    background-color: #2e75b6;
    }

    /*메트릭카드스타일*/
    [data-testid = "stMetricValue"]{
    color: #2e75b6;
    font-weight: bold;
    }

    /*테이블헤더스타일*/
    thead th{
    background-color: #d9e2f3;
    color: #1f4e79;
    }

    /*성공/정보메시지스타일*/
    .stSuccess{
    background-color: #d9e8f5;
    border-left: 4px solid#4472c4;
    }

    .stInfo{
    background-color: #e8f0f8;
    border-left: 4px solid#2e75b6;
    }

    /*경고메시지*/
    .stWarning{
    background-color: #fff4e6;
    border-left: 4px solid#ffa500;
    }

    /*탭스타일*/
    .stTabs[data-baseweb = "tab-list"]{
    gap: 8px;
    }

    .stTabs[data-baseweb = "tab"]{
    color: #2e75b6;
    border: 1px solid#d9e2f3;
    background-color: #f5f8fb;
    }

    .stTabs[aria-selected = "true"]{
    background-color: #4472c4;
    color:white;
    }

    /*파일업로더스타일*/
    .uploadedFile{
    background-color: #e8f0f8;
    border: 1px solid#d9e2f3;
    }
    </style>
    """, unsafe_allow_html=True)


def setup_sidebar():
    """사이드바에 샘플 데이터 테스트 옵션 추가"""
    with st.sidebar:
        st.header("빠른 테스트")
        st.markdown("샘플 데이터로 테스트해보세요!")
        
        st.markdown("**단일 파일 분석 샘플**")
        
        if st.button("📝 샘플 텍스트 분석", use_container_width=True):
            sample_text = """이것은 샘플 텍스트입니다. 
이 텍스트는 품질 진단 프로그램의 테스트를 위해 제공됩니다.
여러 문장이 포함되어 있어 다양한 품질 지표를 측정할 수 있습니다.
텍스트의 형식 정확성, 다양성, 완전성을 평가할 수 있습니다."""
            st.session_state['sample_text'] = sample_text
            st.session_state['use_sample_text'] = True
            st.success("샘플 텍스트가 준비되었습니다!")
            st.rerun()
        
        if st.button("🖼️ 샘플 이미지 분석", use_container_width=True):
            # 더 나은 샘플 이미지 생성 (그라데이션과 패턴 포함)
            # 512x512 RGB 이미지 생성
            sample_img = Image.new('RGB', (512, 512), color='lightblue')
            draw = ImageDraw.Draw(sample_img)
            
            # 그라데이션 효과 추가
            for i in range(512):
                color_value = int(135 + (120 * i / 512))  # lightblue에서 더 진한 파란색으로
                draw.line([(i, 0), (i, 512)], fill=(color_value, color_value, 255))
            
            # 중앙에 원 추가 (패턴 추가)
            center = (256, 256)
            radius = 100
            draw.ellipse([center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius], 
                        fill=(255, 255, 255), outline=(0, 0, 0), width=3)
            
            # 텍스트 추가 (선명도 테스트용)
            try:
                from PIL import ImageFont
                # 기본 폰트 사용
                font = ImageFont.load_default()
                draw.text((200, 240), "Sample", fill=(0, 0, 0), font=font)
            except:
                draw.text((200, 240), "Sample", fill=(0, 0, 0))
            
            st.session_state['sample_image'] = sample_img
            st.session_state['use_sample_image'] = True
            st.success("샘플 이미지가 준비되었습니다! (512x512, 그라데이션 + 패턴)")
            st.rerun()
        
        st.divider()
        st.markdown("**라벨링 기반 평가 샘플**")
        
        if st.button("샘플 라벨링 데이터 생성 (분류)"):
            # 분류 작업용 샘플 데이터 생성
            sample_data = {
                'prediction': ['positive', 'negative', 'positive', 'neutral', 'positive', 
                              'negative', 'positive', 'neutral', 'positive', 'negative',
                              'positive', 'negative', 'neutral', 'positive', 'negative'],
                'ground_truth': ['positive', 'negative', 'positive', 'positive', 'positive',
                                'negative', 'negative', 'neutral', 'positive', 'negative',
                                'positive', 'negative', 'neutral', 'positive', 'negative']
            }
            df_sample = pd.DataFrame(sample_data)
            
            # CSV로 변환하여 세션에 저장
            csv_buffer = io.StringIO()
            df_sample.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_buffer.seek(0)
            
            st.session_state['sample_labeling_data'] = {
                'dataframe': df_sample,
                'csv_buffer': csv_buffer.getvalue(),
                'task_type': 'classification',
                'prediction_col': 'prediction',
                'ground_truth_col': 'ground_truth'
            }
            st.success("샘플 라벨링 데이터를 생성했습니다! (분류 작업)")
        
        if st.button("샘플 라벨링 데이터 생성 (생성)"):
            # 텍스트 생성 작업용 샘플 데이터 생성
            sample_data = {
                'prediction': [
                    'The weather is nice today.',
                    'I love programming and coding.',
                    'Machine learning is fascinating.',
                    'Python is a great language.',
                    'Data science requires many skills.'
                ],
                'ground_truth': [
                    'The weather is beautiful today.',
                    'I enjoy programming and writing code.',
                    'Machine learning is very interesting.',
                    'Python is an excellent programming language.',
                    'Data science needs various technical skills.'
                ]
            }
            df_sample = pd.DataFrame(sample_data)
            
            # CSV로 변환하여 세션에 저장
            csv_buffer = io.StringIO()
            df_sample.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_buffer.seek(0)
            
            st.session_state['sample_labeling_data'] = {
                'dataframe': df_sample,
                'csv_buffer': csv_buffer.getvalue(),
                'task_type': 'generation',
                'prediction_col': 'prediction',
                'ground_truth_col': 'ground_truth'
            }
            st.success("샘플 라벨링 데이터를 생성했습니다! (텍스트 생성 작업)")

