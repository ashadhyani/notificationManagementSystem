import { api } from './api.js';

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

export async function initWebPush(onStatusChange) {
    const btn = document.getElementById('btn-enable-push');
    if (!btn) return;

    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        btn.textContent = '❌ Web Push Not Supported';
        btn.disabled = true;
        return;
    }

    // Register service worker
    try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('Service Worker registered with scope:', registration.scope);

        // Check if already subscribed
        const existingSub = await registration.pushManager.getSubscription();
        if (existingSub && Notification.permission === 'granted') {
            markSubscribed(btn);
            if (onStatusChange) onStatusChange(true);
            return;
        }
    } catch (err) {
        console.error('Service Worker registration error:', err);
    }

    btn.addEventListener('click', async () => {
        try {
            btn.textContent = '⏳ Enabling Push...';
            btn.disabled = true;

            const permission = await Notification.requestPermission();
            if (permission !== 'granted') {
                btn.textContent = '⚠️ Push Permission Denied';
                btn.disabled = false;
                alert('Please allow notification permissions in your browser to receive push notifications.');
                return;
            }

            const registration = await navigator.serviceWorker.ready;
            const vapidData = await api.getVapidPublicKey();
            const vapidKey = vapidData.vapid_public_key;

            if (!vapidKey) {
                throw new Error('VAPID public key not found on server.');
            }

            const convertedKey = urlBase64ToUint8Array(vapidKey);
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: convertedKey,
            });

            // Send subscription JSON to backend
            const subJson = subscription.toJSON();
            await api.subscribeWebPush(subJson);

            markSubscribed(btn);
            if (onStatusChange) onStatusChange(true);

            // Trigger a welcoming browser notification
            if (Notification.permission === 'granted') {
                new Notification('Web Push Enabled!', {
                    body: 'You are now subscribed to receive real browser push notifications.',
                    icon: 'https://cdn-icons-png.flaticon.com/512/3602/3602145.png',
                });
            }
        } catch (err) {
            console.error('Failed to subscribe Web Push:', err);
            btn.textContent = '🔔 Enable Web Push';
            btn.disabled = false;
            alert('Failed to register browser push subscription: ' + err.message);
        }
    });
}

function markSubscribed(btn) {
    btn.textContent = '✅ Web Push Active';
    btn.classList.add('subscribed');
    btn.disabled = true;
}
