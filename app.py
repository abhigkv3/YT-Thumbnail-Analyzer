import streamlit as st
from groq import Groq
import plotly.graph_objects as go
import base64
from PIL import Image
from io import BytesIO
import os

# Page config
st.set_page_config(
    page_title="YT Thumbnail Analyzer",
    page_icon="🎬",
    layout="wide"
)

# ── Branding ───────────────────────────────
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown(
        """
        <div style='background: linear-gradient(135deg, #FF0000, #FF6B6B);
                    border-radius: 12px;
                    padding: 10px;
                    text-align: center;
                    margin-top: 8px;'>
            <span style='font-size: 28px;'>🎬</span><br>
            <span style='color: white; font-size: 10px; font-weight: bold;'>AS</span>
        </div>
        """,
        unsafe_allow_html=True
    )
with col_title:
    st.title("YouTube Thumbnail Analyzer")
    st.markdown(
        "<p style='color: gray; font-size: 13px; margin-top: -10px;'>"
        "Developed by <b>Abhishek Singh</b> | "
        "Business Analyst & GenAI Enthusiast</p>",
        unsafe_allow_html=True
    )

st.markdown("---")

# ── Sidebar ────────────────────────────────
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    groq_api_key = st.sidebar.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_..."
    )

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 What I Analyze:")
st.sidebar.markdown("""
- 🎨 **Colors** — Eye-catching hai?
- 😊 **Faces** — Emotion clear hai?
- 📝 **Text** — Readable hai?
- 🎯 **CTR Score** — Click worthy?
- 💡 **Improvements** — Kya better kar sakte hain?
""")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='text-align:center; color: gray; font-size: 12px;'>"
    "Built by <b>Abhishek Singh</b><br>"
    "Business Analyst & GenAI Enthusiast"
    "</div>",
    unsafe_allow_html=True
)

# ── Functions ──────────────────────────────

def image_to_base64(image):
    """Image ko base64 mein convert karo"""
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def analyze_thumbnail(image, video_title, channel_niche, groq_api_key):
    """Groq Vision se thumbnail analyze karo"""
    client = Groq(api_key=groq_api_key)

    # Image to base64
    img_base64 = image_to_base64(image)

    prompt = f"""You are an expert YouTube thumbnail analyzer with deep knowledge of what makes thumbnails go viral.

Analyze this YouTube thumbnail for the video titled: "{video_title}"
Channel Niche: {channel_niche}

Provide a detailed analysis in this EXACT format:

## Overall CTR Score: X/10

## Color Analysis
[Analyze colors - are they bright, contrasting, eye-catching?]

## Face & Emotion Analysis  
[Are there faces? What emotion? Does it create curiosity?]

## Text Analysis
[Is text readable? Font size? Message clear?]

## Composition Analysis
[Layout, focal point, visual hierarchy]

## Strengths 💪
- [Strength 1]
- [Strength 2]
- [Strength 3]

## Improvements Needed 🔧
- [Improvement 1]
- [Improvement 2]
- [Improvement 3]

## Predicted Performance
- CTR Score: X/10
- Viral Potential: Low/Medium/High
- Target Audience Appeal: X/10
- Mobile Visibility: X/10

## Final Verdict
[2-3 lines summary]"""

    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ],
        max_tokens=1500
    )

    return response.choices[0].message.content


def extract_scores(analysis_text):
    """Analysis se scores extract karo"""
    scores = {
        "CTR Score": 7,
        "Viral Potential": 6,
        "Audience Appeal": 7,
        "Mobile Visibility": 7
    }

    lines = analysis_text.lower().split('\n')
    for line in lines:
        if 'ctr score:' in line:
            try:
                score = int(''.join(filter(str.isdigit, line.split('ctr score:')[1][:5])))
                if 1 <= score <= 10:
                    scores["CTR Score"] = score
            except:
                pass
        elif 'audience appeal:' in line:
            try:
                score = int(''.join(filter(str.isdigit, line.split('appeal:')[1][:5])))
                if 1 <= score <= 10:
                    scores["Audience Appeal"] = score
            except:
                pass
        elif 'mobile visibility:' in line:
            try:
                score = int(''.join(filter(str.isdigit, line.split('visibility:')[1][:5])))
                if 1 <= score <= 10:
                    scores["Mobile Visibility"] = score
            except:
                pass

    return scores


