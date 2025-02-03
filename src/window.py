import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import askyesno
import qrcode
from PIL import Image, ImageTk
import io
from .app import LocalAudioStreamer
from gi.repository import GLib

class window(LocalAudioStreamer):
    """
    Bilding an user interface
    """
    def __init__(self, streamer_instance):
        super().__init__()
        self.streamer = streamer_instance
        self.url_qrcode = 'rtsp://'+self.streamer.ip_address+':'+\
                            str(self.streamer.port)+self.streamer.mount_point
        self.root = None
        self.qrcode_label = None
        self.data_entry = None
        self.close_button = None
        
    def generate_qrcode(self):
        """
        Generate the qrcode
        """
        qr = qrcode.QRCode(
            version=None,
            box_size = 6,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            border=4,
        )
        qr.add_data(self.url_qrcode)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        try:
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_tk = ImageTk.PhotoImage(Image.open(buffered))
        except Exception as e:
            print(f"Error converting image: {e}")
            return

        self.qrcode_label.config(image=img_tk)
        self.qrcode_label.image = img_tk

        # Update the data label
        self.data_label.config(text=f"Please open the url in a media player\nthat supports RTSP streams, such as VLC ")  # Set the data label text
        # Update the text area
        self.data_entry.insert(tk.END, self.url_qrcode)  # Insert the data of the qrcode image
        
    def closing_win(self):
        if messagebox.askokcancel(title='Close QR Code Generator-Detector', message='Are you sure you want to close the application?'):
            GLib.idle_add(self.stop_streaming_and_quit)  # Use the instance
            self.root.destroy()
            # The application will now quit after the GStreamer pipeline is stopped

    def close_window(self):
        if askyesno(title='Close QR Code Generator-Detector', message='Are you sure you want to close the application?'):
            GLib.idle_add(self.stop_streaming_and_quit)  # Use the instance
            self.root.destroy()
            # The application will now quit after the GStreamer pipeline is stopped

    def stop_streaming_and_quit(self):
        super().stop_streaming()
        GLib.MainLoop().quit()  # Stop the GLib main loop. This will allow the application to exit.
           
    def start_gui(self):
        self.root = tk.Tk()
        self.root.title("Local Audio Streamer")
        self.root.geometry('400x390+350+180')
        
        self.qrcode_label = ttk.Label(self.root)

        self.qrcode_label.grid(row=1, column=0, padx=10, pady=10)
        # Create the data label
        self.data_label = ttk.Label(self.root)
        self.data_label.grid(row=2, column=0, padx=10, pady=10)

        self.data_entry = ttk.Entry(self.root, width=45)
        self.data_entry.grid(row=3, column=0, padx=10, pady=10)

        self.close_button = ttk.Button(self.root, text="Close", command=self.close_window)
        self.close_button.grid(row=4, column=0, padx=10, pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.closing_win)

        self.root.after(100, self.generate_qrcode())

        self.root.mainloop()

