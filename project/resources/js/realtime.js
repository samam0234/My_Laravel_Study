import Echo from 'laravel-echo';
import Pusher from 'pusher-js';
let echo;
export function disconnect() { echo?.disconnect(); echo = undefined; }
export function connect(auth, onNotification) {
    disconnect();
    if (!import.meta.env.VITE_REVERB_APP_KEY) return;
    echo = new Echo({
        broadcaster: 'reverb', client: undefined, Pusher,
        key: import.meta.env.VITE_REVERB_APP_KEY,
        wsHost: import.meta.env.VITE_REVERB_HOST || window.location.hostname,
        wsPort: Number(import.meta.env.VITE_REVERB_PORT || 8080),
        wssPort: Number(import.meta.env.VITE_REVERB_PORT || 443),
        forceTLS: (import.meta.env.VITE_REVERB_SCHEME || 'http') === 'https',
        enabledTransports: ['ws', 'wss'],
        authorizer: channel => ({
            authorize(socketId, callback) {
                auth.request('/api/broadcasting/auth', { method: 'POST', body: JSON.stringify({ socket_id: socketId, channel_name: channel.name }) })
                    .then(data => callback(null, data)).catch(error => callback(error, null));
            },
        }),
    });
    echo.private(`App.Models.User.${auth.user.id}`).notification(onNotification);
}
