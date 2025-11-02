"""
공통 유틸리티 함수 모듈
점수 계산 및 등급 변환 등의 공통 기능을 제공합니다.
"""
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import sys

# 한글 폰트 등록
def _register_korean_fonts():
    """한글 폰트를 등록하는 함수"""
    try:
        regular_ttf = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'NotoSansKR-Regular.ttf')
        bold_ttf = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'NotoSansKR-Bold.ttf')
        pdfmetrics.registerFont(TTFont('NotoSansCJK', regular_ttf))
        pdfmetrics.registerFont(TTFont('NotoSansCJK-Bold', bold_ttf))
        print("한글 폰트 등록 성공")
        return True
    except Exception as e:
        print(f"한글 폰트 등록 실패: {e}")
        return False

# 폰트 등록 시도
_hangul_font_registered = _register_korean_fonts()

def calc_total_score(result_dict: dict) -> float:
    """
    품질 지표 딕셔너리에서 평균 점수를 계산합니다.
    
    Args:
        result_dict: 품질 지표 딕셔너리 (값은 0-1 범위의 float)
        
    Returns:
        float: 평균 품질 점수 (0-1)
    """
    if not result_dict:
        return 0.0
    
    scores = [float(score) for score in result_dict.values() if isinstance(score, (int, float))]
    
    if len(scores) == 0:
        return 0.0
    
    return sum(scores) / len(scores)

def get_grade(score: float) -> str:
    """
    품질 점수를 등급으로 변환합니다.
    
    Args:
        score: 품질 점수 (0-1)
        
    Returns:
        str: 품질 등급 (A, B, C, D)
    """
    if score >= 0.8:
        return "A"
    elif score >= 0.6:
        return "B"
    elif score >= 0.4:
        return "C"
    else:
        return "D"

def format_score(score: float, decimals: int = 3) -> str:
    """
    점수를 포맷팅하여 반환합니다.
    
    Args:
        score: 점수 (float)
        decimals: 소수점 자릿수
        
    Returns:
        str: 포맷팅된 점수 문자열
    """
    return f"{score:.{decimals}f}"

def get_grade_description(grade: str) -> str:
    """
    등급에 대한 설명을 반환합니다.
    
    Args:
        grade: 품질 등급 (A, B, C, D)
        
    Returns:
        str: 등급 설명
    """
    descriptions = {
        "A": "우수한 품질입니다. AI 학습에 바로 사용할 수 있습니다.",
        "B": "양호한 품질입니다. 일부 개선이 필요할 수 있습니다.",
        "C": "보통 품질입니다. 품질 개선이 권장됩니다.",
        "D": "품질 개선이 시급합니다. 데이터 정제가 필요합니다.",
    }
    return descriptions.get(grade, "알 수 없는 등급입니다.")

def _get_report_styles():
    """PDF 보고서용 스타일을 반환하는 함수"""
    styles = getSampleStyleSheet()
    
    # 한글 폰트가 등록되었는지 확인하고 적절한 폰트 선택
    font_name = 'NotoSansCJK' if _hangul_font_registered else 'Helvetica-Bold'
    normal_font = 'NotoSansCJK' if _hangul_font_registered else 'Helvetica'
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f4e79'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName=font_name
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2e75b6'),
        spaceAfter=12,
        fontName=font_name
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=normal_font,
        wordWrap='CJK' if _hangul_font_registered else 'LTR'
    )
    
    return title_style, heading_style, normal_style

