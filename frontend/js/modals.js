import { api } from './api.js';

let activeTemplate = null;
let onMatrixRefresh = null;
let onLogsRefresh = null;

export function initModals(matrixCallback, logsCallback) {
    onMatrixRefresh = matrixCallback;
    onLogsRefresh = logsCallback;

    // Edit Modal Elements
    const editModal = document.getElementById('modal-edit');
    const btnCloseEdit = document.getElementById('btn-close-edit');
    const formEdit = document.getElementById('form-edit-template');
    const tagBtns = document.querySelectorAll('.tag-btn');
    const bodyInput = document.getElementById('edit-body');

    if (btnCloseEdit) {
        btnCloseEdit.addEventListener('click', () => {
            editModal.classList.remove('active');
        });
    }

    // Dynamic Tag insertion
    tagBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tag = btn.getAttribute('data-tag');
            const start = bodyInput.selectionStart;
            const end = bodyInput.selectionEnd;
            const text = bodyInput.value;
            bodyInput.value = text.substring(0, start) + tag + text.substring(end);
            bodyInput.focus();
            bodyInput.selectionStart = bodyInput.selectionEnd = start + tag.length;
        });
    });

    // Save Template
    if (formEdit) {
        formEdit.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!activeTemplate) return;

            const btnSave = document.getElementById('btn-save-template');
            btnSave.disabled = true;
            btnSave.textContent = 'Saving...';

            try {
                const subject = document.getElementById('edit-subject').value;
                const body = bodyInput.value;
                await api.updateTemplate(activeTemplate.id, subject, body);

                showToast(`✅ ${activeTemplate.trigger_name} ${activeTemplate.channel} template updated!`);
                editModal.classList.remove('active');
                if (onMatrixRefresh) onMatrixRefresh();
            } catch (err) {
                alert('Failed to update template: ' + err.message);
            } finally {
                btnSave.disabled = false;
                btnSave.textContent = 'Save Changes';
            }
        });
    }

    // Test Send Modal Elements
    const testModal = document.getElementById('modal-test-send');
    const btnCloseTest = document.getElementById('btn-close-test');
    const formTest = document.getElementById('form-test-send');

    if (btnCloseTest) {
        btnCloseTest.addEventListener('click', () => {
            testModal.classList.remove('active');
        });
    }

    if (formTest) {
        formTest.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!activeTemplate) return;

            const btnSend = document.getElementById('btn-execute-test');
            const resultBox = document.getElementById('test-result-box');
            const recipient = document.getElementById('test-recipient').value.trim();

            btnSend.disabled = true;
            btnSend.textContent = 'Sending Test...';
            resultBox.className = 'alert-box';
            resultBox.style.display = 'none';

            try {
                const res = await api.testSendTemplate(activeTemplate.id, recipient);
                resultBox.className = 'alert-box success';
                resultBox.textContent = `🚀 Success: ${res.message}`;
                resultBox.style.display = 'block';

                showToast(`Test sent via ${activeTemplate.channel}!`);
                if (onLogsRefresh) onLogsRefresh();
            } catch (err) {
                resultBox.className = 'alert-box error';
                resultBox.textContent = `❌ Error: ${err.message}`;
                resultBox.style.display = 'block';
            } finally {
                btnSend.disabled = false;
                btnSend.textContent = 'Send Test Notification';
            }
        });
    }
}

export function openEditModal(template) {
    activeTemplate = template;
    const modal = document.getElementById('modal-edit');
    document.getElementById('edit-modal-title').textContent = `Edit Template: ${template.trigger_name} (${template.channel.toUpperCase()})`;
    document.getElementById('edit-subject').value = template.subject || '';
    document.getElementById('edit-body').value = template.body || '';
    modal.classList.add('active');
}

export function openTestSendModal(template) {
    activeTemplate = template;
    const modal = document.getElementById('modal-test-send');
    document.getElementById('test-modal-title').textContent = `Test Send: ${template.trigger_name} (${template.channel.toUpperCase()})`;
    
    const recipientInput = document.getElementById('test-recipient');
    const label = document.getElementById('test-recipient-label');
    const resultBox = document.getElementById('test-result-box');
    resultBox.style.display = 'none';

    if (template.channel === 'whatsapp') {
        label.textContent = 'Recipient Phone Number (with Country Code):';
        recipientInput.placeholder = '+919876543210 (Must be in Meta sandbox list)';
    } else if (template.channel === 'email') {
        label.textContent = 'Recipient Email Address:';
        recipientInput.placeholder = 'your_email@example.com';
    } else {
        label.textContent = 'Web Push Endpoint:';
        recipientInput.placeholder = 'Sends to currently subscribed browser';
    }

    modal.classList.add('active');
}

export function showToast(msg) {
    let toast = document.getElementById('app-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'app-toast';
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3500);
}
