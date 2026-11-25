const elementVideo = document.getElementById("video");
const canevas = document.getElementById("canevas");
const statut = document.getElementById("statut");
let fluxVideo;
let minuterieEnvoi;

async function envoyerImage() {
  if (!fluxVideo) return;
  if (elementVideo.readyState < 2) {
    minuterieEnvoi = setTimeout(envoyerImage, 200);
    return;
  }

  canevas.width = elementVideo.videoWidth;
  canevas.height = elementVideo.videoHeight;
  canevas.getContext("2d").drawImage(elementVideo, 0, 0);
  const blobImage = await new Promise((resoudre) =>
    canevas.toBlob(resoudre, "image/jpeg", 0.8)
  );
  if (!blobImage) {
    minuterieEnvoi = setTimeout(envoyerImage, 200);
    return;
  }

  try {
    const reponse = await fetch("/api/frame", {
      method: "POST",
      body: blobImage,
      headers: {"Content-Type": "image/jpeg"},
    });
    if (!reponse.ok) {
      throw new Error("Le serveur n'a pas accepté l'image.");
    }

    const resultat = await reponse.json();
    if (resultat.qr_valide) {
      arreterFluxCamera();
      statut.textContent = "Code QR détecté : " + resultat.donnees_qr;
      return;
    }
  } catch (erreur) {
    arreterFluxCamera();
    statut.textContent = "Erreur d'envoi de l'image : " + erreur.message;
    return;
  }

  minuterieEnvoi = setTimeout(envoyerImage, 200);
}

function arreterFluxCamera() {
  clearTimeout(minuterieEnvoi);
  if (fluxVideo) {
    fluxVideo.getTracks().forEach((piste) => piste.stop());
  }
  fluxVideo = null;
  elementVideo.srcObject = null;
}

async function demarrerDetection() {
  if (fluxVideo) return;

  if (!window.isSecureContext || !navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    statut.textContent = "L'accès à la caméra nécessite HTTPS ou localhost.";
    return;
  }

  try {
    fluxVideo = await navigator.mediaDevices.getUserMedia({
      video: {facingMode: {ideal: "environment"}},
      audio: false,
    });
    elementVideo.srcObject = fluxVideo;
    statut.textContent = "Recherche d'un code QR...";
    envoyerImage();
  } catch (erreur) {
    statut.textContent = "Camera access failed: " + erreur.message;
  }
}

document.getElementById("demarrer").onclick = demarrerDetection;
window.addEventListener("pagehide", arreterFluxCamera);