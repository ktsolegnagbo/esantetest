from datetime import timedelta
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from skill.decorators import logout_required
from .models import AppUser, Question, Timer, UserResponse, Choice
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from skill.functions import notEmpty
from django.http import JsonResponse
from .forms import AppUserForm, LoginForm, UserForm, UserResponseForm, UserResponseFormSet
from django.utils import timezone
from django.db import connection
import subprocess
import json


# def increment_counter(interval=1, max_value=10):
#     i = 0
#     while i < max_value:
#         print(f"i = {i}")
#         i += 1
#         time.sleep(interval)
#     print("Loop finished.")

@logout_required
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        credential = request.POST.get('credential')
        password = request.POST.get('password')
        if credential and password:
            try:
                user = User.objects.get(username=credential)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=credential)
                except User.DoesNotExist:
                    user = None
                    
            if user is not None and user.is_active and form.is_valid():
                user = authenticate(request, username=user.username, password=password)
                login(request, user)
                try:
                    appUser = AppUser.objects.get(id=user.id, user=user)
                except Exception:
                    appUser = AppUser(id=user.id, user=user)
                  
                appUser.save()
                # messages.success(request, _('Connexion réussie!'))
                # return redirect(next_url) if notEmpty(next_url) else HttpResponseRedirect(reverse('home'))
                
                if user.is_superuser:
                    return redirect('home')
                else:
                    if appUser.finished:
                       messages.info(request, _('Test fermé!')) 
                       logout(request)
                    else:
                        return redirect('home')
            else:
                if user and not user.is_active:
                    messages.error(request, _('Connexion non autorisés'))
                else:
                    messages.error(request, _('Infos incorrect.'))
        else: 
            messages.error(request, _('Champs requis!'))
    else:
        form = LoginForm()
        
    return render(request, 'login.html',{ 'form': form })



