from tkinter import *
import ctypes
import os
from PIL import ImageTk, Image
import tkinter.messagebox as tkMessageBox
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
import speech_recognition as sr
import pyttsx3
import threading as td
from transformers import MarianMTModel, MarianTokenizer
from deep_translator import GoogleTranslator
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename

# Initialize the recognizer
r = sr.Recognizer()

# Initialize the main window
main = Tk()
main.title("Voiceprint Translator")
main.geometry("1040x770")
main.config(bg="#C7F8FF")
main.resizable(0, 0)


lt = [
    "English", "Hindi", "Tamil", "Gujarati", "Marathi", "Spanish", "French", 
    "German", "Italian", "Portuguese", "Chinese", "Arabic", "Russian", 
    "Japanese", "Korean", "Dutch", "Turkish", "Swedish", "Polish", "Thai", "Telugu",
    "Bengali", "Urdu", "Punjabi", "Malayalam", "Kannada", "Nepali", "Sinhala",
    "Greek", "Romanian", "Hungarian", "Finnish", "Hebrew", "Vietnamese", 
    "Indonesian", "Czech", "Slovak", "Croatian", "Bulgarian", "Serbian",
    "Malay", "Filipino", "Swahili", "Zulu", "Xhosa"
]

v1 = StringVar(main)
v1.set(lt[0])
v2 = StringVar(main)
v2.set(lt[1])

# Title label
Label(main, text="Real Time Multilingual Translator", font=("", 18, "bold"),  fg="black").place(x=340, y=20)

flag = False

# Canvas for input box
can = Canvas(main, width=400, height=450, bg="#f24950", relief="solid", bd=1, highlightthickness=0)
can.place(x=30, y=80)
Label(main, text="Input Box:", font=("", 12, "bold"), bg="#f24950", fg="black").place(x=44, y=70)

# Canvas for output box
can = Canvas(main, width=400, height=450, bg="#FEC260", relief="solid", bd=1, highlightthickness=0)
can.place(x=590, y=80)
Label(main, text="Output Box:", font=("", 12, "bold"), bg="#FEC260", fg="black").place(x=880, y=60)

# Text boxes
txtbx = Text(main, width=40, height=10, font=("", 12, "bold"), relief="solid", bd=0, highlightthickness=0)
txtbx.place(x=50, y=100)

txtbx2 = Text(main, width=40, height=10, font=("", 12, "bold"), relief="solid", bd=0, highlightthickness=0)
txtbx2.place(x=610, y=100)

# Load MarianMTModel and tokenizer for offline translation
def load_offline_model(language_pair):
    model_name = f'Helsinki-NLP/opus-mt-en-{language_pair}'
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    return model, tokenizer

# Function to translate text using offline translation
def offline_translate(text, lang_from, lang_to):
    model, tokenizer = load_offline_model(f'{lang_from}-{lang_to}')
    
    # Encode and translate the input text
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    translated = model.generate(**inputs)
    
    # Decode and return translated text
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return translated_text


# Function to import text from a PDF
def import_pdf():
    file = askopenfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if file:
        try:
            reader = PdfReader(file)
            content = ""
            for page in reader.pages:
                content += page.extract_text() + "\n"
            txtbx.delete("1.0", "end-1c")  # Clear the input text box
            txtbx.insert("end", content)  # Insert extracted text
        except Exception as e:
            tkMessageBox.showinfo("Error", f"Failed to read PDF: {str(e)}")

# Function to download the translated text as a PDF
def download_translated_pdf():
    # Get the translated text from the output text box (txtbx2)
    translated_text = txtbx2.get("1.0", "end-1c")
    
    if not translated_text.strip():
        tkMessageBox.showinfo("Error", "No translated text available to save.")
        return
    
    file = asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    
    if file:
        try:
            # Create a PDF file and add the translated text
            c = canvas.Canvas(file, pagesize=letter)
            width, height = letter
            lines = translated_text.split('\n')  # Split text into lines
            
            # Adjust line spacing and write text
            y = height - 50  # Start near the top of the page
            for line in lines:
                if y < 50:  # Check if we need a new page
                    c.showPage()
                    y = height - 50
                c.drawString(50, y, line)  # Write line to the canvas
                y -= 15  # Move down for the next line
            
            c.save()  # Save the PDF
            tkMessageBox.showinfo("Success", "Translated text saved as PDF successfully!")
        except Exception as e:
            tkMessageBox.showinfo("Error", f"Failed to save PDF: {str(e)}")
            