def generate_text_report_pdf(text_scores: dict, total_score: float, grade: str, file_name: str = None) -> BytesIO:
    """
    텍스트 품질 분석 결과를 PDF 보고서로 생성합니다.
    
    Args:
        text_scores: 텍스트 품질 지표 딕셔너리
        total_score: 종합 품질 점수
        grade: 품질 등급
        file_name: 파일명 (없으면 현재 시간 사용)
        
    Returns:
        BytesIO: PDF 파일 바이너리 스트림
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # 스타일 정의
    title_style, heading_style, normal_style = _get_report_styles()
    
    # 헤더
    story.append(Paragraph("AI 학습용 비정형데이터 품질진단 리포트", title_style))
    story.append(Paragraph("텍스트 데이터 품질 분석 결과", heading_style))
    story.append(Spacer(1, 20))
    
    # 생성 날짜
    current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")
    story.append(Paragraph(f"<b>분석 일시:</b> {current_time}", normal_style))
    story.append(Spacer(1, 20))
    
    # 종합 점수 및 등급
    grade_colors = {
        "A": colors.green,
        "B": colors.blue,
        "C": colors.orange,
        "D": colors.red
    }
    
    summary_data = [
        ['종합 품질 점수', f"{total_score:.3f}"],
        ['품질 등급', f"{grade} 등급"],
        ['종합 평가', get_grade_description(grade)]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d9e2f3')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # 상세 지표
    story.append(Paragraph("상세 품질 지표", heading_style))
    
    metrics_data = [['지표', '점수', '설명']]
    for key, value in text_scores.items():
        # 간단한 설명 추가
        description_map = {
            "정확성(오탈자비율)": "오탈자 및 맞춤법 오류 검사",
            "중복도(유사도역비율)": "문장 간 유사도 분석",
            "완전성(문장충실도)": "의미 있는 문장의 비율"
        }
        desc = description_map.get(key, "품질 지표")
        metrics_data.append([key, f"{value:.3f}", desc])
    
    metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472c4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f8fb')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 30))
    
    # 품질 등급 기준 안내
    story.append(Paragraph("품질 등급 기준", heading_style))
    grade_standards = [
        ['등급', '점수 범위', '평가'],
        ['A', '0.8 이상', '우수 - AI 학습에 바로 사용 가능'],
        ['B', '0.6 ~ 0.8', '양호 - 일부 개선 필요'],
        ['C', '0.4 ~ 0.6', '보통 - 품질 개선 권장'],
        ['D', '0.4 미만', '개선 시급 - 데이터 정제 필요']
    ]
    
    grade_table = Table(grade_standards, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    grade_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472c4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f8fb')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(grade_table)
    story.append(Spacer(1, 30))
    
    # 하단 정보
    story.append(Spacer(1, 20))
    story.append(Paragraph("=" * 75, normal_style))
    story.append(Paragraph("본 보고서는 AI 학습용 비정형데이터 품질진단 프로그램으로 생성되었습니다.", 
                          ParagraphStyle('Footer', parent=normal_style, fontSize=9, alignment=TA_CENTER)))
    
    # PDF 생성
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_image_report_pdf(image_scores: dict, total_score: float, grade: str, file_name: str = None) -> BytesIO:
    """
    이미지 품질 분석 결과를 PDF 보고서로 생성합니다.
    
    Args:
        image_scores: 이미지 품질 지표 딕셔너리
        total_score: 종합 품질 점수
        grade: 품질 등급
        file_name: 파일명 (없으면 현재 시간 사용)
        
    Returns:
        BytesIO: PDF 파일 바이너리 스트림
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # 스타일 정의
    title_style, heading_style, normal_style = _get_report_styles()
    
    # 헤더
    story.append(Paragraph("AI 학습용 비정형데이터 품질진단 리포트", title_style))
    story.append(Paragraph("이미지 데이터 품질 분석 결과", heading_style))
    story.append(Spacer(1, 20))
    
    # 생성 날짜
    current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")
    story.append(Paragraph(f"<b>분석 일시:</b> {current_time}", normal_style))
    story.append(Spacer(1, 20))
    
    # 종합 점수 및 등급
    summary_data = [
        ['종합 품질 점수', f"{total_score:.3f}"],
        ['품질 등급', f"{grade} 등급"],
        ['종합 평가', get_grade_description(grade)]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d9e2f3')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # 상세 지표
    story.append(Paragraph("상세 품질 지표", heading_style))
    
    metrics_data = [['지표', '점수', '설명']]
    for key, value in image_scores.items():
        # 간단한 설명 추가
        description_map = {
            "해상도": "이미지 크기 기준 충족 여부",
            "선명도": "이미지 선명함 정도 (Laplacian Variance)",
            "노이즈": "이미지 노이즈 수준",
            "중복도": "중복 이미지 비율"
        }
        desc = description_map.get(key, "품질 지표")
        metrics_data.append([key, f"{value:.3f}", desc])
    
    metrics_table = Table(metrics_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472c4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f8fb')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 30))
    
    # 품질 등급 기준 안내
    story.append(Paragraph("품질 등급 기준", heading_style))
    grade_standards = [
        ['등급', '점수 범위', '평가'],
        ['A', '0.8 이상', '우수 - AI 학습에 바로 사용 가능'],
        ['B', '0.6 ~ 0.8', '양호 - 일부 개선 필요'],
        ['C', '0.4 ~ 0.6', '보통 - 품질 개선 권장'],
        ['D', '0.4 미만', '개선 시급 - 데이터 정제 필요']
    ]
    
    grade_table = Table(grade_standards, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    grade_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472c4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f8fb')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(grade_table)
    story.append(Spacer(1, 30))
    
    # 하단 정보
    story.append(Spacer(1, 20))
    story.append(Paragraph("=" * 80, normal_style))
    story.append(Paragraph("본 보고서는 AI 학습용 비정형데이터 품질진단 프로그램으로 생성되었습니다.", 
                          ParagraphStyle('Footer', parent=normal_style, fontSize=9, alignment=TA_CENTER)))
    
    # PDF 생성
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_dataset_report_pdf(results: dict, data_type: str, dataset_name: str = "데이터셋") -> BytesIO:
    """
    데이터셋 배치 분석 결과를 PDF 보고서로 생성합니다.
    
    Args:
        results: 데이터셋 분석 결과 딕셔너리
        data_type: 데이터 타입 ('이미지' 또는 '텍스트')
        dataset_name: 데이터셋 이름
        
    Returns:
        BytesIO: PDF 파일 바이너리 스트림
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # 스타일 정의
    title_style, heading_style, normal_style = _get_report_styles()
    
    # 헤더
    story.append(Paragraph("AI 학습용 비정형데이터 품질진단 리포트", title_style))
    story.append(Paragraph(f"{dataset_name} - {data_type} 데이터셋 배치 분석 결과", heading_style))
    story.append(Spacer(1, 20))
    
    # 생성 날짜
    current_time = datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S")
    story.append(Paragraph(f"<b>분석 일시:</b> {current_time}", normal_style))
    story.append(Paragraph(f"<b>데이터셋:</b> {dataset_name}", normal_style))
    story.append(Spacer(1, 20))
    
    # 종합 점수 및 등급
    avg_score = results.get("평균 종합 점수", 0.0)
    grade = get_grade(avg_score)
    
    summary_data = [
        ['평균 종합 점수', f"{avg_score:.3f}"],
        ['품질 등급', f"{grade} 등급"],
        ['종합 평가', get_grade_description(grade)]
    ]
    
    summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d9e2f3')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f4e79')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 30))
    
    # 상세 지표
    story.append(Paragraph("상세 품질 지표", heading_style))
    
    # 필터링: 종합 점수는 제외
    metrics_to_show = {k: v for k, v in results.items() if k != "평균 종합 점수"}
    
    metrics_data = [['지표', '평균값']]
    for key, value in metrics_to_show.items():
        if isinstance(value, (int, float)):
            metrics_data.append([key, f"{value:.3f}"])
        else:
            metrics_data.append([key, str(value)])
    
    metrics_table = Table(metrics_data, colWidths=[4*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472c4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f8fb')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 30))
    
    # 품질 등급 기준 안내
    story.append(Paragraph("품질 등급 기준", heading_style))
    grade_standards = [
        ['등급', '점수 범위', '평가'],
        ['A', '0.8 이상', '우수 - AI 학습에 바로 사용 가능'],
        ['B', '0.6 ~ 0.8', '양호 - 일부 개선 필요'],
        ['C', '0.4 ~ 0.6', '보통 - 품질 개선 권장'],
        ['D', '0.4 미만', '개선 시급 - 데이터 정제 필요']
    ]
    
    grade_table = Table(grade_standards, colWidths=[1.5*inch, 1.5*inch, 3*inch])
    grade_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472c4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'NotoSansCJK' if _hangul_font_registered else 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f8fb')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(grade_table)
    story.append(Spacer(1, 30))
    
    # 하단 정보
    story.append(Spacer(1, 20))
    story.append(Paragraph("=" * 80, normal_style))
    story.append(Paragraph("본 보고서는 AI 학습용 비정형데이터 품질진단 프로그램으로 생성되었습니다.", 
                          ParagraphStyle('Footer', parent=normal_style, fontSize=9, alignment=TA_CENTER)))
    
    # PDF 생성
    doc.build(story)
    buffer.seek(0)
    return buffer

