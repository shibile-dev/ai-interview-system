import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_score_radar_chart(communication, technical, confidence, overall):
    categories = ['Communication', 'Technical', 'Confidence', 'Overall']
    values = [communication, technical, confidence, overall]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        line_color='#00D4FF',
        fillcolor='rgba(0, 212, 255, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        title="Performance Radar Chart",
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def create_emotion_pie_chart(emotions_list):
    emotion_counts = {}
    for emotion in emotions_list:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    fig = px.pie(
        values=list(emotion_counts.values()),
        names=list(emotion_counts.keys()),
        title="Emotion Distribution During Interview",
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def create_score_bar_chart(communication, technical, confidence, overall):
    categories = ['Communication', 'Technical', 'Confidence', 'Overall']
    values = [communication, technical, confidence, overall]
    colors = ['#00D4FF', '#FF6B6B', '#51CF66', '#FFD43B']
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f'{v}/10' for v in values],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Interview Score Breakdown",
        yaxis=dict(range=[0, 10]),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig