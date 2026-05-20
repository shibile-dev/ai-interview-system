from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from datetime import datetime

def generate_interview_report(
    candidate_name,
    question,
    answer,
    communication_score,
    technical_score,
    confidence_score,
    overall_score,
    emotion,
    evaluation_text
):
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    # Colors
    GOLD = HexColor('#FFB300')
    DARK = HexColor('#1A1535')
    PURPLE = HexColor('#9B59B6')
    LIGHT_GRAY = HexColor('#F5F5F5')
    DARK_GRAY = HexColor('#333333')
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=DARK,
        spaceAfter=5,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=PURPLE,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=DARK,
        spaceBefore=20,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=DARK_GRAY,
        spaceAfter=8,
        leading=16
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=PURPLE,
        fontName='Helvetica-Bold'
    )
    
    elements = []
    
    # HEADER
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("🤖 AI Interview System", title_style))
    elements.append(Paragraph("Interview Performance Report", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    elements.append(Spacer(1, 20))
    
    # CANDIDATE INFO
    elements.append(Paragraph("👤 Candidate Information", heading_style))
    
    info_data = [
        ['Candidate Name:', candidate_name],
        ['Report Date:', datetime.now().strftime("%B %d, %Y at %I:%M %p")],
        ['Emotional State:', emotion],
        ['Interview Status:', 'Completed ✓'],
    ]
    
    info_table = Table(info_data, colWidths=[150, 350])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_GRAY),
        ('TEXTCOLOR', (0, 0), (0, -1), PURPLE),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#DDDDDD')),
        ('ROUNDEDCORNERS', [5, 5, 5, 5]),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # SCORES
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#EEEEEE')))
    elements.append(Paragraph("📊 Performance Scores", heading_style))
    
    score_data = [
        ['Category', 'Score', 'Rating'],
        ['💬 Communication', f'{communication_score}/10', get_rating(communication_score)],
        ['⚙️ Technical Knowledge', f'{technical_score}/10', get_rating(technical_score)],
        ['💪 Confidence', f'{confidence_score}/10', get_rating(confidence_score)],
        ['⭐ Overall Score', f'{overall_score}/10', get_rating(overall_score)],
    ]
    
    score_table = Table(score_data, colWidths=[200, 100, 200])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#DDDDDD')),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, -1), (-1, -1), DARK),
        ('BACKGROUND', (0, -1), (-1, -1), HexColor('#FFF8E1')),
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 20))
    
    # QUESTION
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#EEEEEE')))
    elements.append(Paragraph("❓ Interview Question", heading_style))
    
    question_box = Table(
        [[Paragraph(question, body_style)]],
        colWidths=[500]
    )
    question_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#F3E5F5')),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('BOX', (0, 0), (-1, -1), 1, PURPLE),
    ]))
    elements.append(question_box)
    elements.append(Spacer(1, 15))
    
    # ANSWER
    elements.append(Paragraph("💬 Candidate Answer", heading_style))
    
    answer_box = Table(
        [[Paragraph(answer, body_style)]],
        colWidths=[500]
    )
    answer_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#FFF8E1')),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('BOX', (0, 0), (-1, -1), 1, GOLD),
    ]))
    elements.append(answer_box)
    elements.append(Spacer(1, 15))
    
    # AI FEEDBACK
    elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#EEEEEE')))
    elements.append(Paragraph("🧠 AI Evaluation & Feedback", heading_style))
    
    feedback_box = Table(
        [[Paragraph(evaluation_text, body_style)]],
        colWidths=[500]
    )
    feedback_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#E8F5E9')),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('ROUNDEDCORNERS', [8, 8, 8, 8]),
        ('BOX', (0, 0), (-1, -1), 1, HexColor('#4CAF50')),
    ]))
    elements.append(feedback_box)
    elements.append(Spacer(1, 30))
    
    # FOOTER
    elements.append(HRFlowable(width="100%", thickness=2, color=GOLD))
    elements.append(Spacer(1, 10))
    
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#888888'),
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph(
        f"Generated by AI Interview System | {datetime.now().strftime('%Y')} | Powered by Google Gemini AI",
        footer_style
    ))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def get_rating(score):
    if score >= 9:
        return "⭐ Excellent"
    elif score >= 7:
        return "✅ Good"
    elif score >= 5:
        return "📈 Average"
    else:
        return "⚠️ Needs Work"