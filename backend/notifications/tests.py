from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from django.core.management import call_command
from .models import Trigger, NotificationTemplate, NotificationLog

class NotificationSystemTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Seed triggers
        call_command('seed_triggers')
        self.admin_user = User.objects.get(username='admin')
        self.test_user = User.objects.create_user(username='john_doe', password='password123', email='john@example.com')

    def test_seed_command_creates_only_two_triggers(self):
        """Verify that strictly 2 triggers and 6 templates are created."""
        triggers = Trigger.objects.all()
        self.assertEqual(triggers.count(), 2)
        codes = set(triggers.values_list('code', flat=True))
        self.assertEqual(codes, {'login', 'logout'})

        templates = NotificationTemplate.objects.all()
        self.assertEqual(templates.count(), 6) # 2 triggers x 3 channels

    def test_matrix_api_endpoint(self):
        """Verify GET /api/matrix/ returns correct 2x3 matrix structure."""
        response = self.client.get('/api/matrix/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data['channels']), 3)
        self.assertEqual(len(data['triggers']), 2)

    def test_login_fires_trigger_synchronously(self):
        """Verify that logging in synchronously executes the login trigger and creates logs."""
        initial_log_count = NotificationLog.objects.filter(trigger_code='login').count()

        response = self.client.post('/api/auth/login/', {
            'username': 'john_doe',
            'password': 'password123',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['trigger_fired'], 'login')
        self.assertIn('notifications_dispatched', response.json())

        # Check logs created
        new_log_count = NotificationLog.objects.filter(trigger_code='login').count()
        self.assertEqual(new_log_count - initial_log_count, 3) # whatsapp, email, web_push

    def test_logout_fires_trigger_synchronously(self):
        """Verify that logging out synchronously executes the logout trigger."""
        self.client.force_authenticate(user=self.test_user)
        initial_log_count = NotificationLog.objects.filter(trigger_code='logout').count()

        response = self.client.post('/api/auth/logout/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['trigger_fired'], 'logout')

        new_log_count = NotificationLog.objects.filter(trigger_code='logout').count()
        self.assertEqual(new_log_count - initial_log_count, 3)

    def test_template_toggle_skips_disabled_channel(self):
        """Verify toggling OFF a channel skips it during trigger execution."""
        login_trigger = Trigger.objects.get(code='login')
        whatsapp_tpl = NotificationTemplate.objects.get(trigger=login_trigger, channel='whatsapp')

        # Toggle OFF
        toggle_res = self.client.patch(f'/api/templates/{whatsapp_tpl.id}/toggle/')
        self.assertEqual(toggle_res.status_code, status.HTTP_200_OK)
        whatsapp_tpl.refresh_from_db()
        self.assertFalse(whatsapp_tpl.is_enabled)

        # Execute login
        NotificationLog.objects.all().delete()
        self.client.post('/api/auth/login/', {
            'username': 'john_doe',
            'password': 'password123',
        }, format='json')

        # WhatsApp should not have been dispatched
        logs = NotificationLog.objects.filter(trigger_code='login')
        channels_logged = list(logs.values_list('channel', flat=True))
        self.assertNotIn('whatsapp', channels_logged)
        self.assertIn('email', channels_logged)
        self.assertIn('web_push', channels_logged)

    def test_template_update_and_test_send(self):
        """Verify PUT /api/templates/{id}/ and direct test send."""
        tpl = NotificationTemplate.objects.first()
        res = self.client.put(f'/api/templates/{tpl.id}/', {
            'subject': 'Updated Test Subject',
            'body': 'Updated Body with {{user_name}}',
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tpl.refresh_from_db()
        self.assertEqual(tpl.subject, 'Updated Test Subject')

        # Direct test send
        send_res = self.client.post(f'/api/templates/{tpl.id}/test-send/', {
            'recipient': 'test@example.com',
        }, format='json')
        self.assertEqual(send_res.status_code, status.HTTP_200_OK)
        self.assertTrue(send_res.json()['success'])
