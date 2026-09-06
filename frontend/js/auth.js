import { api } from './api.js';
import { showToast } from './modals.js';

let currentUser = null;
let onTriggerDispatched = null;

export function initAuth(triggerCallback) {
    onTriggerDispatched = triggerCallback;

    const userBadge = document.getElementById('user-badge');
    const btnUserAction = document.getElementById('btn-user-action');
    const formUserLogin = document.getElementById('form-user-login');
    const formUserRegister = document.getElementById('form-user-register');
    const btnUserLogout = document.getElementById('btn-user-logout');
    const userSessionView = document.getElementById('user-session-view');
    const userAuthForms = document.getElementById('user-auth-forms');
    const activeUserName = document.getElementById('active-user-name');
    const triggerBanner = document.getElementById('live-trigger-banner');

    // Check current user session on load
    checkSession();

    // User Login (Fires 'Login' trigger synchronously)
    if (formUserLogin) {
        formUserLogin.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('login-username').value.trim();
            const password = document.getElementById('login-password').value.trim();
            const phone = document.getElementById('login-phone').value.trim();
            const btn = document.getElementById('btn-submit-login');

            btn.disabled = true;
            btn.textContent = 'Signing in...';

            try {
                const res = await api.login(username, password, phone);
                currentUser = res.user;
                showToast(`🎉 ${res.message}`);
                updateUIState();

                // Show trigger banner and native browser notification
                displayTriggerNotification(res.trigger_fired, res.notifications_dispatched);
                if (window.Notification && Notification.permission === 'granted') {
                    new Notification(`Notification Alert: ${res.trigger_fired.toUpperCase()}`, {
                        body: `Hi ${currentUser?.username || 'User'}, you successfully signed in!`,
                        icon: 'https://cdn-icons-png.flaticon.com/512/3602/3602145.png'
                    });
                }
                if (onTriggerDispatched) onTriggerDispatched();
            } catch (err) {
                alert('Login failed: ' + err.message);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Sign In (Fires Login Trigger)';
            }
        });
    }

    // User Logout (Fires 'Logout' trigger synchronously)
    if (btnUserLogout) {
        btnUserLogout.addEventListener('click', async () => {
            btnUserLogout.disabled = true;
            btnUserLogout.textContent = 'Signing out...';

            try {
                const res = await api.logout();
                showToast(`👋 ${res.message}`);
                currentUser = null;
                updateUIState();

                displayTriggerNotification(res.trigger_fired, res.notifications_dispatched);
                if (window.Notification && Notification.permission === 'granted') {
                    new Notification(`Notification Alert: LOGOUT`, {
                        body: 'You have been safely signed out. See you soon!',
                        icon: 'https://cdn-icons-png.flaticon.com/512/3602/3602145.png'
                    });
                }
                if (onTriggerDispatched) onTriggerDispatched();
            } catch (err) {
                alert('Logout error: ' + err.message);
            } finally {
                btnUserLogout.disabled = false;
                btnUserLogout.textContent = 'Sign Out (Fires Logout Trigger)';
            }
        });
    }

    // User Register
    if (formUserRegister) {
        formUserRegister.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('reg-username').value.trim();
            const email = document.getElementById('reg-email').value.trim();
            const password = document.getElementById('reg-password').value.trim();
            const btn = document.getElementById('btn-submit-reg');

            btn.disabled = true;
            btn.textContent = 'Registering...';

            try {
                const res = await api.register(username, email, password);
                showToast(`✅ Registered ${res.user.username}! Please sign in now.`);
                formUserRegister.reset();
                document.getElementById('login-username').value = username;
                document.getElementById('login-password').focus();
            } catch (err) {
                alert('Registration failed: ' + err.message);
            } finally {
                btn.disabled = false;
                btn.textContent = 'Create User Account';
            }
        });
    }

    async function checkSession() {
        try {
            const data = await api.getCurrentUser();
            if (data.authenticated) {
                currentUser = data.user;
            } else {
                currentUser = null;
            }
            updateUIState();
        } catch (err) {
            currentUser = null;
            updateUIState();
        }
    }

    function updateUIState() {
        if (currentUser) {
            userBadge.innerHTML = `
                <span class="user-dot"></span>
                <span>User: <strong>${escapeHtml(currentUser.username)}</strong> ${currentUser.is_staff ? '(Admin)' : ''}</span>
            `;
            userAuthForms.style.display = 'none';
            userSessionView.style.display = 'block';
            activeUserName.textContent = currentUser.username;
        } else {
            userBadge.innerHTML = `
                <span class="user-dot" style="background: #9CA3AF; box-shadow: none;"></span>
                <span>Not signed in</span>
            `;
            userAuthForms.style.display = 'grid';
            userSessionView.style.display = 'none';
        }
    }

    function displayTriggerNotification(triggerCode, dispatchedChannels) {
        if (!triggerBanner) return;

        let channelBadges = (dispatchedChannels || []).map(ch => {
            const color = ch.status === 'SENT' ? '#10B981' : '#EF4444';
            return `<span style="display:inline-block; margin-right: 6px; padding: 2px 6px; border-radius: 4px; background: rgba(255,255,255,0.1); color: ${color}; font-weight:600;">${ch.channel.toUpperCase()}: ${ch.status}</span>`;
        }).join('');

        triggerBanner.innerHTML = `
            <div style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(99, 102, 241, 0.4); border-radius: 12px; padding: 14px 18px; margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <div style="font-weight: 700; color: #A5B4FC; font-size: 14px;">⚡ Real Event Trigger Fired: [${triggerCode.toUpperCase()}]</div>
                    <div style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">Synchronously dispatched to enabled channels:</div>
                </div>
                <div>${channelBadges || 'No active channels'}</div>
            </div>
        `;

        triggerBanner.style.display = 'block';
        setTimeout(() => {
            triggerBanner.style.display = 'none';
        }, 8000);
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
