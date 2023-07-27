from django.views import View
from django.http import JsonResponse, HttpRequest
from django.forms.models import model_to_dict
import json
from django.contrib.auth.models import User
from .models import Task
from django.contrib.auth import authenticate
from base64 import b64decode


class UsersView(View):
    def get(self, request: HttpRequest, pk=None):
        if pk is None:
            users = User.objects.all()
            users_list = [model_to_dict(user, fields=['id', 'username']) for user in users]
            return JsonResponse(users_list, safe=False)
        else:
            try:
                user = User.objects.get(pk=pk)
                user_dict = model_to_dict(user, fields=['id', 'username'])
                return JsonResponse(user_dict)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
            
    def post(self, request: HttpRequest):
        data = request.body.decode('utf-8')
        data = json.loads(data)
        try:
            user = User.objects.create_user(username=data['username'], password=data['password'])
            user_dict = model_to_dict(user, fields=['id', 'username'])
            return JsonResponse(user_dict, status=201)
        except KeyError:
            return JsonResponse({'error': 'Invalid data'}, status=400)
        
    def put(self, request: HttpRequest, pk=None):
        if pk is None:
            return JsonResponse({'error': 'Invalid request'}, status=400)
        try:
            user = User.objects.get(pk=pk)
            data = request.body.decode('utf-8')
            data = json.loads(data)
            user.username = data['username']
            user.save()
            user_dict = model_to_dict(user, fields=['id', 'username'])
            return JsonResponse(user_dict)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except KeyError:
            return JsonResponse({'error': 'Invalid data'}, status=400)

    def delete(self, request: HttpRequest, pk=None):
        if pk is None:
            return JsonResponse({'error': 'Invalid request'}, status=400)
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return JsonResponse({'status': 'ok'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)



class TasksView(View):
    def get(self, request: HttpRequest, pk=None) -> JsonResponse:
        data = request.body.decode('utf-8')
        if data:
            data = json.loads(data)
        else:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        try:
            user = User.objects.get(pk=data['user_id'])
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except KeyError:
            return JsonResponse({'error': 'Invalid data'}, status=400)
            
        if pk is None:
            tasks = Task.objects.filter(author=user)
            tasks_list = [model_to_dict(task, fields=['id', 'title', 'completed']) for task in tasks]
            return JsonResponse(tasks_list, safe=False)
        else:
            try:
                task = Task.objects.get(pk=pk, author=user)
                task_dict = model_to_dict(task, fields=['id', 'title', 'completed'])
                return JsonResponse(task_dict)
            except Task.DoesNotExist:
                return JsonResponse({'error': 'Task not found'}, status=404)

    def post(self, request: HttpRequest) -> JsonResponse:
        data = request.body.decode('utf-8')
        data = json.loads(data)

        try:
            user = User.objects.get(pk=data['user_id'])
            task = Task.objects.create(title=data['title'], description=data.get('description', ''), author=user)
            task.save()
            return JsonResponse(model_to_dict(task, fields=['id', 'title', 'completed']))
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except KeyError:
            return JsonResponse({'error': 'Invalid data'}, status=400)
    
    
    def put(self, request: HttpRequest, pk: int) -> JsonResponse:
        data = request.body.decode('utf-8')
        data = json.loads(data)

        try:
            user = User.objects.get(pk=data['user_id'])
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except KeyError:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        try:
            task = Task.objects.get(id=pk, author=user)
        except Task.DoesNotExist:
            return JsonResponse({'error': 'Task not found'}, status=404)

        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.completed = data.get('completed', task.completed)

        task.save()
        return JsonResponse(model_to_dict(task, fields=['id', 'title', 'completed']))

    def delete(self, request: HttpRequest, pk: int) -> JsonResponse:
        data = request.body.decode('utf-8')
        data = json.loads(data)

        try:
            user = User.objects.get(pk=data['user_id'])
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except KeyError:
            return JsonResponse({'error': 'Invalid data'}, status=400)

        try:
            task = Task.objects.get(author=user, id=pk)
            task.delete()
            return JsonResponse({'status': 'deleted task'}, status=204)
        except Task.DoesNotExist:
            return JsonResponse({'error': 'Task not found'}, status=404)
        

class LoginView(View):
    def post(self, request: HttpRequest) -> JsonResponse:

        headers = request.headers

        if headers.get('Content-Type') != 'application/json':
            return JsonResponse({'error': 'Invalid Content-Type'}, status=400)

        authorization = headers.get('Authorization')
        if authorization is None:
            return JsonResponse({'error': 'No authorization header'}, status=401)

        authorization = authorization.split(' ')
        
        if len(authorization) != 2:
            return JsonResponse({'error': 'Invalid authorization header'}, status=401)
        
        if authorization[0] != 'Basic':
            return JsonResponse({'error': 'Invalid authorization header'}, status=401)

        username, password = b64decode(authorization[1]).decode('utf-8').split(':')

        try:
            user: User = authenticate(username=username, password=password)

            if user is not None:
                return JsonResponse({'status': 'ok'})
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except KeyError:
            return JsonResponse({'error': 'Invalid data'}, status=400)