def get_timer(request):
    user = AppUser.objects.get(user=request.user)
    if user.end_date:
        time_diff = user.end_date - timezone.now()
        total_seconds = time_diff.total_seconds()
        if total_seconds < 0:
            data = {
                'timer': "00h:00m:00s",
                'status': 'finished',
                'seconds': 100
            }
        else:
            hours = int(total_seconds // 3600 ) # 1 hour = 3600 seconds
            minutes = int((total_seconds % 3600) // 60)  # Remaining minutes
            seconds = int(total_seconds % 60)  # Remaining seconds
            
            hours = (f'0{hours}h:' if hours < 10 else f'{hours}h:') if hours > 0 else ''
            minutes = (f'0{minutes}m:' if minutes < 10 else f'{minutes}m:') if minutes > 0 else ''
            seconds = f'0{seconds}' if seconds < 10 else f'{seconds}'

            data = {
                'timer': f"{hours}{minutes}{seconds}s",
                'status': 'success',
                'seconds': int(total_seconds)
            }
    else:
        data = {
            'timer': "No end date set",
            'status': 'failed',
            'seconds': 100
        }

    return JsonResponse(data)

@login_required
def user_logout(request):
    logout(request)
    # messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect(reverse('login'))

# @login_required
# def increment_counter(interval=1, max_value=10):
#     i = 0
#     while i < max_value:
#         print(f"i = {i}")
#         i += 1
#         time.sleep(interval)
#     print("Loop finished.")

@login_required
def home(request):
    try:
        appUser = AppUser.objects.get(user=request.user)
        if appUser.end_date:
            time_diff = appUser.end_date - timezone.now()
            total_seconds = time_diff.total_seconds()
            if total_seconds <= 0:
                return redirect('finish')
            else:
                return redirect('question_view', question_id=1)
            
        timer = Timer.objects.filter(id=1).first()
        if not timer:
            timer = Timer(id=1, hours=1, minutes=5, seconds=1)
            timer.save()
            
        return render(request, 'home.html', {
            'username': appUser.user.username, 
            'first_name': appUser.user.first_name, 
            'last_name': appUser.user.last_name, 
            'email': appUser.user.email,
            'timer': f'{timer.hours}h:{timer.minutes}m:{timer.seconds}s'
        })
    except Exception:
        return redirect('logout')



@login_required
def question_view(request, question_id=None):
    user = AppUser.objects.get(user=request.user)
    if not user.started or not user.end_date:
        
        timer = Timer.objects.filter(id=1).first()
        if not timer:
            timer = Timer(id=1, hours=1, minutes=5, seconds=1)
            timer.save()
            
        current_time = timezone.now()
        user.started = True
        user.finished = False
        user.time_left = 0
        user.end_date = current_time + timedelta(hours=timer.hours, minutes=timer.minutes, seconds=timer.seconds)
        user.save()
    
    time_diff = user.end_date - timezone.now()
    total_seconds = time_diff.total_seconds()
    
    if total_seconds <= 0:
        if not request.user.is_superuser:
                user.finished = True
                user.save()
        return redirect('finish')
        
    question_id = question_id if isinstance(question_id, int) and question_id > 0 else None
    questions =  Question.objects.all()
    questionsLen = len(questions)
    
    try:
        question = Question.objects.get(uid=question_id)
    except Exception:
        question = None
    
    if question_id and question_id is not None and question and question is not None and questionsLen > 0:
        next_question_id = (question_id + 1) if question_id else 1
        
        if question_id <= 0 or question_id > questionsLen:
            return redirect('question_view', question_id=1)
        
        try:
            response = UserResponse.objects.get(question=question, user=request.user)
        except Exception:
            response = UserResponse(question=question, user=request.user)
            
        if request.method == 'POST':
            form = UserResponseForm(request.POST, question=question)
            if form.is_valid():
                
                response.save()
                
                if question.question_type == Question.QCM_U:
                    try:
                        choice_id = form.cleaned_data['choices']
                        if choice_id:
                            choice = Choice.objects.get(id=choice_id)
                            response.choices.set([choice])
                            response.note_qcm = 1 if choice.is_correct else 0
                                
                    except Exception:
                        pass
                elif question.question_type == Question.QCM_M:
                    try:
                        choice_ids = form.cleaned_data.get('choices', [])
                        # choice_ids = form.cleaned_data['choices']
                        if choice_ids:
                            choices = Choice.objects.filter(id__in=choice_ids)
                            total_correct_choices = Choice.objects.filter(question=question, is_correct=True).count()
                            response.choices.set(choices)
                            qcm_score = 0
                            for choice in choices:
                                if choice.is_correct:
                                    qcm_score += 1
                            response.note_qcm = qcm_score / total_correct_choices if total_correct_choices > 0 else 0
                            
                    except Exception:
                        pass
                else:
                    answer = form.cleaned_data['answer']
                    if answer:
                        response.answer=answer
                        
                response.already_done = True
                response.save()
                
                if next_question_id < questionsLen:
                    return redirect('question_view', question_id=next_question_id)
                else:
                    return redirect('finish')
        else:
            try:
                initial_data = {
                    'choices': [c.id for c in response.choices.all()],
                    'answer': response.answer,
                }
            except Exception:
                initial_data = {
                    'choices': [],
                    'answer': question.default
                }
            form = UserResponseForm(initial=initial_data, question=question)
            # form = UserResponseForm(question=question)
            
        context = {
            'form': form,
            'question': question,
            'questions': questions,
            'question_id': question_id,
            'answer': response.answer if response and response.answer else question.default
        }
        
        return render(request, 'question.html', context)
    else:
        return redirect('error')



@login_required
def admin_question_view(request, user_id, question_id):
        
    question_id = question_id if isinstance(question_id, int) and question_id > 0 else None
    user_id = user_id if isinstance(user_id, int) and user_id > 0 else None
    questions =  Question.objects.all()
    questionsLen = len(questions)
    
    
    try:
        question = Question.objects.get(uid=question_id)
        user = AppUser.objects.get(user__id=user_id)
    except Exception:
        question = None
        user = None
    
    if question_id and user_id and question and user and questionsLen > 0:
        next_question_id = (question_id + 1) if question_id else 1
        try:
            user_response = UserResponse.objects.get(user=user.user, question=question)
            initial_data = {
                'choices': [c.id for c in user_response.choices.all()],
                'answer': user_response.answer,
            }
        except Exception:
            user_response = None
            initial_data = {
                'choices': [],
                'answer': question.default
            }
        form = UserResponseForm(initial=initial_data, question=question)
    context = {
        'form': form,
        'question': question,
        'questions': questions,
        'question_id': next_question_id,
        'user_id': user_id,
        'answer': user_response.answer if user_response and user_response.answer else question.default
    }
    
    return render(request, 'admin-question.html', context)
    


@login_required
def execute_python_code(code):
    try:
        with open("user_code.py", "w") as code_file:
            code_file.write(code)
        result = subprocess.run(['python3', 'user_code.py'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return {'status': 'success', 'output': result.stdout}
        else:
            return {'status': 'error', 'message': result.stderr}
    except subprocess.TimeoutExpired:
        return {'status': 'error', 'message': 'Le code a pris trop de temps à s’exécuter.'}

@login_required
@csrf_exempt
def run_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code')
        language = data.get('language')
        script_filename = f'{request.user.username}_temp_script'
        
        

        if language == 'python':
            try:
                # Execute Python code
                with open(f'{script_filename}.py', 'w') as f:
                    f.write(code)
                result = subprocess.run(['python3', f'{script_filename}.py'], capture_output=True, text=True, timeout=10)
                output = result.stdout + result.stderr  # Combine stdout and stderr
            except subprocess.TimeoutExpired:
                output = "The script took too long to run."
            except Exception as e:
               output = f"An error occurred: {e}"
                

        elif language == 'nodejs':
            subprocess.run(["npm", "init", "-y"], check=True)
            # Install Express
            subprocess.run(["npm", "install", "express"], check=True)
            
            # Execute Node.js code
            with open(f'{script_filename}.js', 'w') as f:
                f.write(code)
            result = subprocess.run(['node', f'{script_filename}.js'], capture_output=True, text=True, check=True)
            output = result.stdout + result.stderr  # Combine stdout and stderr

        elif language == 'sql':
            # Execute SQL code safely (only SELECT statements allowed)
            output = execute_sql(code)

        else:
            output = 'Unsupported language.'

        return JsonResponse({'output': output})

    return JsonResponse({'output': 'Invalid request'}, status=400)

@login_required
def execute_sql(query):
    with connection.cursor() as cursor:
        try:
            # Execute the query
            cursor.execute(query)
            # Fetch the rows
            rows = cursor.fetchall()
            # If there are no rows, return an empty result set
            if rows is None:
                return json.dumps([])
            # Get the column names
            if cursor.description is None:
                return "Effectué avec succès!"
                # return "No column description available."
            columns = [col[0] for col in cursor.description]
            # Convert rows to a list of dictionaries
            output = [dict(zip(columns, row)) for row in rows]
            # Return the result as a JSON string
            return json.dumps(output)
        except Exception as e:
            return str(e)  # Return the error message as output

# @login_required
def error(request):
    return render(request, 'error.html')

@login_required
def finish(request):
    user = AppUser.objects.get(user=request.user)
    if user.end_date:
        time_diff = user.end_date - timezone.now()
        total_seconds = time_diff.total_seconds()
        finished = total_seconds <= 0
    else:
        finished = True
    return render(request, 'finish.html', {'finished': finished})


def user_list(request):
    users = AppUser.objects.all()
    user_data = []

    for user in users:
        # Calculate counts for user responses
        resps = UserResponse.objects.filter(user=user.user)
        qcm_count = sum([r.note_qcm for r in resps])
        code_count = sum([r.note_code for r in resps])
        user_data.append({
            'user': user,
            'qcm_count': qcm_count,
            'code_count': code_count,
        })

    return render(request, 'user_list.html', {'user_data': user_data})

def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Form for User details
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        response_formset = UserResponseFormSet(request.POST, queryset=UserResponse.objects.filter(user=user))
        
        if user_form.is_valid() and response_formset.is_valid():
            user_form.save()
            response_formset.save()
            return redirect('user_list')
    else: 
        user_form = UserForm(instance=user)
        response_formset = UserResponseFormSet(queryset=UserResponse.objects.filter(user=user))

    return render(request, 'edit_user.html', {
        'user_form': user_form,
        'response_formset': response_formset,
        'user': user
    })


# def edit_user(request, user_id):
#     user = get_object_or_404(User, id=user_id)
#     app_user = get_object_or_404(AppUser, user=user)

#     if request.method == 'POST':
#         form = AppUserForm(request.POST, instance=app_user)
#         if form.is_valid():
#             form.save()
#             return redirect('user_list')
#     else:
#         form = AppUserForm(instance=app_user)

#     return render(request, 'edit_user.html', {'form': form, 'user': user})

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('user_list')
    
    return render(request, 'delete_user.html', {'user': user})

# @csrf_exempt
# def save_timer(request, question_id):
#     if request.method == 'POST':
#         try:
#             question = get_object_or_404(Question, uid=question_id)
#             data = json.loads(request.body)
#             remaining_time = data.get('remaining_time')
#             if remaining_time and remaining_time is not None:
#                 try:
#                     userResponse = UserResponse.objects.get(question=question, user=request.user)
#                 except Exception:
#                     userResponse = UserResponse(question=question, user=request.user)
                
#                 data = json.loads(request.body)
#                 remaining_time = data.get('remaining_time')
                
#                 time_taken = question.time_limit - (remaining_time if remaining_time > 0 else 0)
                
#                 userResponse.time_taken = time_taken
#                 userResponse.save()
#                 return JsonResponse({'status': 'success'})
#         except Exception:
#             pass

#     return JsonResponse({'status': 'error'}, status=400)

# @login_required
# def question_view0(request, question_id=None):
#     question_id = question_id if isinstance(question_id, int) and question_id > 0 else None
    
#     # if question_id == 1:
#     #     AppUser.objects.get(time_left=)
    
#     if question_id and question_id is not None:
#         questionsLen = Question.objects.count()
        
#         try:
#             question = Question.objects.get(uid=question_id)
#         except Exception:
#             question = None
            
#         if question and question is not None and questionsLen > 0:
#             questions =  Question.objects.all()
#             next_question_id = (question_id + 1) if question_id else 1
            
#             idsList = []
#             for q in questions:
#                 resp = UserResponse.objects.filter(question__uid=q.uid, user=request.user).first()
#                 if resp:
#                     if resp.already_done:
#                         pass
#                     else:
#                         idsList.append(q.uid)
#                 else:
#                     idsList.append(q.uid)
            
#             idsList = sorted(idsList)
                
#             if len(idsList) <= 0 or question_id > questionsLen:
#                 return redirect('finish')
            
#             try:
#                 userResponse = UserResponse.objects.get(question=question, user=request.user)
#             except Exception:
#                 userResponse = UserResponse(question=question, user=request.user, already_done=False)
            
#             if not userResponse.already_done:
#                 if request.method == 'POST':
#                     form = UserResponseForm(request.POST, question=question)
#                     if form.is_valid():
#                         time_taken = int(form.cleaned_data['time_taken'])
#                         if time_taken - 1 <= question.time_limit + 1:
#                             if question.question_type in [Question.QCM_M, Question.QCM_U]:
#                                 choiceId = form.cleaned_data['choice']
#                                 if notEmpty(choiceId):
#                                     try:
#                                         choice = Choice.objects.get(id=form.cleaned_data['choice'])
#                                         userResponse.choice=choice
#                                     except Exception:
#                                         pass
                                    
#                                 userResponse.time_taken=time_taken
#                             else:
#                                 answer = form.cleaned_data['answer']
#                                 # if question.question_type in [Question.PYTHON, Question.NODEJS, Question.SQL]:
#                                 #     # Securely execute the code
#                                 #     result = execute_python_code(answer)
#                                 #     if result['status'] == 'error':
#                                 #         form.add_error('answer', f"Erreur d'exécution: {result['message']}")
#                                 #         # Return to the same page with errors
#                                 #         return render(request, 'question.html', {'form': form, 'question': question, 'start_time': timezone.now()})
#                                 # Save the response if it's not a choice question
#                                 if notEmpty(answer):
#                                     userResponse.answer=answer
                                    
#                             userResponse.time_taken = time_taken
#                             userResponse.already_done = True
#                             userResponse.save()
                            
#                             if next_question_id < questionsLen:
#                                 return redirect('question_view', question_id=next_question_id)
#                             else:
#                                 return redirect('finish')
#                 else:
#                     form = UserResponseForm(question=question)
                    
#                 if userResponse and userResponse.time_taken and userResponse.time_taken <= question.time_limit + 2:
#                     remaining_time = question.time_limit - userResponse.time_taken
#                 else:
#                     remaining_time = question.time_limit
                    
#                 if remaining_time <= 0:
#                     return redirect('question_view', question_id=next_question_id)
                    
                    
#                 context = {
#                     'form': form,
#                     'question': question,
#                     'questions': questions,
#                     'start_time': timezone.now(),
#                     'question_id': question_id,
#                     'user_response': userResponse,
#                     'remaining_time': remaining_time,
#                 }
                
#                 return render(request, 'question.html', context)
            
#             return redirect('question_view', question_id=next_question_id)
#         else:
#             return redirect('error')
#     else:
#         return redirect('error')

# def execute_sql(query):
#     # Check if the query is a SELECT statement
#     # if not query.strip().lower().startswith("select"):
#     #     return "Only SELECT statements are allowed."

#     with connection.cursor() as cursor:
#         try:
#             cursor.execute(query)
#             rows = cursor.fetchall()
#             columns = [col[0] for col in cursor.description]
#             output = [dict(zip(columns, row)) for row in rows]
#             return json.dumps(output)  # Convert to JSON string
#         except Exception as e:
#             return str(e)  # Return the error message as output