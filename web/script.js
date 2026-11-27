const element_video = document.getElementById("video");
const canevas = document.getElementById("canevas");
const statut = document.getElementById("statut");
let flux_video;
let minuterie_envoi;

async function envoyerImage() {
  if (!flux_video) return;
  if (element_video.readyState < 2) {
    minuterie_envoi = setTimeout(envoyerImage, 200);
    return;
  }

  canevas.width = element_video.videoWidth;
  canevas.height = element_video.videoHeight;
  canevas.getContext("2d").drawImage(element_video, 0, 0);
  const image_binaire = await new Promise((resoudre) =>
    canevas.toBlob(resoudre, "image/jpeg", 0.8)
  );
  if (!image_binaire) {
    minuterie_envoi = setTimeout(envoyerImage, 200);
    return;
  }

  try {
    const reponse = await fetch("/api/frame", {
      method: "POST",
      body: image_binaire,
      headers: {"Content-Type": "image/jpeg"},
    });
    if (!reponse.ok) {
      throw new Error("Le serveur n'a pas accepté l'image.");
    }

    const resultat = await reponse.json();
    if (resultat.qr_valide) {
      arreter_flux_camera();
      statut.textContent = "Code QR détecté : " + resultat.donnees_qr;
      return;
    }
  } catch (erreur) {
    arreter_flux_camera();
    statut.textContent = "Erreur d'envoi de l'image : " + erreur.message;
    return;
  }

  minuterie_envoi = setTimeout(envoyerImage, 200);
}

function arreter_flux_camera() {
  clearTimeout(minuterie_envoi);
  if (flux_video) {
    flux_video.getTracks().forEach((piste) => piste.stop());
  }
  flux_video = null;
  element_video.srcObject = null;
}

async function demarrer_detection() {
  if (flux_video) return;

  if (!window.isSecureContext || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    statut.textContent = "L'accès à la caméra nécessite HTTPS ou localhost.";
    return;
  }

  try {
    flux_video = await navigator.mediaDevices.getUserMedia({
      video: {facingMode: {ideal: "environment"}},
      audio: false,
    });
    element_video.srcObject = flux_video;
    statut.textContent = "Recherche d'un code QR...";
    envoyerImage();
  } catch (erreur) {
    statut.textContent = "Camera access failed: " + erreur.message;
  }
}

document.getElementById("demarrer").onclick = demarrer_detection;
window.addEventListener("pagehide", arreter_flux_camera);