from django import forms
from .models import AppUser, Question, UserResponse
from django.contrib.auth.models import User
from django.forms import modelformset_factory

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class AppUserForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ['time_left', 'started', 'finished', 'end_date']  # Adjust fields as needed
        widgets = {
            'time_left': forms.NumberInput(attrs={'class': 'form-control'}),
            'started': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'finished': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }
        
class UserResponseForm(forms.Form):
    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None)  # Handle missing 'question' argument
        super(UserResponseForm, self).__init__(*args, **kwargs)

        if question:
            if question.question_type == Question.QCM_U:
                choices = [(choice.id, choice.text) for choice in question.choices.all()]
                self.fields['choices'] = forms.ChoiceField(
                    choices=choices,
                    widget=forms.RadioSelect(attrs={'class': 'no-copy'}),
                    label='Veuillez sélectionner une option:'  # Add your label here
                )
                self.fields['choices'].required = False
            elif question.question_type == Question.QCM_M:
                choices = [(choice.id, choice.text) for choice in question.choices.all()]
                self.fields['choices'] = forms.MultipleChoiceField(
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple(attrs={'class': 'no-copy'}),
                    label='Veuillez sélectionner une ou plusieurs options:'  # Add your label here
                )
                self.fields['choices'].required = False
            else:
                self.fields['answer'] = forms.CharField(
                    widget=forms.Textarea(attrs={'rows': 5, 'cols': 40, 'class': 'no-copy'}),
                    label='Votre réponse:',  # Add your label here
                )
                self.fields['answer'].required = False  # Conditional field

        # Hidden field for time taken
        # self.fields['time_taken'] = forms.IntegerField(widget=forms.HiddenInput())

class FullUserResponseForm(forms.ModelForm):
    class Meta:
        model = UserResponse
        fields = ['question', 'answer', 'choices', 'already_done', 'note_qcm', 'note_code']


UserResponseFormSet = modelformset_factory(
    UserResponse,
    form=FullUserResponseForm,
    fields=['question', 'answer', 'choices', 'already_done', 'note_qcm', 'note_code'],  # Explicitly define fields to include
    # fields=['answer', 'choices', 'note_qcm', 'note_code'],  # Explicitly define fields to include
    extra=0
)

class LoginForm(forms.ModelForm):
    credential = forms.CharField()
    password = forms.CharField()
    
    class Meta():
        model = User
        fields = ['credential', 'password']
        widgets = {
            'credential': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email ou Nom utilisateur',
            }),
            'password': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mot de passe',
            }),
        }
        
        labels = {
            'credential': 'Email ou Nom utilisateur',
            'password': 'Mot de passe',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Définir les champs requis
        self.fields['credential'].required = True
        self.fields['password'].required = True
