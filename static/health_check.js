
const HEALTH_TIMEOUT_MS = 3000;
const DEGRADED_BANNER_ID = 'service-status-banner';
const SUBMIT_BUTTON_SELECTOR = 'button[type="submit"]';

async function checkServiceHealth() {
    console.log("Running service health check...");
    const banner = document.getElementById(DEGRADED_BANNER_ID);

    const submitButton = document.querySelector(SUBMIT_BUTTON_SELECTOR);


    if (submitButton) {
        submitButton.disabled = true;
    }

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), HEALTH_TIMEOUT_MS);

        const response = await fetch("/health", {
            method: 'GET',
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (response.ok) {
            const data = await response.json();
            if (data.status === 'ok') {

                if (submitButton) submitButton.disabled = false;
                if (banner) banner.style.display = 'none';
                return true;
            }
        }

        throw new Error("Service reported non-OK status.");

    } catch (error) {

        console.error("Health check failed (Degraded Mode activated):", error.name);

        if (banner) {
            banner.textContent = "⚠️ Система перевантажена або недоступна. Спробуйте пізніше.";
            banner.style.display = 'block';
        }

        return false;
    }
}

document.addEventListener('DOMContentLoaded', checkServiceHealth);