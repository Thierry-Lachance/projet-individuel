const elementVideo = document.getElementById("video");
const canevas = document.getElementById("canevas");
const statut = document.getElementById("statut");
let fluxVideo;

async function envoyerImage() {
  if (!fluxVideo || elementVideo.readyState < 2) return;
  canevas.width = elementVideo.videoWidth;
  canevas.height = elementVideo.videoHeight;
  canevas.getContext("2d").drawImage(elementVideo, 0, 0);
  const donneesImage = await new Promise((resoudre) =>
    canevas.toBlob(resoudre, "image/jpeg", 0.8)
  );
  if (donneesImage) {
    await fetch("/api/frame", {
      method: "POST",
      body: donneesImage,
      headers: {"Content-Type": "image/jpeg"},
    });
  }
}

async function demarrerDetection() {
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
    statut.textContent = "Streaming to the desktop app";
    setInterval(envoyerImage, 100);
  } catch (erreur) {
    statut.textContent = "Camera access failed: " + erreur.message;
  }
}

document.getElementById("demarrer").onclick = demarrerDetection;