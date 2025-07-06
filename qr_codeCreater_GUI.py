import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
import time

# --- Sabitler ---
APP_TITLE = "QR Kod Oluşturucu"
APP_RESIZABLE = True 

# Renk paleti
COLOR_PRIMARY_BG = "#FFB266" 
COLOR_SECONDARY_BG = "#FFD7A8"
COLOR_DARK_ACCENT = "#333333" 
COLOR_DARKER_ACCENT = "#1A1A1A"
COLOR_TEXT_LIGHT = "#FFFFFF" 
COLOR_TEXT_DARK = "#333333" 
COLOR_ERROR = "#FF5733" 

FONT_HEADER = ("Segoe UI", 18, "bold")
FONT_SUBHEADER = ("Segoe UI", 14, "bold")
FONT_BODY = ("Segoe UI", 12)
FONT_BUTTON = ("Segoe UI", 12, "bold")

QR_CODE_SAVE_DIR = "./qrcodes"
QR_CODE_DISPLAY_SIZE = (450, 450) 

class QRCodeGeneratorApp:
    def __init__(self, master):
        self.master = master
        self.master.title(APP_TITLE)
        
        self.master.state('zoomed') 
        
        self.master.config(bg=COLOR_PRIMARY_BG)
        if not APP_RESIZABLE:
            self.master.resizable(False, False)
        else:
            self.master.grid_rowconfigure(0, weight=1)
            self.master.grid_columnconfigure(0, weight=1)
            self.master.grid_columnconfigure(1, weight=1)

        # Uygulama Durum Değişkenleri
        self.selected_center_img_path = "" # Ortadaki resim
        self.selected_bg_img_path = "" # Arka plan resmi
        self.qr_code_name = ""
        self.current_mode = 0 
        self.generated_qr_pil_image = None 
        self.base_qr_pil_image = None 

        self._create_widgets()

    def _create_widgets(self):
        """Uygulamadaki tüm UI bileşenlerini oluşturur ve ilk görünümlerini ayarlar."""

        # Sol taraf için Frame (Giriş ve Tasarım Ayarları)
        self.left_frame = Frame(self.master, bg=COLOR_PRIMARY_BG)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.left_frame.grid_rowconfigure(9, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        # Sağ taraf için Frame (QR Kodu Görüntüleme ve Geri Bildirim)
        self.right_frame = Frame(self.master, bg=COLOR_PRIMARY_BG)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_rowconfigure(1, weight=0)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # --- Sol Frame Bileşenleri ---
        self.lbl_title = Label(self.left_frame, text="Başlık:", bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_DARK, font=FONT_SUBHEADER)
        self.lbl_title.grid(row=0, column=0, sticky="w", pady=(0, 2))

        self.entry_title = Entry(self.left_frame, width=35, font=FONT_BODY, fg='grey',
                                 insertbackground=COLOR_DARK_ACCENT, bd=3)
        self.entry_title.insert(0, "QR Kod Adı (örn: Web Sitem)") 
        self.entry_title.bind("<FocusIn>", self._clear_placeholder)
        self.entry_title.bind("<FocusOut>", self._add_placeholder)
        self.entry_title.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        self.lbl_link = Label(self.left_frame, text="Bağlantı/Metin:", bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_DARK, font=FONT_SUBHEADER)
        self.lbl_link.grid(row=2, column=0, sticky="w", pady=(0, 2))

        self.entry_link = Entry(self.left_frame, width=35, font=FONT_BODY, fg='grey',
                                 insertbackground=COLOR_DARK_ACCENT, bd=3)
        self.entry_link.insert(0, "https://ornek.com veya Metniniz") 
        self.entry_link.bind("<FocusIn>", self._clear_placeholder)
        self.entry_link.bind("<FocusOut>", self._add_placeholder)
        self.entry_link.grid(row=3, column=0, sticky="ew", pady=(0, 20))

        self.btn_generate = Button(self.left_frame, text="QR Kodu Oluştur", font=FONT_BUTTON, width=25,
                                   bg=COLOR_DARK_ACCENT, fg=COLOR_TEXT_LIGHT, command=self._generate_qr)
        self.btn_generate.grid(row=4, column=0, sticky="ew", pady=(0, 20))

        # --- Tasarım Ayarları Frame'i ---
        self.design_frame = LabelFrame(self.left_frame, text="Tasarım Ayarları", bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_DARK,
                                        font=FONT_SUBHEADER, padx=10, pady=10)
        self.design_frame.grid(row=5, column=0, sticky="nsew", pady=(0, 20))
        self.design_frame.grid_columnconfigure(1, weight=1)

        # Resim Ayarları
        self.lbl_image_settings = Label(self.design_frame, text="Resim Ayarları:", bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_DARK, font=FONT_BODY)
        self.lbl_image_settings.grid(row=0, column=0, sticky="w", pady=5)
        
        self.image_settings_options = ["Yok", "Ortadaki Resim", "Arka Plan Resmi"]
        self.selected_image_setting_var = StringVar(self.master)
        self.selected_image_setting_var.set("Yok") 

        self.image_settings_dropdown = OptionMenu(self.design_frame, self.selected_image_setting_var, *self.image_settings_options,
                                                  command=self._update_image_settings_visibility)
        self.image_settings_dropdown.config(bg=COLOR_SECONDARY_BG, fg=COLOR_TEXT_DARK, font=FONT_BODY, width=18)
        self.image_settings_dropdown.grid(row=0, column=1, sticky="ew", pady=5, padx=5)

        # Ortadaki Resim Yükleme 
        self.lbl_center_image_info = Label(self.design_frame, text="", bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_DARK, font=FONT_BODY)
        self.btn_select_center_img = Button(self.design_frame, text="Ortadaki Resmi Seç", font=FONT_BUTTON, width=20,
                                            bg=COLOR_SECONDARY_BG, fg=COLOR_TEXT_DARK, command=self._select_center_image)

        # Arka Plan Resmi Seçme Düğmesi ve Bilgisi 
        self.lbl_background_image_info = Label(self.design_frame, text="", bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_DARK, font=FONT_BODY)
        self.btn_select_background_img = Button(self.design_frame, text="Arka Plan Resmi Seç", font=FONT_BUTTON, width=20,
                                               bg=COLOR_SECONDARY_BG, fg=COLOR_TEXT_DARK, command=self._select_background_image)

        # Desen Seçenekleri
        self.lbl_pattern_selection = Label(self.design_frame, text="Desen (Modül Şekli):", bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_DARK, font=FONT_BODY)
        self.lbl_pattern_selection.grid(row=1, column=0, sticky="w", pady=5)
        self.pattern_options = ["Kare", "Yuvarlak Noktalar"]
        self.selected_pattern_var = StringVar(self.master)
        self.selected_pattern_var.set("Kare") 

        self.pattern_dropdown = OptionMenu(self.design_frame, self.selected_pattern_var, *self.pattern_options)
        self.pattern_dropdown.config(bg=COLOR_SECONDARY_BG, fg=COLOR_TEXT_DARK, font=FONT_BODY, width=18)
        self.pattern_dropdown.grid(row=1, column=1, sticky="ew", pady=5, padx=5) 

        # Hata Düzeltme Seviyesi
        self.lbl_error_correction = Label(self.design_frame, text="Hata Düzeltme Seviyesi:", bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_DARK, font=FONT_BODY)
        self.lbl_error_correction.grid(row=2, column=0, sticky="w", pady=5) 
        
        self.error_correction_levels = {
            "Düşük (L)": ERROR_CORRECT_L,
            "Orta (M)": ERROR_CORRECT_M,
            "Yüksek (Q)": ERROR_CORRECT_Q,
            "Çok Yüksek (H)": ERROR_CORRECT_H
        }
        self.error_correction_names = list(self.error_correction_levels.keys())
        self.selected_error_correction = StringVar(self.master)
        self.selected_error_correction.set(self.error_correction_names[1]) 

        self.error_correction_dropdown = OptionMenu(self.design_frame, self.selected_error_correction, *self.error_correction_names)
        self.error_correction_dropdown.config(bg=COLOR_SECONDARY_BG, fg=COLOR_TEXT_DARK, font=FONT_BODY, width=18)
        self.error_correction_dropdown.grid(row=2, column=1, sticky="ew", pady=5, padx=5) 

        # QR Kod Rengi Seçimi
        self.lbl_qr_color = Label(self.design_frame, text="QR Kod Rengi:", bg=COLOR_PRIMARY_BG, fg=COLOR_TEXT_DARK, font=FONT_BODY)
        self.lbl_qr_color.grid(row=3, column=0, sticky="w", pady=5) 
        
        self.slider_r = Scale(self.design_frame, from_=0, to=255, orient="horizontal", label="Kırmızı Ton",
                              command=self._qr_color_changer, length=250, bg=COLOR_SECONDARY_BG,
                              fg=COLOR_TEXT_DARK, troughcolor=COLOR_DARK_ACCENT, highlightbackground=COLOR_PRIMARY_BG)
        self.slider_r.grid(row=4, column=0, columnspan=2, sticky="ew", pady=2) 
        
        self.slider_g = Scale(self.design_frame, from_=0, to=255, orient="horizontal", label="Yeşil Ton",
                              command=self._qr_color_changer, length=250, bg=COLOR_SECONDARY_BG,
                              fg=COLOR_TEXT_DARK, troughcolor=COLOR_DARK_ACCENT, highlightbackground=COLOR_PRIMARY_BG)
        self.slider_g.grid(row=5, column=0, columnspan=2, sticky="ew", pady=2) 
        
        self.slider_b = Scale(self.design_frame, from_=0, to=255, orient="horizontal", label="Mavi Ton",
                              command=self._qr_color_changer, length=250, bg=COLOR_SECONDARY_BG,
                              fg=COLOR_TEXT_DARK, troughcolor=COLOR_DARK_ACCENT, highlightbackground=COLOR_PRIMARY_BG)
        self.slider_b.grid(row=6, column=0, columnspan=2, sticky="ew", pady=2)

        # Varsayılan renkleri ayarla
        self.slider_r.set(0) 
        self.slider_g.set(0)
        self.slider_b.set(0)

        # Sağ Frame Bileşenleri
        self.lbl_qr_display = Label(self.right_frame, bg=COLOR_PRIMARY_BG) 
        self.lbl_qr_display.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.lbl_feedback = Label(self.right_frame, text="", bg=COLOR_DARK_ACCENT, fg=COLOR_TEXT_LIGHT, font=FONT_BODY,
                                   wraplength=400) 
        self.lbl_feedback.grid(row=1, column=0, sticky="ew", pady=(20, 0), padx=50)
        
        # Başlangıçta gizle
        self._update_image_settings_visibility("Yok")


    def _clear_placeholder(self, event):
        """Entry'nin placeholder metnini temizler."""
        if event.widget.get() in ("QR Kod Adı (örn: Web Sitem)", "https://ornek.com veya Metniniz"):
            event.widget.delete(0, END)
            event.widget.config(fg=COLOR_TEXT_DARK)

    def _add_placeholder(self, event):
        """Entry boşsa placeholder metni geri ekler."""
        if not event.widget.get():
            if event.widget == self.entry_title:
                event.widget.insert(0, "QR Kod Adı (örn: Web Sitem)")
            elif event.widget == self.entry_link:
                event.widget.insert(0, "https://ornek.com veya Metniniz")
            event.widget.config(fg='grey')

    def _select_center_image(self):
        """Kullanıcının bir resim dosyası seçmesini sağlar ve dosya adını gösterir (QR kodun ortası için)."""
        file_path = filedialog.askopenfilename(
            title="Bir resim dosyası seçin (QR kod ortası için)",
            filetypes=[("Resim dosyaları", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.selected_center_img_path = file_path
            self.lbl_center_image_info.config(text=f"Seçilen Orta Resim: {os.path.basename(file_path)}")
            self._generate_qr() # Resim seçildiğinde QR kodu yeniden oluştur
        else:
            self.selected_center_img_path = ""
            self.lbl_center_image_info.config(text="Ortadaki resim seçilmedi.")
            self._generate_qr() # Resim seçilmediğinde de QR kodu yeniden oluştur (resimsiz haliyle)


    def _select_background_image(self):
        """Kullanıcının QR kodun arka planı için bir resim dosyası seçmesini sağlar."""
        file_path = filedialog.askopenfilename(
            title="Arka plan resmi seçin",
            filetypes=[("Resim dosyaları", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            self.selected_bg_img_path = file_path
            self.lbl_background_image_info.config(text=f"Seçilen Arka Plan: {os.path.basename(file_path)}")
            self._generate_qr() # Arka plan resmi seçildiğinde QR kodu yeniden oluştur
        else:
            self.selected_bg_img_path = ""
            self.lbl_background_image_info.config(text="Arka plan resmi seçilmedi.")
            self._show_feedback("Arka plan resmi seçilmediği için düz beyaz arka plan kullanıldı.", color=COLOR_TEXT_DARK, bg_color=COLOR_SECONDARY_BG)
            self._generate_qr() # Resim seçilmediğinde de QR kodu yeniden oluştur (düz arka plan ile)

    def _update_image_settings_visibility(self, selected_value):
        """Resim Ayarları seçeneğine göre ilgili resim yükleme bileşenlerini gösterir/gizler ve diğerlerinin konumunu ayarlar."""
        
        # Tüm resim ile ilgili bileşenleri gizle
        self.btn_select_center_img.grid_forget()
        self.lbl_center_image_info.grid_forget()
        self.btn_select_background_img.grid_forget()
        self.lbl_background_image_info.grid_forget()

        # Temel başlangıç satırlarını tanımla
        current_row = 1 

        if selected_value == "Ortadaki Resim":
            self.btn_select_center_img.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=5, padx=5)
            self.lbl_center_image_info.grid(row=current_row + 1, column=0, columnspan=2, sticky="w", pady=2)
            current_row += 2 
            if not self.selected_center_img_path:
                self._show_feedback("Ortadaki resmi seçmek için 'Ortadaki Resmi Seç' düğmesini kullanın.", color=COLOR_TEXT_DARK, bg_color=COLOR_SECONDARY_BG)
        elif selected_value == "Arka Plan Resmi":
            self.btn_select_background_img.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=5, padx=5)
            self.lbl_background_image_info.grid(row=current_row + 1, column=0, columnspan=2, sticky="w", pady=2)
            current_row += 2 
            if not self.selected_bg_img_path:
                self._show_feedback("Arka plan resmi seçmek için 'Arka Plan Resmi Seç' düğmesini kullanın.", color=COLOR_TEXT_DARK, bg_color=COLOR_SECONDARY_BG)
       

        # Diğer elemanların satırlarını dinamik olarak ayarla
        self.lbl_pattern_selection.grid(row=current_row, column=0, sticky="w", pady=5)
        self.pattern_dropdown.grid(row=current_row, column=1, sticky="ew", pady=5, padx=5)
        current_row += 1

        self.lbl_error_correction.grid(row=current_row, column=0, sticky="w", pady=5)
        self.error_correction_dropdown.grid(row=current_row, column=1, sticky="ew", pady=5, padx=5)
        current_row += 1
        
        self.lbl_qr_color.grid(row=current_row, column=0, sticky="w", pady=5)
        current_row += 1

        self.slider_r.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=2)
        current_row += 1
        self.slider_g.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=2)
        current_row += 1
        self.slider_b.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=2)
        
        # Resim ayarları değiştiğinde QR kodunu yeniden oluştur
        if self.base_qr_pil_image: 
            self._generate_qr()


    def _get_qr_save_path(self):
        """Oluşturulan QR kodun kaydedileceği tam yolu döndürür."""
        clean_name = self.qr_code_name.replace(" ", "_").strip()
        if not clean_name or clean_name == "QR_Kod_Adı_(örn:_Web_Sitem)":
            clean_name = "untitled_qr"
        return os.path.join(QR_CODE_SAVE_DIR, f"{clean_name}.png")

    def _display_qr_image(self, pil_image):
        """Pillow Image nesnesini Tkinter PhotoImage'a dönüştürür ve label'da gösterir."""
        try:
            if not os.path.exists(QR_CODE_SAVE_DIR):
                os.makedirs(QR_CODE_SAVE_DIR)

            self.generated_qr_pil_image = pil_image.copy() 
            save_path = self._get_qr_save_path()
            self.generated_qr_pil_image.save(save_path)

            tk_image = ImageTk.PhotoImage(pil_image)
            self.lbl_qr_display.config(image=tk_image)
            self.lbl_qr_display.image = tk_image

            self._show_feedback("QR Kodu başarıyla oluşturuldu ve kaydedildi!", color=COLOR_TEXT_LIGHT, bg_color=COLOR_DARK_ACCENT)

        except Exception as e:
            messagebox.showerror("Kaydetme/Görüntüleme Hatası", f"QR kodu kaydedilirken veya görüntülenirken bir hata oluştu: {e}")
            self._show_feedback(f"Hata: {e}", color=COLOR_TEXT_LIGHT, bg_color=COLOR_ERROR)

    def _process_center_image_for_qr(self, qr_pil_image):
        """Seçilen resmi QR kodun ortasına yerleştirir."""
        if not self.selected_center_img_path:
            return qr_pil_image 

        try:
            img = Image.open(self.selected_center_img_path).convert("RGBA")
            qr_width, qr_height = qr_pil_image.size
            
            target_size = (qr_width // 4, qr_height // 4) 
            img.thumbnail(target_size, Image.LANCZOS) 

            img_pos = ((qr_width - img.size[0]) // 2, (qr_height - img.size[1]) // 2)
            
            temp_qr = qr_pil_image.copy().convert("RGBA") 
            temp_qr.paste(img, img_pos, img) 
            
            return temp_qr.convert("RGB") 
        
        except Exception as e:
            messagebox.showerror("Resim İşleme Hatası", f"Ortadaki resim işlenirken bir hata oluştu: {e}")
            self._show_feedback(f"Ortadaki Resim Hatası: {e}", color=COLOR_TEXT_LIGHT, bg_color=COLOR_ERROR)
            return qr_pil_image.convert("RGB")

    def _apply_background_design(self, qr_image_size):
        """QR kodun arka planına düz renk veya resim uygular."""
        background_type = self.selected_image_setting_var.get()
        img_width, img_height = qr_image_size

        if background_type == "Arka Plan Resmi":
            if self.selected_bg_img_path and os.path.exists(self.selected_bg_img_path):
                try:
                    bg_img = Image.open(self.selected_bg_img_path).convert("RGB")
                    bg_img = bg_img.resize(qr_image_size, Image.LANCZOS)
                    bg_img = bg_img.convert("RGBA")

                    # Yarı saydam beyaz bir katman amaç qr okunurluğunu artırmak
                    alpha_layer = Image.new("RGBA", qr_image_size, (255, 255, 255, 102)) 
                    
                    combined_img = Image.alpha_composite(bg_img, alpha_layer)
                    
                    return combined_img.convert("RGB") 
                    
                except Exception as e:
                    messagebox.showerror("Arka Plan Resmi Hatası", f"Arka plan resmi yüklenirken bir hata oluştu: {e}\nDüz beyaz arka plan kullanılıyor.")
                    self._show_feedback(f"Arka Plan Resmi Hatası: {e}", color=COLOR_TEXT_LIGHT, bg_color=COLOR_ERROR)
                    return Image.new("RGB", (img_width, img_height), "white")
            else:
                self._show_feedback("Arka plan resmi seçilmedi veya bulunamadı. Düz beyaz arka plan kullanıldı.", color=COLOR_TEXT_LIGHT, bg_color=COLOR_ERROR)
                return Image.new("RGB", (img_width, img_height), "white")
        
        # Diğer tüm durumlarda (Yok, Ortadaki Resim) düz beyaz arka plan kullan
        return Image.new("RGB", (img_width, img_height), "white")

    def _generate_qr(self):
        """QR kodu oluşturma işlemini başlatır."""
        self.qr_code_name = self.entry_title.get().strip()
        qr_data = self.entry_link.get().strip()

        if self.qr_code_name == "QR Kod Adı (örn: Web Sitem)" or not self.qr_code_name:
            self._show_feedback("Lütfen geçerli bir QR kod başlığı girin.", color=COLOR_TEXT_LIGHT, bg_color=COLOR_ERROR)
            return
        if qr_data == "https://ornek.com veya Metniniz" or not qr_data:
            self._show_feedback("Lütfen QR kodu için bir bağlantı veya metin girin.", color=COLOR_TEXT_LIGHT, bg_color=COLOR_ERROR)
            return

        self._show_feedback("QR Kodu oluşturuluyor...", color=COLOR_TEXT_LIGHT, bg_color=COLOR_DARK_ACCENT)
        self.master.update_idletasks() 

        try:
            error_correction_level = self.error_correction_levels[self.selected_error_correction.get()]

            qr_instance = qrcode.QRCode(
                version=None, 
                error_correction=error_correction_level,
                box_size=10,
                border=4,
            )
            qr_instance.add_data(qr_data)
            qr_instance.make(fit=True)
            
            self.base_qr_pil_image = qr_instance.make_image(fill_color="black", back_color="white")
            self.base_qr_pil_image = self.base_qr_pil_image.resize(QR_CODE_DISPLAY_SIZE)

            final_qr_image = self._apply_background_design(QR_CODE_DISPLAY_SIZE)

            r = self.slider_r.get()
            g = self.slider_g.get()
            b = self.slider_b.get()
            qr_color = (r, g, b)

            # QR kodun siyah modüllerini seçilen renge boya
            # ve deseni uygula (Kare veya Yuvarlak Noktalar)
            base_pixels_bw = self.base_qr_pil_image.copy().convert("L").load()
            draw_final = ImageDraw.Draw(final_qr_image)
            
            module_approx_size = QR_CODE_DISPLAY_SIZE[0] / self.base_qr_pil_image.width * qr_instance.box_size
            dot_radius_factor = 0.4
            dot_radius = int(module_approx_size * dot_radius_factor)

            for x in range(0, QR_CODE_DISPLAY_SIZE[0], int(module_approx_size)):
                for y in range(0, QR_CODE_DISPLAY_SIZE[1], int(module_approx_size)):
                    center_x = x + int(module_approx_size / 2)
                    center_y = y + int(module_approx_size / 2)

                    if center_x < QR_CODE_DISPLAY_SIZE[0] and center_y < QR_CODE_DISPLAY_SIZE[1]:
                        if base_pixels_bw[center_x, center_y] < 128: 
                            if self.selected_pattern_var.get() == "Yuvarlak Noktalar":
                                draw_final.ellipse((center_x - dot_radius, center_y - dot_radius,
                                                     center_x + dot_radius, center_y + dot_radius),
                                                     fill=qr_color)
                            else: # Kare desen
                                draw_final.rectangle((x, y, x + module_approx_size, y + module_approx_size),
                                                     fill=qr_color)
            
            # Eğer "Ortadaki Resim" seçildiyse resmi QR kodun ortasına ekle
            if self.selected_image_setting_var.get() == "Ortadaki Resim":
                final_qr_image = self._process_center_image_for_qr(final_qr_image)

            self._display_qr_image(final_qr_image)

        except Exception as e:
            messagebox.showerror("Oluşturma Hatası", f"QR kodu oluşturulurken beklenmedik bir hata oluştu: {e}")
            self._show_feedback(f"Hata: {e}", color=COLOR_TEXT_LIGHT, bg_color=COLOR_ERROR)

    def _qr_color_changer(self, event=None):
        """QR kodun rengini değiştirir."""
        if self.base_qr_pil_image is None:
            return

        # Rengi değiştirmeden önce arka planı yeniden uygula (düz renk veya resim)
        colored_final_image = self._apply_background_design(QR_CODE_DISPLAY_SIZE)
        draw_colored_final = ImageDraw.Draw(colored_final_image)

        r = self.slider_r.get()
        g = self.slider_g.get()
        b = self.slider_b.get()
        qr_color = (r, g, b)

        base_pixels_bw = self.base_qr_pil_image.copy().convert("L").load()

        module_approx_size = QR_CODE_DISPLAY_SIZE[0] / self.base_qr_pil_image.width * 10
        dot_radius_factor = 0.4
        dot_radius = int(module_approx_size * dot_radius_factor)

        for x in range(0, QR_CODE_DISPLAY_SIZE[0], int(module_approx_size)):
            for y in range(0, QR_CODE_DISPLAY_SIZE[1], int(module_approx_size)):
                center_x = x + int(module_approx_size / 2)
                center_y = y + int(module_approx_size / 2)

                if center_x < QR_CODE_DISPLAY_SIZE[0] and center_y < QR_CODE_DISPLAY_SIZE[1]:
                    if base_pixels_bw[center_x, center_y] < 128: 
                        if self.selected_pattern_var.get() == "Yuvarlak Noktalar":
                            draw_colored_final.ellipse((center_x - dot_radius, center_y - dot_radius,
                                                         center_x + dot_radius, center_y + dot_radius),
                                                         fill=qr_color)
                        else: # Kare desen
                            draw_colored_final.rectangle((x, y, x + module_approx_size, y + module_approx_size),
                                                         fill=qr_color)

        # Eğer "Ortadaki Resim" seçildiyse resmi QR kodun ortasına ekle
        if self.selected_image_setting_var.get() == "Ortadaki Resim":
            colored_final_image = self._process_center_image_for_qr(colored_final_image)

        self._display_qr_image(colored_final_image)

    def _show_feedback(self, message, color=COLOR_TEXT_LIGHT, bg_color=COLOR_DARK_ACCENT, duration_ms=3000):
        """Kullanıcıya kısa süreli geri bildirim mesajı gösterir."""
        self.lbl_feedback.config(text=message, fg=color, bg=bg_color)
        self.master.after(duration_ms, lambda: self.lbl_feedback.config(text="", bg=COLOR_PRIMARY_BG))

# Uygulamayı başlat
if __name__ == "__main__":
    if not os.path.exists(QR_CODE_SAVE_DIR):
        os.makedirs(QR_CODE_SAVE_DIR)

    root = Tk()
    app = QRCodeGeneratorApp(root)
    root.mainloop()