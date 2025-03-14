from gtts import gTTS
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

def create_image_with_text(text, width=640, height=480, font_size=80):
    """Create an image with the specified text."""
    # Create a blank image with a white background
    image = Image.new('RGB', (width, height), color='white')

    # Initialize ImageDraw
    draw = ImageDraw.Draw(image)

    # Load a font
    try:
        # Adjust the font size and path to your system
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        # Fallback to default font if specified font is unavailable
        font = ImageFont.load_default()

    # Calculate text size using textbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate position for centering the text
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    # Draw the text on the image
    draw.text((text_x, text_y), text, fill='black', font=font)

    # Convert to a NumPy array for MoviePy
    return np.array(image)

def text_to_speech(text, filename='output.mp3'):
    """Convert text to speech and save it as an audio file."""
    tts = gTTS(text=text, lang='en')
    tts.save(filename)

def create_video_from_text(text, output_filename='output_video.mp4', duration=5):
    """Create a video from the given text."""
    # Create an image with the text
    image_with_text = create_image_with_text(text)

    # Create a video clip from the image
    clip = ImageClip(image_with_text).set_duration(duration)

    # Create audio from text
    audio_filename = 'output.mp3'
    text_to_speech(text, audio_filename)

    # Load audio file
    audio_clip = AudioFileClip(audio_filename)

    # Set audio to the video clip
    video = clip.set_audio(audio_clip)

    # Write the video file
    video.write_videofile(output_filename, fps=24)

    # Clean up: Remove the audio file after creating the video
    os.remove(audio_filename)

if __name__ == "__main__":
    # Example usage
    text = "Heg idira. Chana gidira. Ela"
    create_video_from_text(text)
