import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import pdf2image
import os

def select_pdf_and_display_image():
    # Select PDF file
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if not pdf_path:
        return

    # Convert PDF to image
    images = pdf2image.convert_from_path(pdf_path)
    if not images:
        return

    # Display the first page of the PDF
    first_page_image = images[0]
    first_page_image = first_page_image.resize((1241, 1754), Image.LANCZOS)  # Resize image to A4 size

    # Save the image in the same folder as the PDF
    pdf_dir = os.path.dirname(pdf_path)
    image_path = os.path.join(pdf_dir, "first_page_image.png")
    first_page_image.save(image_path)

    # Create Tkinter window
    root = tk.Tk()
    root.title("PDF Image Viewer")

    # Convert PIL image to PhotoImage
    photo = ImageTk.PhotoImage(first_page_image)

    # Create a label to display the image
    label = tk.Label(root, image=photo)
    label.image = photo  # Keep a reference to avoid garbage collection
    label.pack()

    # Run the Tkinter main loop
    root.mainloop()

if __name__ == "__main__":
    select_pdf_and_display_image()