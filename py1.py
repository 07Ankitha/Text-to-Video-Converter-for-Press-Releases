import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from gtts import gTTS
from googletrans import Translator
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import os

class VideoConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PIB Press Release")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a1a')

        # Language mapping (adding more languages)
        self.language_codes = {
            "English": "en",
            "Hindi": "hi",
            "Kannada": "kn",
            "Tamil": "ta",
            "Malayalam": "ml",
            "Telugu": "te",
            "Bengali": "bn",
            "Punjabi": "pa",
            "Gujarati": "gu",
            "Marathi": "mr"
        }

        self.selected_images = []
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

        # Language selection (side by side arrangement)
        lang_frame = tk.Frame(right_frame, bg='#1a1a1a')
        lang_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(lang_frame, text="SELECT THE LANGUAGE",
                font=('Arial', 12, 'bold'), fg='#b19cd9', bg='#1a1a1a').grid(row=0, column=0, pady=(0, 10), padx=10)

        self.language_var = tk.StringVar(value="English")

        row = 1
        col = 0
        for lang in self.language_codes.keys():
            rb = tk.Radiobutton(lang_frame, text=lang, value=lang,
                              variable=self.language_var, fg='white', bg='#1a1a1a',
                              selectcolor='#1a1a1a', activebackground='#1a1a1a',
                              activeforeground='#b19cd9')
            rb.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            col += 1
            if col == 2:  # Start new row after two languages
                col = 0
                row += 1

        # Browse frame
        browse_frame = tk.Frame(right_frame, bg='#1a1a1a')
        browse_frame.pack(fill=tk.X, pady=20)

        tk.Label(browse_frame, text="BROWSE IMAGES",
                font=('Arial', 12, 'bold'), fg='#b19cd9', bg='#1a1a1a').pack(pady=(0, 10))

        tk.Button(browse_frame, text="Browse Images",
                 command=self.browse_images, bg='#2d2d2d', fg='white',
                 activebackground='#b19cd9').pack()

        # Image Preview area
        self.image_preview_frame = tk.Frame(right_frame, bg='#1a1a1a')
        self.image_preview_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        # Generate button
        self.generate_button = tk.Button(main_container, text="Generate Video",
                                       command=self.generate_video, bg='#b19cd9',
                                       fg='white', activebackground='#9a7cc9',
                                       font=('Arial', 11, 'bold'),
                                       padx=30, pady=10)
        self.generate_button.pack(pady=20)

    def browse_images(self):
        # Allow multiple image selection
        filenames = filedialog.askopenfilenames(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        
        if filenames:
            # Ensure no more than 3 images can be selected
            if len(filenames) + len(self.selected_images) > 3:
                messagebox.showwarning("Selection Limit", "You can select up to 3 images only.")
                return
            
            # Add the selected images
            self.selected_images.extend(filenames)
            self.display_images()

    def display_images(self):
        # Clear any previously displayed images
        for widget in self.image_preview_frame.winfo_children():
            widget.destroy()

        # Display selected images
        for filename in self.selected_images:
            img = Image.open(filename)
            img.thumbnail((150, 150))  # Resize image to fit the preview
            img_tk = ImageTk.PhotoImage(img)

            label = tk.Label(self.image_preview_frame, image=img_tk, bg='#1a1a1a')
            label.image = img_tk  # Keep a reference to the image object
            label.pack(side=tk.LEFT, padx=5)

    def generate_video(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        language = self.language_codes[self.language_var.get()]
        
        if not text:
            messagebox.showwarning("Input Missing", "Please enter some text.")
            return
        
        if not self.selected_images:
            messagebox.showwarning("Image Missing", "Please browse at least one image.")
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

            # Generate video using multiple selected images
            image_clips = []
            for img_path in self.selected_images:
                img = Image.open(img_path)
                img = img.resize((1280, 720))  # Resize image to match video size

                # Save the image without text
                image_file = os.path.join(os.path.dirname(output_path), "temp_image.jpg")
                img.save(image_file)

                # Create video clip for each image
                image_clip = ImageClip(image_file).set_duration(8)  # Set 8 seconds duration for each image
                image_clips.append(image_clip)

            # Concatenate the image clips into one video
            final_clip = concatenate_videoclips(image_clips, method="compose")

            # Generate audio for the translated text
            audio_file = os.path.join(os.path.dirname(output_path), "temp_audio.mp3")
            tts = gTTS(text=translated_text, lang=language, slow=False)
            tts.save(audio_file)

            audio_clip = AudioFileClip(audio_file)
            
            # Trim audio if longer than the video duration
            if audio_clip.duration > final_clip.duration:
                audio_clip = audio_clip.subclip(0, final_clip.duration)
            
            final_clip = final_clip.set_audio(audio_clip)

            # Write video with specific codec settings
            final_clip.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=os.path.join(os.path.dirname(output_path), "temp-audio.m4a"),
                remove_temp=True,
                threads=4,
                ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"]
            )

            # Cleanup temporary files
            os.remove(image_file)
            os.remove(audio_file)

            messagebox.showinfo("Success", "Video created successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()
