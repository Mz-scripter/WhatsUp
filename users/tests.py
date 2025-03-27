from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class UserAppTests(TestCase):
    def test_registration_with_invalid_data(self):
        """
        Test that registration fails with invalid or missing data.
        """
        # Test with missing password
        response = self.client.post(reverse('register'), {'username': 'testuser'})
        self.assertEqual(User.objects.count(), 0)
        self.assertContains(response, 'This field is required.')
        
        # Test with duplicate usernames
        User.objects.create_user('testuser', 'test@gmail.com', 'password123')
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'password1': 'password123',
            'password2': 'password123'
        })
        self.assertEqual(User.objects.count(), 1)
        self.assertContains(response, 'A user with that username already exists.')
    
    def test_successful_login(self):
        """
        Test that a user can log in with correct credentials.
        """
        User.objects.create_user('testuser', 'test@gmail.com', 'password123')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'password123'
        })
        self.assertIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, reverse('chat_list'))
        
    def test_login_with_incorrect_credentials(self):
        """
        Test that login fails with incorrect credentials
        """
        User.objects.create_user('testuser', 'test@gmail.com', 'password123')
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertContains(response, 'Invalid username or password.')
    
    def test_successful_logout(self):
        """
        Test that a logged-in user can logout
        """
        User.objects.create_user('testuser', 'test@gmail.com', 'password123')
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, reverse('login'))