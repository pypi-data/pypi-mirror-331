import requests
import os
import sys
from PySide6.QtWidgets import QMessageBox
from packaging.version import Version
from .progressbar import LoadingWindow
import verifact.metadata as metadata

class UpdateManager:
    def __init__(self, repo_owner, repo_name, parent=None):
        self.about = parent
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self._file_size = 0
        self._downloaded_size = 0
        self.dir_update = "maj"

    @property
    def file_size(self):
        """Taille du fichier à télécharger."""
        return self._file_size
    
    @file_size.setter
    def file_size(self, value:int):
        if not isinstance(value, int):
            msg = "La taille du fichier doit être un nombre entier"
            raise TypeError(msg)
        self._file_size = value

    @property
    def downloaded_size(self):
        """Taille du fichier téléchargé."""
        return self._downloaded_size

    @downloaded_size.setter
    def downloaded_size(self, value:int):
        if not isinstance(value, int):
            msg = "La taille du fichier doit être un nombre entier"
            raise TypeError(msg)
        self._downloaded_size = value

    @property
    def progress(self):
        """Pourcentage de téléchargement."""
        if self.file_size == 0:
            return 0
        return int(self.downloaded_size / self.file_size * 100)

    def get_latest_release_info(self, extension=".exe"):
        """
        Récupère les informations de la dernière version publiée sur GitHub, 
        y compris le tag et l'URL du fichier .exe.

        Returns:
            tuple: Un tuple contenant le tag de la dernière version et 
            l'URL du fichier .exe, ou (None, None) si une erreur se produit.
        """
        url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
            data = response.json()
            tag_name = data.get("tag_name")
            assets = data.get("assets", [])
            exe_url = None
            for asset in assets:
                if asset.get("name", "").lower().endswith(extension):
                    exe_url = asset.get("browser_download_url")
                    break
            return tag_name, exe_url
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération de la dernière version depuis GitHub : {e}")
            return None, None

    def check_updates(self):
        """
        Vérifie si une mise à jour est disponible.

        Returns:
            bool: True si une mise à jour est disponible, False sinon.
        """
        latest_tag, exe_url = self.get_latest_release_info()
        
        if not latest_tag or not exe_url:
            return False
        
        latest_version = Version(latest_tag.lstrip('v'))
        current_version = Version(metadata.version)

        return latest_version > current_version

    def update_software(self):
        """Met à jour le logiciel en téléchargeant le fichier .exe depuis GitHub."""
        
        print("Mise à jour du logiciel...")
        _, exe_url = self.get_latest_release_info()
        if not exe_url:
            print("Aucun fichier .exe trouvé dans la dernière version.")
            return
        print(f"Téléchargement de la nouvelle version depuis : {exe_url}")
        
        response = requests.get(exe_url, stream=True)
        response.raise_for_status()
        self.file_size = int(response.headers.get("content-length", 0))
        
        # Vérifie si le programme est un exécutable ou un fichier python
        if hasattr(sys, 'frozen'):
            self.old_path = os.path.abspath(sys.executable) # .exe
        else:
            self.old_path = os.path.abspath(__file__) # .py
        
        # Définir le chemin du dossier et du fichier mis à jour
        new_filename = str(os.path.basename(exe_url))
        self.new_filedir = os.path.join(
            os.path.dirname(self.old_path), 
            self.dir_update
            )
        self.new_path = os.path.join(self.new_filedir, new_filename)
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(self.new_filedir, exist_ok=True)
        
        # Affiche la barre de progression
        loading_window = LoadingWindow(self.about)
        loading_window.show()
        
        # Téléchargement du fichier mis à jour
        with open(self.new_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                self.downloaded_size += len(chunk)
                loading_window.update_progress(self.progress)
                print(f"Progression mise à jour : {self.progress}%", end="\r")
        
        loading_window.close()
        print("Téléchargement de la mise à jour terminé.")
    
    def show_file_location_message(self, file_path):
        """Affiche un message informant l'utilisateur de la nouvelle version."""
        msg_box = QMessageBox()
        txt = f"""
        La mise à jour a été téléchargée ici :\n\n{file_path}\n
        Vous pouvez supprimer l'ancienne version.
        """
        msg_box.setWindowTitle("Mise à jour terminée")
        msg_box.setText(txt)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)

        # Afficher le message
        msg_box.exec()

