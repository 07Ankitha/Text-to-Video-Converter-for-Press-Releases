import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
from gtts import gTTS
from googletrans import Translator
from moviepy.editor import ImageClip, AudioFileClip
import os

class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PIB Press Release")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')

        # Language mapping
        self.language_codes = {
            "English": "en",
            "Hindi": "hi",
            "Kannada": "kn",
            "Tamil": "ta",
            "Malayalam": "ml"
        }

        self.setup_gui()

    def setup_gui(self):
        # Main container
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_frame = tk.Frame(main_container, bg='#1a1a1a')
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title = tk.Label(header_frame, text="PIB Press Release", 
                        font=('Arial', 24, 'bold'), fg='#b19cd9', bg='#1a1a1a')
        title.pack(pady=(0, 10))

        # Content area
        content_frame = tk.Frame(main_container, bg='#1a1a1a')
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Text input
        left_frame = tk.Frame(content_frame, bg='#1a1a1a')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(left_frame, text="ENTER THE TEXT TO\nGENERATE THE VIDEO",
                font=('Arial', 12, 'bold'), fg='#b19cd9', bg='#1a1a1a').pack(pady=(0, 10))

        self.text_entry = tk.Text(left_frame, height=10, bg='#2d2d2d', fg='white',
                                font=('Arial', 11))
        self.text_entry.pack(fill=tk.BOTH, expand=True)

        # Right side - Language and Browse
        right_frame = tk.Frame(content_frame, bg='#1a1a1a')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Language selection
        lang_frame = tk.Frame(right_frame, bg='#1a1a1a')
        lang_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(lang_frame, text="SELECT THE LANGUAGE",
                font=('Arial', 12, 'bold'), fg='#b19cd9', bg='#1a1a1a').pack(pady=(0, 10))

        self.language_var = tk.StringVar(value="English")
        for lang in self.language_codes.keys():
            rb = tk.Radiobutton(lang_frame, text=lang, value=lang,
                              variable=self.language_var, fg='white', bg='#1a1a1a',
                              selectcolor='#1a1a1a', activebackground='#1a1a1a',
                              activeforeground='#b19cd9')
            rb.pack(anchor=tk.W, pady=2)

        # Browse frame
        browse_frame = tk.Frame(right_frame, bg='#1a1a1a')
        browse_frame.pack(fill=tk.X, pady=20)

        tk.Label(browse_frame, text="BROWSE IMAGES",
                font=('Arial', 12, 'bold'), fg='#b19cd9', bg='#1a1a1a').pack(pady=(0, 10))

        tk.Button(browse_frame, text="Browse Image",
                 command=self.browse_image, bg='#2d2d2d', fg='white',
                 activebackground='#b19cd9').pack()

        # Generate button
        self.generate_button = tk.Button(main_container, text="Generate Video",
                                       command=self.generate_video, bg='#b19cd9',
                                       fg='white', activebackground='#9a7cc9',
                                       font=('Arial', 11, 'bold'),
                                       padx=30, pady=10)
        self.generate_button.pack(pady=20)

    def browse_image(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if filename:
            # Store the selected image path for later use
            self.selected_image = filename

    def generate_video(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        language = self.language_codes[self.language_var.get()]
        
        if not text:
            messagebox.showwarning("Input Missing", "Please enter some text.")
            return
        
        output_path = filedialog.asksaveasfilename(
            defaultextension=".mp4",
            filetypes=[("MP4 files", "*.mp4")])
        
        if output_path:
            self.create_video(text, language, output_path)

    def create_video(self, text, language, output_path):
        try:
            # Translate text
            translator = Translator()
            translated = translator.translate(text, dest=language)
            translated_text = translated.text

            # Create temporary files with full paths
            temp_dir = os.path.dirname(output_path)
            audio_file = os.path.join(temp_dir, "temp_audio.mp3")
            image_file = os.path.join(temp_dir, "temp_image.jpg")

            # Generate audio
            tts = gTTS(text=translated_text, lang=language, slow=False)
            tts.save(audio_file)

            # Create image with text
            img = Image.new("RGB", (1280, 720), color="white")
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            
            # Calculate text position
            words = translated_text.split()
            lines = []
            current_line = ''
            
            for word in words:
                test_line = current_line + ' ' + word if current_line else word
                bbox = font.getbbox(test_line)
                if bbox[2] < (1280 - 100):  # 50px margin on each side
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Draw text
            line_height = font.getbbox('Tg')[3]
            y = (720 - len(lines) * line_height) // 2
            
            for line in lines:
                bbox = font.getbbox(line)
                x = (1280 - bbox[2]) // 2
                draw.text((x, y), line, fill="black", font=font)
                y += line_height

            img.save(image_file)

            # Create video with specific codec settings
            video_clip = ImageClip(image_file).set_duration(10)
            audio_clip = AudioFileClip(audio_file)
            
            # Trim audio if longer than video duration
            if audio_clip.duration > 10:
                audio_clip = audio_clip.subclip(0, 10)
            
            final_clip = video_clip.set_audio(audio_clip)
            
            # Write video with specific codec settings
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=os.path.join(temp_dir, "temp-audio.m4a"),
                remove_temp=True,
                threads=4,
                ffmpeg_params=[
                    "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart"
                ]
            )

            # Cleanup
            for temp_file in [audio_file, image_file]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

            messagebox.showinfo("Success", "Video created successfully!")

        except Exception as e:
            # Cleanup on error
            for temp_file in [audio_file, image_file]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()