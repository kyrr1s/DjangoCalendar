from django.test import TestCase

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth import logout

from accounts.forms import LoginForm, RegisterForm

User = get_user_model()  # Get the user model

######################################### LOGIN TESTS ##################################3

class loginViewTests(TestCase):
    """ Tests for the Login view """

    def setUp(self):
        self.login_url = reverse('accounts:login')
        self.user = User.objects.create_user(
            username='test@test.com',
            password='testtest1234'
        )

    def test_login_get(self):
        """ Test that the login page loads correctly """
        response = self.client.get(self.login_url)
        
        self.assertEqual(response.status_code, 200) #response == 200
        self.assertIsInstance(response.context['form'], LoginForm) # valid form
        self.assertTemplateUsed(response, 'auth/login.html') #valid template

    def test_login_post_valid_creds(self):
        """ Test login with valid creds """
        valid_creds = {
            'username': 'test@test.com',
            'password': 'testtest1234'
        }
        response = self.client.post(self.login_url, data=valid_creds)
        
        self.assertRedirects(response, reverse('planner:planner')) # redirect to planner
        self.assertEqual(response.wsgi_request.user, self.user) # check if user logged in

    def test_login_post_invalid_creds(self):
        """ Test login with invalid creds """
        invalid_creds = {
            'username': 'testtest@test.com',
            'password1': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data=invalid_creds)
    
        self.assertEqual(response.status_code, 200) # response == 200
        self.assertIsInstance(response.context['form'], LoginForm) #the page should render again
        self.assertFalse(response.wsgi_request.user.is_authenticated) # check if user do not auth

    def test_login_post_no_creds(self):
        """ Test login with no creds """
        response = self.client.post(self.login_url, data={})

        self.assertEqual(response.status_code, 200) # response == 200
        self.assertIsInstance(response.context['form'], LoginForm) #the page should render again
        self.assertFalse(response.wsgi_request.user.is_authenticated) # check if user do not auth

############################################## EXIT TESTS ###########################################33

class exitViewTests(TestCase):
    """ Tests for the exit view """

    def setUp(self):
        self.user = User.objects.create_user(
            username='test@test.com',
            password='testtest1234'
        )
        self.exit_url = reverse('accounts:exit')

    def test_exit_redirect(self):
        """ Test that the user exites correctly """
    
        self.client.login(username='test@test.com', password='testtest1234') #Login

        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200) # user logged in

        response = self.client.get(self.exit_url) # Exit

        self.assertRedirects(response, reverse('accounts:login')) # redirect to Login view

        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)  
        self.assertFalse(response.wsgi_request.user.is_authenticated) # user logged out

    def test_exit_user_without_creds(self):
        """ Test that an anon user without creds can access Exit view """
        response = self.client.get(self.exit_url)
        self.assertRedirects(response, reverse('accounts:login')) # redirect to Login view 

######################################### REGISTER TEST #################################

class registerViewTests(TestCase):
    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')

    def test_register_get(self):
        """ Test that the register page loads correctly """
        response = self.client.get(self.register_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], RegisterForm)
        self.assertTemplateUsed(response, 'auth/register.html')

    def test_register_valid_creds(self):
        """ Test registration with valid creds """
        valid_creds = {
            'username': 'newusertest@example.com',
            'password1': 'newpassword1234',
            'password2': 'newpassword1234'
        }
        response = self.client.post(self.register_url, data=valid_creds)
        
        self.assertRedirects(response, self.login_url) # redirect to Login view
        self.assertTrue(User.objects.filter(username='newusertest@example.com').exists()) # user was succesfully created
        
    def test_register_invalid_creds(self):
        """ Test registration with invalid creds """
        invalid_creds = {
            'username': 'newuser@example.com',
            'password1': '1',
            'password2': '1'
        }
        response = self.client.post(self.register_url, data=invalid_creds)
        
        self.assertEqual(response.status_code, 200) # response == 200
        self.assertIsInstance(response.context['form'], RegisterForm)
        self.assertFalse(User.objects.filter(username='newuser@example.com').exists()) # user was not created

    def test_register_with_different_passwords(self):
        """ Test registration with mismatched passwords """
        mismatched_password_data = {
            'username': 'newuser@test.com',
            'password1': 'password1234',
            'password2': '1234password'
        }
        response = self.client.post(self.register_url, data=mismatched_password_data)
        
        self.assertEqual(response.status_code, 200) # response == 200
        self.assertIsInstance(response.context['form'], RegisterForm)
        self.assertFalse(User.objects.filter(username='newuser@test.com').exists()) # user was not created

    def test_register_existing_username(self):
        """ Test registration with an already used username """
        User.objects.create_user(username='existing@test.com', password='password1234')
        duplicate_username_data = {
            'username': 'existing@test.com',
            'password1': 'newpassword1234',
            'password2': 'newpassword1234'
        }
        response = self.client.post(self.register_url, data=duplicate_username_data)
        
        self.assertEqual(response.status_code, 200) # response == 200
        self.assertIsInstance(response.context['form'], RegisterForm)
        self.assertEqual(User.objects.filter(username='existing@test.com').count(), 1) # user count does not change

        new_user = User.objects.get(username='existing@test.com')
        self.assertTrue(new_user.check_password('password1234')) # check that user password does not changed

# todo: 
# - tests for ProfileForm