# Function to import doc
def import_text():
    file = askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if file:
        with open(file, "r") as f:
            content = f.read()
        txtbx.delete("1.0", "end-1c")  
        txtbx.insert("end", content)  
        
# Function to speak the text
def speak():
    global txtbx2
    tx = txtbx2.get("1.0", END)
    code = ["en", "hi", "ta", "gu", "mr", "es", "fr", "de", "it", "pt", "zh-CN", "ar", "ru",
    "ja", "ko", "nl", "tr", "sv", "pl", "th", "te", "bn", "ur", "pa", "ml", "kn",
    "ne", "si", "el", "ro", "hu", "fi", "he", "vi", "id", "cs", "sk", "hr", "bg",
    "sr", "ms", "tl", "sw", "zu", "xh"]
    language = code[lt.index(v2.get())]
    myobj = gTTS(text=tx, lang=language, slow=False)
    try:
        os.remove("temp.mp3")
    except:
        pass
    myobj.save("temp.mp3")
    song = AudioSegment.from_mp3("temp.mp3")
    play(song)

# Function to detect and translate speech
def detect():
    global flag, txtbx
    while True:
        if flag == True:
            break
        try:
            with sr.Microphone() as source2:
                r.adjust_for_ambient_noise(source2, duration=0.2)
                txtbx.delete("1.0", END)  
                txtbx.insert("end", "Listening...")  
                audio2 = r.listen(source2)
                MyText = r.recognize_google(audio2)
                MyText = MyText.lower()
                print(f"You said: {MyText}")
                txtbx.delete("1.0", END)  
                txtbx.insert("end", MyText)  
                translate()
        except sr.RequestError as e:
            tkMessageBox.showinfo("Warning", "Could not request results; {0}".format(e))
            break
        except sr.UnknownValueError:
            tkMessageBox.showinfo("Warning", "Unknown error occurred")
            break

# Function to start speech detection
def start():
    global flag, b1
    flag = False
    b1["text"] = "Stop Speaking"
    b1["command"] = stop
    td.Thread(target=detect).start()

# Function to stop speech detection
def stop():
    global flag, b1
    b1["text"] = "Give Voice Input"
    b1["command"] = start
    flag = True

# Function to clear all text boxes and reset to defaults
def clear_all():
    txtbx.delete("1.0", "end-1c")  
    txtbx2.delete("1.0", "end-1c")  
    v1.set(lt[0]) 
    v2.set(lt[1]) 

# Function to detect typing and translate in real-time
def detect_typing(event):
    translate()

# Function to translate text
def translate():
    global txtbx, txtbx2
    txtbx2.delete("1.0", "end-1c")
    tx = txtbx.get("1.0", END)
    code = ["en", "hi", "ta", "gu", "mr", "es", "fr", "de", "it", "pt", "zh-CN", "ar", "ru",
    "ja", "ko", "nl", "tr", "sv", "pl", "th", "te", "bn", "ur", "pa", "ml", "kn",
    "ne", "si", "el", "ro", "hu", "fi", "he", "vi", "id", "cs", "sk", "hr", "bg",
    "sr", "ms", "tl", "sw", "zu", "xh"]
        
    lang_from = "auto"  
    lang_to = code[lt.index(v2.get())]  
    
    offline_lang_pairs = ["en-hi", "hi-en", "en-ta", "ta-en", "en-gu", "gu-en"]  
    if lang_from == "en" and lang_to in ["hi", "ta", "gu"]:
        translated = offline_translate(tx, lang_from, lang_to)
        txtbx2.insert("end", translated)
    else:
        try:
            translated = GoogleTranslator(source=lang_from, target=lang_to).translate(tx)
            txtbx2.insert("end", translated)
        except Exception as e:
            tkMessageBox.showinfo("Error", f"Translation failed: {str(e)}")

# Function to swap input and output languages and text boxes
def swap_languages():
    current_input = v1.get()
    current_output = v2.get()
    v1.set(current_output)
    v2.set(current_input)

    input_text = txtbx.get("1.0", END)
    output_text = txtbx2.get("1.0", END)
    txtbx.delete("1.0", END)  
    txtbx.insert("end", "Listening...")  
    txtbx2.delete("1.0", "end-1c")
    txtbx2.insert("end", input_text)

# Function to download the translated text as a .txt file
def download_translated_text():
    # Get the translated text from the output text box (txtbx2)
    translated_text = txtbx2.get("1.0", "end-1c")  # Retrieve text from txtbx2
    
    # Check if there is any translated text
    if not translated_text.strip():
        tkMessageBox.showinfo("Error", "No translated text available to save.")
        return
    
    # Open a save file dialog to choose the location and name for the file
    file = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    
    if file:
        try:
            # Write the translated text to the selected file using UTF-8 encoding
            with open(file, "w", encoding="utf-8") as f:
                f.write(translated_text)
            tkMessageBox.showinfo("Success", "File saved successfully!")
        except Exception as e:
            tkMessageBox.showinfo("Error", f"Failed to save file: {str(e)}")

