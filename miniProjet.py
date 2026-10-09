
from pathlib import Path
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

class Application:

    def __init__(self, root):
        self.root = root
        self.root.title("VisionLab — Filtres et Canny")
        self.root.geometry("1320x800")
        self.root.minsize(1100, 760)
        self.root.configure(bg="#eef2f7")
        self.image = None
        self.resultats = {}
        self.photos = {}
        self.delai = None
        self.filtre = tk.StringVar(value="Gaussien")
        self.noyau = tk.StringVar(value="5 × 5")
        self.seuil_bas = tk.StringVar(value="50")
        self.seuil_haut = tk.StringVar(value="150")
        self.statut = tk.StringVar(
            value="Choisissez une image pour commencer."
        )
        self.creer_interface()
        self.seuil_bas.trace_add("write", self.programmer_traitement)
        self.seuil_haut.trace_add("write", self.programmer_traitement)

    def creer_interface(self):
        
        # Palette conservée depuis le projet original.
        self.bg, self.accent = "#eef2f7", "#a76490"
        self.ink, self.muted = "#39313e", "#756d7c"
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=(12, 9),
                        background="white", foreground=self.ink)
        style.configure("Accent.TButton", background=self.accent, foreground="white")
        style.map("Accent.TButton", background=[("active", "#AF7BB9")])
        style.configure("TRadiobutton", background="white", foreground=self.ink,
                        font=("Segoe UI", 10), padding=4)
        style.configure(
            "TCombobox",
            padding=6,
            fieldbackground="#F3E5EF",
            foreground="#39313e",
            selectbackground="#F3E5EF",
            selectforeground="#39313e",
            background="#a76490",
            arrowcolor="white"
        )

        style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", "#F3E5EF")
            ],
            foreground=[
                ("readonly", "#39313e")
            ],
            selectbackground=[
                ("focus", "#F3E5EF"),
                ("!focus", "#F3E5EF")
            ],
            selectforeground=[
                ("focus", "#39313e"),
                ("!focus", "#39313e")
            ]
        )
        style.configure("TSpinbox", padding=6)
        style.configure("TNotebook", background=self.bg, borderwidth=0)
        style.configure("TNotebook.Tab", padding=(18, 10), font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", "#a76490")],
                  foreground=[("selected", "white")])
        header = tk.Frame(self.root, bg=self.accent, padx=24, pady=16)
        header.pack(fill="x")
        brand = tk.Frame(header, bg=self.accent)
        brand.pack(side="left")
        tk.Label(brand, text="VISION LAB", bg=self.accent, fg="white",
                 font=("Segoe UI", 23, "bold")).pack(anchor="w")
        tk.Label(brand, text="Filtrage d’image & détection de contours", bg=self.accent,
                 fg="white", font=("Segoe UI", 10)).pack(anchor="w")
        ttk.Button(header, text="＋  Choisir une image", command=self.choisir_image).pack(side="right")
        body = tk.Frame(self.root, bg=self.bg, padx=18, pady=18)
        body.pack(fill="both", expand=True)
        side = tk.Frame(body, bg="white", width=255, padx=18, pady=16)
        side.pack(side="left", fill="y", padx=(0, 18))
        side.pack_propagate(False)
        def label(text, size=10, color=None, bold=False):
            w = tk.Label(side, text=text, bg="white", fg=color or self.ink,
                         font=("Segoe UI", size, "bold" if bold else "normal"),
                         justify="left", anchor="w", wraplength=215)
            w.pack(fill="x", pady=(0, 6))
            return w
        def section(text):
            tk.Frame(side, bg=self.bg, height=1).pack(fill="x", pady=12)
            label(text, 10, "#B154B1", True)
        label("PARAMÈTRES", 12, self.accent, True)
        label("Ajustez les réglages pour observer les contours.", 9, self.muted)
        section("01   FILTRE DE LISSAGE")
        for nom in ("Gaussien", "Médian", "Bilatéral","Moyenneur"):
            ttk.Radiobutton(side, text=nom, variable=self.filtre, value=nom,
                            command=self.traiter).pack(anchor="w")
        section("02   TAILLE DU NOYAU")
        choix = ttk.Combobox(side, textvariable=self.noyau,
                            values=[f"{n} × {n}" for n in range(1, 16, 2)],
                            state="readonly", width=16)
        choix.pack(fill="x")
        choix.bind("<<ComboboxSelected>>", self.traiter)
        
        section("03   SEUILS CANNY")
        for titre, variable in (("Seuil bas", self.seuil_bas), ("Seuil haut", self.seuil_haut)):
            row = tk.Frame(side, bg="white")
            row.pack(fill="x", pady=4)
            tk.Label(row, text=titre, bg="white", fg=self.ink,
                     font=("Segoe UI", 10)).pack(side="left")
            ttk.Spinbox(row, from_=0, to=255, textvariable=variable,
                        width=6).pack(side="right")
        
        ttk.Button(side, text="Réinitialiser les réglages", command=self.reinitialiser).pack(fill="x", pady=(10, 6))
        self.export = ttk.Button(side, text="Exporter les contours", style="Accent.TButton",
                                 command=self.exporter, state="disabled")
        self.export.pack(fill="x")
        main = tk.Frame(body, bg=self.bg)
        main.pack(side="left", fill="both", expand=True)
        tk.Label(main, text="Atelier de traitement", bg=self.bg, fg=self.ink,
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        self.info = tk.StringVar(value="Importez une image pour commencer votre analyse.")
        tk.Label(main, textvariable=self.info, bg=self.bg, fg=self.muted,
                 font=("Segoe UI", 10), anchor="w").pack(fill="x", pady=(4, 16))
        tabs = ttk.Notebook(main)
        tabs.pack(fill="both", expand=True)
        self.panneaux = {}
        for tabname, titles in (("Traitement", ("Originale", "Image filtrée", "Contours Canny")),
                                ("Comparaison des 3 filtres", ("Gaussien + Canny", "Médian + Canny", "Bilatéral + Canny"))):
            page = tk.Frame(tabs, bg=self.bg)
            tabs.add(page, text=tabname)
            page.rowconfigure(0, weight=1)
            for col, title in enumerate(titles):
                page.columnconfigure(col, weight=1, uniform="images")
                card = tk.Frame(page, bg="white", padx=8, pady=10)
                card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 8, 0), pady=12)
                tk.Label(card, text=title, bg="white", fg=self.accent,
                         font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(2, 10))
                canvas = tk.Canvas(card, bg="#D9D5DA", highlightthickness=0, width=1, height=1)
                canvas.pack(fill="both", expand=True)
                self.panneaux[title] = canvas
                canvas.bind("<Configure>", lambda e, nom=title: self.afficher(nom))
                tk.Label(card, text="Aperçu proportionnel", bg="white", fg=self.muted,
                         font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 0))
        
        tk.Label(self.root, textvariable=self.statut, anchor="w", bg="white",
                 fg=self.ink, padx=20, pady=10, font=("Segoe UI", 9)).pack(fill="x")

    def reinitialiser(self):
        self.filtre.set("Gaussien")
        self.noyau.set("5 × 5")
        self.seuil_bas.set("50")
        self.seuil_haut.set("150")
        self.traiter()

    def exporter(self):
        if "Contours Canny" not in self.resultats:
            return
        path = filedialog.asksaveasfilename(parent=self.root, title="Exporter les contours",
                    defaultextension=".png", filetypes=[("Image PNG", "*.png")])
        if path:
            try:
                ok, data = cv2.imencode(".png", self.resultats["Contours Canny"])
                if not ok:
                    raise ValueError("Échec de l’encodage PNG.")
                data.tofile(path)
                self.statut.set("Contours exportés : " + Path(path).name)
            except (OSError, ValueError, cv2.error) as err:
                messagebox.showerror("Export impossible", str(err), parent=self.root)

    def choisir_image(self):
        chemin = filedialog.askopenfilename(
            parent=self.root,
            title="Choisir une image",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff"),
                ("Tous les fichiers", "*.*")
            ]
        )
        if not chemin:
            return
        try:
            # Lecture compatible avec les chemins accentués
            donnees = np.fromfile(chemin, dtype=np.uint8)
            nouvelle_image = cv2.imdecode(
                donnees, cv2.IMREAD_COLOR
            )
            if nouvelle_image is None:
                raise ValueError("Impossible de lire cette image.")
            self.image = nouvelle_image
            h, w = self.image.shape[:2]
            self.info.set(f"{Path(chemin).name[:65]}   •   {w} × {h} pixels")
            self.traiter()
        except (OSError, ValueError, cv2.error) as erreur:
            messagebox.showerror(
                "Erreur", str(erreur), parent=self.root
            )

    def programmer_traitement(self, *args):
        # Laisser le temps de saisir une valeur complète
        if self.delai is not None:
            self.root.after_cancel(self.delai)
        self.delai = self.root.after(
            250, self.traiter_apres_delai
        )

    def traiter_apres_delai(self):
        self.delai = None
        self.traiter()

    def traiter(self, event=None):
        if self.image is None:
            return
        self.export.configure(state="disabled")
        try:
            bas = int(self.seuil_bas.get())
            haut = int(self.seuil_haut.get())
        except ValueError:
            self.statut.set(
                "Entrez deux nombres entiers pour les seuils."
            )
            return
        if not (0 <= bas <= haut <= 255):
            self.statut.set(
                "Respectez : 0 ≤ seuil bas ≤ seuil haut ≤ 255."
            )
            return
        taille = int(self.noyau.get().split(" × ")[0])
        filtre = self.filtre.get()
        # 1. Passage en niveaux de gris
        gris = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        # 2. Filtrage / réduction du bruit
        if taille == 1:
            filtree = gris.copy()
        elif filtre == "Gaussien":
            filtree = cv2.GaussianBlur(
                gris, (taille, taille), 0
            )
        elif filtre == "Médian":
            filtree = cv2.medianBlur(gris, taille)
        elif filtre == "Bilatéral":
            filtree = cv2.bilateralFilter(
                gris,
                d=taille,
                sigmaColor=75,
                sigmaSpace=75
            )
        else:
            filtree = cv2.blur(gris, (taille, taille))
        # 3. Détection des contours
        # Canny calcule notamment les gradients en interne.
        contours = cv2.Canny(filtree, bas, haut)
        self.resultats = {
            "Originale": self.image,
            "Image filtrée": filtree,
            "Contours Canny": contours
        }
        # Calculer les trois méthodes sur la même image avec les mêmes réglages.
        operations = {
            "Gaussien": lambda: cv2.GaussianBlur(gris, (taille, taille), 0),
            "Médian": lambda: cv2.medianBlur(gris, taille),
            "Bilatéral": lambda: cv2.bilateralFilter(gris, taille, 75, 75)
        }
        for nom, operation in operations.items():
            base = gris if taille == 1 else operation()
            self.resultats[nom + " + Canny"] = cv2.Canny(base, bas, haut)
        for titre in self.panneaux:
            self.afficher(titre)
        self.export.configure(state="normal")
        self.statut.set(
            f"Filtre : {filtre}   |   Noyau : {taille} × {taille}"
            f"   |   Seuils Canny : {bas} / {haut}"
        )

    def afficher(self, titre):
        canvas = self.panneaux[titre]
        canvas.delete("all")
        largeur = canvas.winfo_width()
        hauteur = canvas.winfo_height()
        if titre not in self.resultats:
            canvas.create_text(
                largeur // 2,
                hauteur // 2,
                text="Choisissez une image",
                fill="#141314",
                font=("Segoe UI", 11)
            )
            return
        image = self.resultats[titre]
        if image.ndim == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image)
        # Adapter l'aperçu sans déformer l'image
        image_pil.thumbnail(
            (max(1, largeur - 12), max(1, hauteur - 12)),
            Image.Resampling.LANCZOS
        )
        photo = ImageTk.PhotoImage(image_pil)
        self.photos[titre] = photo
        canvas.create_image(
            largeur // 2,
            hauteur // 2,
            image=photo,
            anchor="center"
        )

if __name__ == "__main__":
    root = tk.Tk()
    application = Application(root)
    root.mainloop()
