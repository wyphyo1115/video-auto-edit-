import streamlit as st
from moviepy.editor import *
import tempfile
import os

# ယာယီဖိုင်သိမ်းမည့် Function
def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        return None

st.set_page_config(page_title="BingBong Auto Video Editor", page_icon="🎬")

st.title("🎬 BingBong Auto Video Maker")
st.write("ပုံတွေ၊ အသံနဲ့ နောက်ခံဗီဒီယိုကို ထည့်လိုက်ပါ - ကျန်တာ App က အလိုအလျောက် ဖြတ်ဆက်ပေးပါလိမ့်မယ်။")

# --- 1. Inputs (ဖိုင်ထည့်ရန်နေရာများ) ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Media Assets")
    uploaded_images = st.file_uploader("ဓာတ်ပုံများ ရွေးပါ (၄ ပုံ ခန့်)", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
    uploaded_bg_video = st.file_uploader("နောက်ခံ ဗီဒီယို (Background)", type=['mp4', 'mov'])

with col2:
    st.subheader("2. Audio & Text")
    uploaded_audio = st.file_uploader("အသံဖိုင် (Voice/Music)", type=['mp3', 'wav'])
    subtitle_text = st.text_area("စာတန်းထိုးရန် (Subtitle)", "BingBong Video Production")

# --- 2. Processing (ဗီဒီယိုထုတ်လုပ်ခြင်း) ---
if st.button("🚀 Create Video (ဗီဒီယို ထုတ်မယ်)", type="primary"):
    if uploaded_images and uploaded_bg_video and uploaded_audio:
        with st.spinner('ဗီဒီယိုကို တည်းဖြတ်နေပါပြီ... ခဏစောင့်ပါ...'):
            try:
                # ဖိုင်များကို ယာယီသိမ်းဆည်းခြင်း
                bg_video_path = save_uploaded_file(uploaded_bg_video)
                audio_path = save_uploaded_file(uploaded_audio)
                image_paths = [save_uploaded_file(img) for img in uploaded_images]

                # ၁. အသံဖိုင်ကို တည်ဆောက်ခြင်း
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration # ဗီဒီယိုအရှည်ကို အသံဖိုင်အရှည်အတိုင်း ယူမယ်

                # ၂. နောက်ခံဗီဒီယိုကို ပြင်ဆင်ခြင်း
                bg_clip = VideoFileClip(bg_video_path).resize(height=720) # 720p သို့ ပြောင်းမယ်
                # ဗီဒီယိုတိုနေရင် Loop လုပ်မယ်၊ ရှည်နေရင် ဖြတ်မယ်
                if bg_clip.duration < duration:
                    bg_clip = vfx.loop(bg_clip, duration=duration)
                else:
                    bg_clip = bg_clip.subclip(0, duration)

                # ၃. ပုံများကို တစ်လှည့်စီ ပြသခြင်း
                image_clips = []
                img_duration = duration / len(image_paths) # ပုံတစ်ပုံ ကြာချိန်

                for i, img_path in enumerate(image_paths):
                    # ပုံကို Resize လုပ်ပြီး အလယ်မှာ ထားမယ်
                    img = (ImageClip(img_path)
                           .resize(height=500) 
                           .set_position("center")
                           .set_start(i * img_duration)
                           .set_duration(img_duration)
                           .crossfadein(0.5)) # အဝင် Effect
                    image_clips.append(img)

                # ၄. စာတန်းထိုးခြင်း (Text)
                # Note: ImageMagick မရှိရင် ဒီအပိုင်း Error တက်နိုင်ပါတယ်
                try:txt_clip = (TextClip(subtitle_text, fontsize=50, color='white', font='Arial', stroke_color='black', stroke_width=2)
                                .set_position(('center', 'bottom'))
                                .set_duration(duration))
                    final_layers = [bg_clip, *image_clips, txt_clip]
                except:
                    st.warning("ImageMagick မရှိသောကြောင့် စာတန်းမပါဘဲ ထုတ်ပါမည်။")
                    final_layers = [bg_clip, *image_clips]

                # ၅. အားလုံးပေါင်းစပ်ခြင်း (Composite)
                final_video = CompositeVideoClip(final_layers, size=bg_clip.size)
                final_video = final_video.set_audio(audio_clip)

                # ၆. Export (ထုတ်ယူခြင်း)
                output_filename = "bingbong_output.mp4"
                final_video.write_videofile(output_filename, codec='libx264', audio_codec='aac', fps=24)

                # ၇. ရလဒ်ပြသခြင်း
                st.success("✅ ဗီဒီယို ရပါပြီ!")
                st.video(output_filename)
                
                # Download Button
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="⬇️ Download Video",
                        data=file,
                        file_name="my_auto_video.mp4",
                        mime="video/mp4"
                    )

                # ယာယီဖိုင်များကို ရှင်းလင်းခြင်း (Optional)
                os.remove(bg_video_path)
                os.remove(audio_path)
                for p in image_paths: os.remove(p)

            except Exception as e:
                st.error(f"Error ဖြစ်သွားပါတယ်: {e}")
    else:
        st.error("ကျေးဇူးပြု၍ ပုံ၊ အသံ နှင့် နောက်ခံဗီဒီယို အားလုံးကို ထည့်ပေးပါ။")