# Function to stop speech detection
def stop():
    global flag, b1
    flag = True
    b1["text"] = "Give Voice Input"
    b1["command"] = start
    txtbx.delete("1.0", END)  

# Theme toggle function
current_theme = "light"

def toggle_theme():
    global current_theme
    if current_theme == "light":
        main.config(bg="#121212")
        txtbx.config(bg="#1E1E1E", fg="#FFFFFF")
        txtbx2.config(bg="#1E1E1E", fg="#FFFFFF")
        b1.config(bg="#FEC260", fg="#000000")
        current_theme = "dark"
    else:
        main.config(bg="#C7F8FF")
        txtbx.config(bg="#FFFFFF", fg="#000000")
        txtbx2.config(bg="#FFFFFF", fg="#000000")
        b1.config(bg="#FEC260", fg="#000000")
        current_theme = "light"

# # Add a theme toggle button
# theme_button = Button(main, text="Toggle Theme", font=("", 12, "bold"), width=15, bg="#FEF9EF", fg="black", 
#                       command=toggle_theme, relief="solid", bd=1, highlightthickness=0)
# theme_button.place(x=455, y=600)


# Button to give voice input
b1 = Button(main, text="Give Voice Input", font=("", 12, "bold"), width=35, relief="solid", bd=1, 
            highlightthickness=0, command=start, bg="#FEC260", fg="black")
b1.place(x=50, y=450)

Button(main, text="Speak Text", font=("", 12, "bold"), width=35, bg="#17C3B2", fg="black", command=speak, relief="solid", bd=1,
       highlightthickness=0).place(x=610, y=450)

Button(main, text="Translate", font=("", 12, "bold"), width=10, bg="#FEF9EF", fg="black", command=translate, relief="solid", bd=1, highlightthickness=0).place(x=455, y=380)

# Button to import text file for translation
Button(main, text="Import Text File", font=("", 12, "bold"), width=20, bg="#17C3B2", fg="black", command=import_text, relief="solid", bd=1, highlightthickness=0).place(x=30, y=550)

# Button to download the translated text
Button(main, text="Download Translated Text", font=("", 12, "bold"), width=20, bg="#FEC260", fg="black", command=download_translated_text, relief="solid", bd=1, highlightthickness=0).place(x=30, y=600)

# Button to import text from a PDF file
Button(main, text="Import PDF File", font=("", 12, "bold"), width=20, bg="#17C3B2", fg="black", command=import_pdf, relief="solid", bd=1, highlightthickness=0).place(x=260, y=550)

# Button to download translated text as PDF
Button(main, text="Download Translated PDF", font=("", 12, "bold"), width=20, bg="#FEC260", fg="black", command=download_translated_pdf, relief="solid", bd=1, highlightthickness=0).place(x=260, y=600)


# Button to swap input/output languages
b2 = Button(main, text="<-- Swap -->", font=("", 12, "bold"), width=10, relief="solid", bd=1, 
            highlightthickness=0, command=swap_languages, bg="#FEF9EF", fg="black")
b2.place(x=455, y=300)

# Clear button to reset to default
clear_button = Button(main, text="Clear All", font=("", 12, "bold"), width=10, bg="#FEF9EF", fg="black", 
                      command=clear_all, relief="solid", bd=1, highlightthickness=0)
clear_button.place(x=455, y=420)

# Label for input/output language options
Label(main, text="Select Input Language:", font=("", 12, "bold"), bg="#f24950", fg="black").place(x=50, y=300)
Label(main, text="Select Output Language:", font=("", 12, "bold"), bg="#FEC260", fg="black").place(x=610, y=300)

# Option menus for selecting languages
o1 = OptionMenu(main, v1, *lt)
o1.config(font=("", 12, "bold"), width=36, bg="#FEF9EF", fg="black", relief="solid", bd=1, highlightthickness=0)
o1.place(x=50, y=340)

o2 = OptionMenu(main, v2, *lt)
o2.config(font=("", 12, "bold"), width=36, bg="#FEF9EF", fg="black", relief="solid", bd=1, highlightthickness=0)
o2.place(x=610, y=340)

# Bind the typing event for real-time translation
txtbx.bind("<KeyRelease>", detect_typing)


# Run the main loop
main.mainloop()
