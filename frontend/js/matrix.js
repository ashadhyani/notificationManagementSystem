import { api } from './api.js';
import { openEditModal, openTestSendModal, showToast } from './modals.js';

export async function renderMatrix(containerId, onLogsRefresh) {
    const container = document.getElementById(containerId);
    if (!container) return;

    try {
        container.innerHTML = '<div style="padding: 24px; text-align: center; color: var(--text-muted);">Loading Matrix...</div>';
        const data = await api.getMatrix();
        const triggers = data.triggers || [];
        const channels = data.channels || ['whatsapp', 'email', 'web_push'];

        if (triggers.length === 0) {
            container.innerHTML = '<div style="padding: 24px; text-align: center;">No triggers configured.</div>';
            return;
        }

        let html = `
            <table class="matrix-table">
                <thead>
                    <tr>
                        <th style="width: 22%;">Trigger Event</th>
                        <th>💬 WhatsApp</th>
                        <th>📧 Transactional Email</th>
                        <th>🔔 Web Push (Browser)</th>
                    </tr>
                </thead>
                <tbody>
        `;

        triggers.forEach(trigger => {
            html += `
                <tr>
                    <td class="matrix-trigger-cell">
                        <div class="trigger-name">${escapeHtml(trigger.name)}</div>
                        <div class="trigger-desc">${escapeHtml(trigger.description)}</div>
                        <span class="trigger-tag">Trigger: ${escapeHtml(trigger.code)}</span>
                    </td>
            `;

            channels.forEach(channel => {
                const template = trigger.templates.find(t => t.channel === channel);
                if (!template) {
                    html += `<td><div class="cell-card disabled">Not configured</div></td>`;
                    return;
                }

                const isEnabled = template.is_enabled;
                html += `
                    <td>
                        <div class="cell-card ${isEnabled ? '' : 'disabled'}" id="cell-${template.id}">
                            <div class="cell-header">
                                <div class="channel-pill ${channel}">
                                    <span>${getChannelIcon(channel)}</span>
                                    <span>${getChannelLabel(channel)}</span>
                                </div>
                                <label class="switch" title="Toggle Channel">
                                    <input type="checkbox" ${isEnabled ? 'checked' : ''} data-template-id="${template.id}" class="toggle-switch">
                                    <span class="slider"></span>
                                </label>
                            </div>
                            <div class="cell-preview">
                                ${template.subject ? `<div class="cell-subject">${escapeHtml(template.subject)}</div>` : ''}
                                <div>${escapeHtml(template.body || 'No message configured.')}</div>
                            </div>
                            <div class="cell-actions">
                                <button class="btn btn-secondary btn-sm btn-edit-cell" data-template='${JSON.stringify(template)}'>
                                    ✏️ Edit
                                </button>
                                <button class="btn btn-secondary btn-sm btn-test-cell" data-template='${JSON.stringify(template)}' ${isEnabled ? '' : 'disabled style="opacity: 0.5; cursor: not-allowed;" title="Channel is toggled OFF"'}>
                                    🚀 Test Send
                                </button>
                            </div>
                        </div>
                    </td>
                `;
            });

            html += `</tr>`;
        });

        html += `
                </tbody>
            </table>
        `;

        container.innerHTML = html;

        // Attach event listeners for Toggles
        container.querySelectorAll('.toggle-switch').forEach(input => {
            input.addEventListener('change', async (e) => {
                const templateId = e.target.getAttribute('data-template-id');
                const cell = document.getElementById(`cell-${templateId}`);
                const isChecked = e.target.checked;
                try {
                    const res = await api.toggleTemplate(templateId, isChecked);
                    const nowEnabled = res.template.is_enabled;
                    const testBtn = cell ? cell.querySelector('.btn-test-cell') : null;
                    const editBtn = cell ? cell.querySelector('.btn-edit-cell') : null;

                    if (nowEnabled) {
                        cell.classList.remove('disabled');
                        if (testBtn) {
                            testBtn.removeAttribute('disabled');
                            testBtn.style.opacity = '1';
                            testBtn.style.cursor = 'pointer';
                            testBtn.title = '';
                        }
                    } else {
                        cell.classList.add('disabled');
                        if (testBtn) {
                            testBtn.setAttribute('disabled', 'true');
                            testBtn.style.opacity = '0.5';
                            testBtn.style.cursor = 'not-allowed';
                            testBtn.title = 'Channel is toggled OFF';
                        }
                    }

                    if (testBtn) testBtn.setAttribute('data-template', JSON.stringify(res.template));
                    if (editBtn) editBtn.setAttribute('data-template', JSON.stringify(res.template));

                    showToast(res.message);
                } catch (err) {
                    e.target.checked = !e.target.checked;
                    alert('Failed to toggle template: ' + err.message);
                }
            });
        });

        // Attach event listeners for Edit buttons
        container.querySelectorAll('.btn-edit-cell').forEach(btn => {
            btn.addEventListener('click', () => {
                const template = JSON.parse(btn.getAttribute('data-template'));
                openEditModal(template);
            });
        });

        // Attach event listeners for Test Send buttons
        container.querySelectorAll('.btn-test-cell').forEach(btn => {
            btn.addEventListener('click', () => {
                const template = JSON.parse(btn.getAttribute('data-template'));
                if (template.is_enabled === false) {
                    alert(`Cannot test send: ${template.trigger_name} (${template.channel.toUpperCase()}) is currently toggled OFF. Please switch the toggle ON first.`);
                    return;
                }
                openTestSendModal(template);
            });
        });

    } catch (err) {
        container.innerHTML = `<div style="padding: 24px; color: var(--danger);">Failed to load matrix: ${err.message}</div>`;
    }
}

function getChannelIcon(channel) {
    switch (channel) {
        case 'whatsapp': return '💬';
        case 'email': return '📧';
        case 'web_push': return '🔔';
        default: return '📢';
    }
}

function getChannelLabel(channel) {
    switch (channel) {
        case 'whatsapp': return 'WhatsApp';
        case 'email': return 'Email';
        case 'web_push': return 'Web Push';
        default: return channel;
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
