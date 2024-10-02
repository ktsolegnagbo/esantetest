from django.db import models
from django.contrib.auth.models import User


class Timer(models.Model):
    id = models.AutoField(primary_key=True)
    hours = models.PositiveIntegerField(unique=True, null=False, blank=False, default=0)
    minutes = models.PositiveIntegerField(unique=True, null=False, blank=False, default=0)
    seconds = models.PositiveIntegerField(unique=True, null=False, blank=False, default=0)

class Question(models.Model):
    TEXT = 'text'
    # CODE = 'code'
    PYTHON = 'python'
    NODEJS = 'nodejs'
    SQL = 'sql'
    QCM_M = 'qcm_m'
    QCM_U = 'qcm_u'

    QUESTION_TYPES = [
        (TEXT, 'Texte'),
        (PYTHON, 'Code Python'),
        (NODEJS, 'Code NodeJs'),
        (SQL, 'Code Sql'),
        (QCM_M, 'Choix Multiple'),
        (QCM_U, 'Choix Unique'),
    ]
    uid = models.PositiveIntegerField(unique=True, null=False, blank=False)
    title = models.CharField(max_length=255, default='Question ')
    text = models.TextField(default='')
    default = models.TextField(default='-')
    correction = models.TextField(default='')
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default=TEXT)
    time_limit = models.IntegerField(default=60)  # Temps en secondes (2 à 3 minutes)
    
    @property
    def is_already_done(self):
        objects = UserResponse.objects.filter(question=self, already_done=True)
        return {
            'id': [o.question.uid for o in objects],
            'user': [o.user.id for o in objects]
        }


    def __str__(self):
        return self.text


class Choice(models.Model):
    id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.text} (Correct: {self.is_correct})'


class AppUser(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='app_user')
    time_left = models.PositiveBigIntegerField(default=0, null=False, blank=False)
    started = models.BooleanField(default=False, null=False, blank=False)
    finished = models.BooleanField(default=False, null=False, blank=False)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return  f'{self.user.username}'

class UserResponse(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(blank=True, null=True)  # Pour texte ou code
    # choice = models.ForeignKey(Choice, null=True, blank=True, on_delete=models.SET_NULL)  # Pour QCM
    choices = models.ManyToManyField(Choice, blank=True)
    # multiple_choice = models.TextField(blank=True, null=True)  # Pour texte ou code
    # time_taken = models.IntegerField()  # Temps en secondes pour répondre
    already_done = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    note_qcm = models.PositiveIntegerField(null=False, blank=False, default=0)
    note_code = models.PositiveIntegerField(null=False, blank=False, default=0)
    

    def __str__(self):
        return f'Response by {self.user} to {self.question}'
