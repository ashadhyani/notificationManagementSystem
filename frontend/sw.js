// Web Push Notification Service Worker
self.addEventListener('push', function(event) {
    let data = { title: 'Notification Alert', body: 'New notification received!' };
    
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data.body = event.data.text();
        }
    }

    const title = data.title || 'Notification Alert';
    const options = {
        body: data.body || '',
        icon: data.icon || 'https://cdn-icons-png.flaticon.com/512/3602/3602145.png',
        badge: data.badge || 'https://cdn-icons-png.flaticon.com/512/3602/3602145.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            { action: 'open', title: 'Open App' },
            { action: 'close', title: 'Dismiss' }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(function(clientList) {
            for (let i = 0; i < clientList.length; i++) {
                const client = clientList[i];
                if (client.url === '/' && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow('/');
            }
        })
    );
});
