from pathlib import Path
from threading import Lock, Thread

from flask import Flask, abort, jsonify, request, send_from_directory
from werkzeug.serving import BaseWSGIServer, make_server


class ServeurWeb:
    def __init__(self, port_http: int = 8080, port_https: int = 8443) -> None:
        self._dossier_web = Path(__file__).resolve().parent
        self._port_http = port_http
        self._port_https = port_https
        self._application = Flask(__name__)
        self._application.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
        self._derniere_image: bytes | None = None
        self._verrou = Lock()
        self._serveurs: list[BaseWSGIServer] = []
        self._threads: list[Thread] = []
        self._configurer_routes()

    def _configurer_routes(self) -> None:
        @self._application.get("/")
        def page_accueil():
            return send_from_directory(self._dossier_web, "index.html")

        @self._application.get("/<path:nom_fichier>")
        def servir_ressource(nom_fichier: str):
            if nom_fichier not in {"style.css", "script.js"}:
                abort(404)
            return send_from_directory(self._dossier_web, nom_fichier)

        @self._application.post("/api/frame")
        def recevoir_image():
            if request.mimetype != "image/jpeg":
                return jsonify(erreur="Le contenu doit être une image JPEG."), 415

            donnees_image = request.get_data()
            if not donnees_image:
                return jsonify(erreur="L'image reçue est vide."), 400

            with self._verrou:
                self._derniere_image = donnees_image
            return jsonify(ok=True)

    def demarrer(self) -> None:
        serveurs = []
        try:
            serveurs.append(
                make_server(
                    "0.0.0.0", self._port_http, self._application, threaded=True
                )
            )
            serveurs.append(
                make_server(
                    "0.0.0.0",
                    self._port_https,
                    self._application,
                    threaded=True,
                    ssl_context="adhoc",
                )
            )
        except OSError:
            for serveur in serveurs:
                serveur.server_close()
            raise

        self._serveurs = serveurs
        self._threads = [
            Thread(target=serveur.serve_forever, daemon=True)
            for serveur in self._serveurs
        ]
        for thread in self._threads:
            thread.start()

    def arreter(self) -> None:
        for serveur in self._serveurs:
            serveur.shutdown()
            serveur.server_close()
        for thread in self._threads:
            thread.join()
        self._serveurs.clear()
        self._threads.clear()

    def derniere_image(self) -> bytes | None:
        with self._verrou:
            return self._derniere_image
