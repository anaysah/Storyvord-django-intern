from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Task
import json

class TaskAPITestCase(TestCase):
    def setUp(self):
        # Set up test client and users
        self.client = Client()
        
        # Create a normal user
        self.user = User.objects.create_user(username='normaluser', password='testpass123')
        
        # Create an admin user
        self.admin = User.objects.create_user(username='adminuser', password='adminpass123', is_staff=True)
        
        # Generate JWT tokens
        self.user_token = str(RefreshToken.for_user(self.user).access_token)
        self.admin_token = str(RefreshToken.for_user(self.admin).access_token)
        
        # Create some test tasks
        self.task_by_user = Task.objects.create(
            title="User Task", description="Normal user task", created_by=self.user, status='pending', priority='low'
        )
        self.task_by_admin = Task.objects.create(
            title="Admin Task", description="Admin task", created_by=self.admin, status='completed', priority='high'
        )
    
    def test_create_task(self):
        """Test POST /api/tasks/ - Normal user can create a task"""
        data = {'title': 'New Task', 'description': 'Test task', 'status': 'pending', 'priority': 'medium'}
        response = self.client.post(
            '/api/tasks/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 3)  # 2 from setUp + 1 new
        self.assertEqual(response.json()['created_by'], self.user.id)

    def test_list_tasks_normal_user(self):
        """Test GET /api/tasks/ - Normal user sees only their tasks"""
        response = self.client.get(
            '/api/tasks/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tasks = response.json()['results']  # Paginated response
        self.assertEqual(len(tasks), 1)  # Only user's task
        self.assertEqual(tasks[0]['title'], 'User Task')

    def test_list_tasks_admin(self):
        """Test GET /api/tasks/ - Admin sees all tasks"""
        response = self.client.get(
            '/api/tasks/',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tasks = response.json()['results']
        self.assertEqual(len(tasks), 2)  # Both tasks

    def test_retrieve_task(self):
        """Test GET /api/tasks/{id}/ - User can retrieve their task"""
        response = self.client.get(
            f'/api/tasks/{self.task_by_user.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['title'], 'User Task')
    
    def test_another_retrieve_task(self):
        """Test GET /api/tasks/{id}/ - User can not retrieve another users task"""
        response = self.client.get(
            f'/api/tasks/{self.task_by_admin.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_task(self):
        """Test PUT /api/tasks/{id}/ - User can update their task"""
        data = {'title': 'Updated Task', 'description': 'Updated', 'status': 'completed', 'priority': 'high'}
        response = self.client.put(
            f'/api/tasks/{self.task_by_user.id}/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task_by_user.refresh_from_db()
        self.assertEqual(self.task_by_user.status, 'completed')
        self.assertEqual(self.task_by_user.priority, 'high')

    def test_delete_task(self):
        """Test DELETE /api/tasks/{id}/ - User can delete their task"""
        response = self.client.delete(
            f'/api/tasks/{self.task_by_user.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 1)  # Only admin task remains
    
    def test_update_task_not_owner(self):
        """Test PUT /api/tasks/{id}/ - Normal user can't update another's task"""
        data = {'title': 'Unauthorized Update'}
        response = self.client.put(
            f'/api/tasks/{self.task_by_admin.id}/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Not found because other user will not be able to see if any task with that id exist

    def test_delete_task_not_owner(self):
        """Test DELETE /api/tasks/{id}/ - Normal user can't delete another's task"""
        response = self.client.delete(
            f'/api/tasks/{self.task_by_admin.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Not found because other user will not be able to see if any task with that id exist

    def test_admin_update_any_task(self):
        """Test PUT /api/tasks/{id}/ - Admin can update any task"""
        data = {'title': 'Admin Updated Task'}
        response = self.client.put(
            f'/api/tasks/{self.task_by_user.id}/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task_by_user.refresh_from_db()
        self.assertEqual(self.task_by_user.title, 'Admin Updated Task')

    def test_unauthenticated_access(self):
        """Test GET /api/tasks/ - Unauthenticated user is denied"""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_by_status(self):
        Task.objects.create(title="Completed Task", status='completed', priority='medium', created_by=self.user)
        response = self.client.get(
            '/api/tasks/?status=completed', HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tasks = response.json()['results']
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['status'], 'completed')

    def test_filter_by_priority(self):
        response = self.client.get(
            '/api/tasks/?priority=low', HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tasks = response.json()['results']
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['priority'], 'low')

    def test_filter_by_created_date(self):
        """Test GET /api/tasks/?created_at__gte=... - Filter by date range"""
        response = self.client.get(
            '/api/tasks/?created_at__gte=2023-01-01',
            HTTP_AUTHORIZATION=f'Bearer {self.user_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tasks = response.json()['results']
        self.assertEqual(len(tasks), 1)  # Should match setUp task