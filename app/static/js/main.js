// Fonction pour ajouter un log
function addLog(message, type = "info") {
  const logContainer = document.getElementById("logContainer");

  // Retirer le placeholder si présent
  const placeholder = logContainer.querySelector(".log-placeholder");
  if (placeholder) {
    placeholder.remove();
  }

  const logEntry = document.createElement("p");
  logEntry.className = `log-entry ${type}`;

  const timestamp = new Date().toLocaleTimeString("fr-FR");
  logEntry.textContent = `[${timestamp}] ${message}`;

  logContainer.appendChild(logEntry);
  logContainer.scrollTop = logContainer.scrollHeight;
}

// Gestionnaire du bouton d'envoi
document.addEventListener("DOMContentLoaded", function () {
  const sendBtn = document.getElementById("sendBtn");

  if (sendBtn) {
    sendBtn.addEventListener("click", async function () {
      // Désactiver le bouton
      sendBtn.disabled = true;
      sendBtn.textContent = "Envoi en cours...";

      addLog("🚀 Début de l'envoi des conventions", "info");

      try {
        const response = await fetch("/api/send_conventions", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        });

        const result = await response.json();

        if (result.success) {
          if (result.count === 0) {
            addLog("ℹ️ Aucune convention à envoyer", "info");
          } else {
            addLog(
              `✅ ${result.count} convention(s) envoyée(s) avec succès`,
              "success",
            );
          }

          // Rafraîchir les stats
          refreshStats();
        } else {
          addLog(`❌ Erreur: ${result.error}`, "error");
        }
      } catch (error) {
        addLog(`❌ Erreur réseau: ${error.message}`, "error");
      } finally {
        // Réactiver le bouton
        sendBtn.disabled = false;
        sendBtn.textContent = "Envoyer les Conventions";
      }
    });
  }
});

// Fonction pour rafraîchir les statistiques
async function refreshStats() {
  try {
    const response = await fetch("/api/stats");
    const stats = await response.json();

    // Mettre à jour les chiffres
    const statNumbers = document.querySelectorAll(".stat-number");
    if (statNumbers.length >= 5) {
      statNumbers[0].textContent = stats.total;
      statNumbers[1].textContent = stats.a_generer;
      statNumbers[2].textContent = stats.a_valider;
      statNumbers[3].textContent = stats.a_envoyer;
      statNumbers[4].textContent = stats.envoyes;
    }

    addLog("📊 Statistiques mises à jour", "info");
  } catch (error) {
    addLog(
      `⚠️ Erreur lors de la mise à jour des stats: ${error.message}`,
      "error",
    );
  }
}
