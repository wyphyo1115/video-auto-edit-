import streamlit as st
from moviepy.editor import *
import tempfile
import os

st.title("🎬 Simple Auto Video Maker")

uploaded_images = st.file_uploader("ပုံများ ရွေးပါ", type=['jpg', 'png', 'jpeg'], accept_multiple_files=True)
uploaded_audio = st.file_uploader("အသံဖိုင်", type=['mp3', 'wav'])

if st.button("Create Video"):
    if uploaded_images and uploaded_audio:
        with st.spinner('Making video...'):
            try:
                # Save temp audio
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                    tmp_audio.write(uploaded_audio.getvalue())
                    audio_path = tmp_audio.name

                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                
                # Create clips
                clips = []
                img_duration = duration / len(uploaded_images)
                
                for img_file in uploaded_images:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
                        tmp_img.write(img_file.getvalue())
                        img_path = tmp_img.name
                    
                    # Create Image Clip
                    clip = (ImageClip(img_path)
                            .resize(height=720)
                            .set_duration(img_duration)
                            .crossfadein(0.5))
                    clips.append(clip)

                # Concatenate
                final_video = concatenate_videoclips(clips, method="compose")
                final_video = final_video.set_audio(audio_clip)
                
                # Write file
                output_file = "output.mp4"
                final_video.write_videofile(output_file, fps=24, codec='libx264')
                
                st.video(output_file)
                st.success("Done!")

            except Exception as e:
                st.error(f"Error: {e}")
