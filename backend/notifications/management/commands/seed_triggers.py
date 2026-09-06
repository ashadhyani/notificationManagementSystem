from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from notifications.models import Trigger, NotificationTemplate

class Command(BaseCommand):
    help = 'Seeds strictly 2 triggers (Login, Logout) and 6 templates (2x3 matrix) plus default admin.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding triggers, templates, and admin user...")

        # 1. Create or update default Admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@notifications.com',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created or not admin_user.check_password('admin12345'):
            admin_user.set_password('admin12345')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created/Updated admin user: admin / admin12345"))

        # 2. Define strictly 2 triggers
        triggers_data = [
            {
                'code': 'login',
                'name': 'Login',
                'description': 'Fires immediately when a user signs in on the website.',
                'templates': {
                    'whatsapp': {
                        'subject': 'Login Alert',
                        'body': 'Hi {{user_name}}, welcome back! You successfully signed in at {{time}}.',
                    },
                    'email': {
                        'subject': 'Welcome Back, {{user_name}}!',
                        'body': 'Hello {{user_name}},\n\nYou have logged into your account at {{time}}.\nIf this was not you, please secure your account immediately.\n\nBest regards,\nNotification Team',
                    },
                    'web_push': {
                        'subject': 'Welcome Back!',
                        'body': 'Hi {{user_name}}, you are now signed in to Notification System.',
                    },
                }
            },
            {
                'code': 'logout',
                'name': 'Logout',
                'description': 'Fires immediately when a user signs out of the website.',
                'templates': {
                    'whatsapp': {
                        'subject': 'Sign Out Alert',
                        'body': 'Hi {{user_name}}, you have successfully logged out at {{time}}. See you soon!',
                    },
                    'email': {
                        'subject': 'You Have Logged Out, {{user_name}}',
                        'body': 'Hello {{user_name}},\n\nYou were signed out of your account on {{time}}.\nThank you for visiting!\n\nBest regards,\nNotification Team',
                    },
                    'web_push': {
                        'subject': 'Logged Out',
                        'body': 'You have been safely signed out. See you soon!',
                    },
                }
            },
        ]

        # 3. Populate triggers & templates
        for t_data in triggers_data:
            trigger, _ = Trigger.objects.update_or_create(
                code=t_data['code'],
                defaults={
                    'name': t_data['name'],
                    'description': t_data['description'],
                }
            )

            for channel, tpl_data in t_data['templates'].items():
                tpl, tpl_created = NotificationTemplate.objects.update_or_create(
                    trigger=trigger,
                    channel=channel,
                    defaults={
                        'is_enabled': True,
                        'subject': tpl_data['subject'],
                        'body': tpl_data['body'],
                    }
                )
                self.stdout.write(f"  -> Template [{trigger.name} - {channel}]: {'Created' if tpl_created else 'Updated'}")

        self.stdout.write(self.style.SUCCESS("Successfully seeded triggers and templates! (2 rows x 3 columns = 6 cells)"))