def create_radar_chart(scores):
    """Radar chart banao scores ke liye"""
    categories = list(scores.keys())
    values = list(scores.values())
    values.append(values[0])  # Close the radar
    categories.append(categories[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(255, 0, 0, 0.2)',
        line=dict(color='#FF0000', width=2),
        name='Thumbnail Score'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False,
        title="Thumbnail Performance Radar",
        height=400
    )
    return fig


def create_gauge(score):
    """CTR Score gauge banao"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "CTR Score", 'font': {'size': 20}},
        gauge={
            'axis': {'range': [0, 10]},
            'bar': {'color': "#FF0000"},
            'steps': [
                {'range': [0, 4], 'color': "#FFE0E0"},
                {'range': [4, 7], 'color': "#FFFF99"},
                {'range': [7, 10], 'color': "#E0FFE0"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(height=300)
    return fig


# ── Main App ───────────────────────────────

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Thumbnail Upload karo")

    uploaded_file = st.file_uploader(
        "Thumbnail image choose karo",
        type=["jpg", "jpeg", "png", "webp"]
    )

    video_title = st.text_input(
        "Video Title (optional)",
        placeholder="e.g. Excel VLOOKUP Tutorial for Beginners"
    )

    channel_niche = st.selectbox(
        "Channel Niche:",
        [
            "Education/Tutorial",
            "Entertainment",
            "Gaming",
            "Tech/Software",
            "Finance/Business",
            "Health/Fitness",
            "Food/Cooking",
            "Travel",
            "News/Politics",
            "Other"
        ]
    )

    analyze_btn = st.button("🔍 Analyze Karo!", type="primary")

with col2:
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.subheader("👁️ Tumhara Thumbnail:")
        st.image(image, use_column_width=True)

        # Image info
        width, height = image.size
        st.caption(f"Size: {width}x{height}px | Format: {uploaded_file.type}")

# ── Analysis ───────────────────────────────
if analyze_btn:
    if not groq_api_key:
        st.error("Groq API Key daalo!")
    elif not uploaded_file:
        st.error("Thumbnail upload karo!")
    else:
        with st.spinner("🤖 AI thumbnail analyze kar raha hai..."):
            try:
                image = Image.open(uploaded_file)

                # RGB convert karo
                if image.mode != "RGB":
                    image = image.convert("RGB")

                analysis = analyze_thumbnail(
                    image,
                    video_title or "YouTube Video",
                    channel_niche,
                    groq_api_key
                )

                st.success("✅ Analysis complete!")
                st.markdown("---")

                # Scores extract karo
                scores = extract_scores(analysis)

                # Dashboard
                st.markdown("## 📊 Analysis Dashboard")

                # Gauge + Radar
                col1, col2 = st.columns(2)
                with col1:
                    fig_gauge = create_gauge(scores["CTR Score"])
                    st.plotly_chart(fig_gauge, use_container_width=True)
                with col2:
                    fig_radar = create_radar_chart(scores)
                    st.plotly_chart(fig_radar, use_container_width=True)

                # Detailed Analysis
                st.markdown("---")
                st.markdown("## 📝 Detailed Analysis")
                st.markdown(analysis)

                # Footer
                st.markdown("---")
                st.markdown(
                    "<div style='text-align:center; color: gray; font-size: 13px;'>"
                    "🎬 YouTube Thumbnail Analyzer | "
                    "Built by <b>Abhishek Singh</b> | "
                    "Business Analyst & GenAI Enthusiast"
                    "</div>",
                    unsafe_allow_html=True
                )

            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    st.error("⚠️ Rate limit exceed! 1-2 minute baad try karo.")
                else:
                    st.error(f"⚠️ Error: {str(e)}")