import json
from pathlib import Path

class Settings():
    def __init__(self):
        self._client_root = "C"
        self._min_occurrences = 3
        self._case_insensitive = True
        self._auto_update = True
        self._logs = ("VE", "VT")
    
    @property
    def client_root(self):
        """Racine des comptes clients du fichier d'import"""
        return self._client_root
    
    @client_root.setter
    def client_root(self, value):
        self._client_root = str(value)

    @property
    def min_occurrences(self):
        """Nombre minimum d'occurences pour considérer une séquence valide."""
        return self._min_occurrences

    @min_occurrences.setter
    def min_occurrences(self, value):
        if not isinstance(value, int):
            return
        elif value < 1:
            return
        self._min_occurrences = value

    @property
    def case_insensitive(self):
        """Indique si la recherche est insensible ou non aux majuscules."""
        return self._case_insensitive

    @case_insensitive.setter
    def case_insensitive(self, value):
        if not isinstance(value, bool):
            return
        self._case_insensitive = value

    @property
    def auto_update(self):
        """Indique si les mises à jour sont recherchées au démarrage."""
        return self._auto_update

    @auto_update.setter
    def auto_update(self, value):
        if not isinstance(value, bool):
            return
        self._auto_update = value
        
    @property
    def logs(self):
        """Codes journaux à conserver dans le fichier d'import"""
        return self._logs
    
    @logs.setter
    def logs(self, value):
        if isinstance(value, tuple):
            self._logs = value
        if isinstance(value, str):
            self._logs = (value)
        if isinstance(value, list):
            self._logs = tuple(value)

    def path_save(self):
        """Renvoie le chemin du fichier de sauvegarde."""
        file = "verifact_parameters.json"
        folder = "Atem83"
        path_file = Path.home() / "Documents" / folder / file
        return path_file

    def save(self):
        """Enregistre les paramètres dans un fichier de configuration."""
        settings = {
            "client_root": self.client_root,
            "min_occurrences": self.min_occurrences,
            "case_insensitive": self.case_insensitive,
            "auto_update": self.auto_update,
            "logs": self.logs
            }
        path_file = self.path_save()

        try:
            # Crée le dossier "Verifact" s'il n'existe pas
            path_folder = Path(path_file).parent
            path_folder.mkdir(parents=True, exist_ok=True)

            # Ecris ma sauvegarde
            with open(path_file, "w", encoding='utf-8') as file:
                json.dump(settings, file, indent=4, ensure_ascii=False)
        except:
            print("Impossible de sauvegarder les paramètres.")

    def load(self):
        """Charge les paramètres du fichier de configuration."""
        path_file = self.path_save()
        try:
            with open(path_file, "r", encoding='utf-8') as file:
                settings = json.load(file)
                self.client_root = settings["client_root"]
                self.min_occurrences = settings["min_occurrences"]
                self.case_insensitive = settings["case_insensitive"]
                self.auto_update = settings["auto_update"]
                self.logs = settings["logs"]
        except:
            print("Impossible de charger les paramètres.")
