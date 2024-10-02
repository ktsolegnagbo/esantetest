from django.contrib import admin
from skill.models import AppUser, Choice, Question, Timer, UserResponse

class TimerAdmin(admin.ModelAdmin):
    'id',
    'hours',
    'minutes',
    'seconds',
    
    
class AppUserAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'id',
        'time_left',
        'started',
        'finished',
        'end_date',
    )

class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'id',
        'uid',
        'text',
        'default',
        'correction',
        'question_type',
        'time_limit',
    )

class ChoiceAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'id',
        'text',
        'is_correct',
    )

class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('user', 'id', 'question', 'answer', 'get_choices', 'already_done', 'submitted_at', 'note_qcm', 'note_code')
    # Make fields searchable
    search_fields = ('user__username', 'question__text')
    # Filter options
    # list_filter = ('already_done', 'submitted_at', 'note_qcm', 'note_code')
    list_filter = ('already_done', 'submitted_at', 'note_qcm', 'note_code')
    # Order the responses by date (most recent first)
    ordering = ('-submitted_at',)
    # Custom method to show multiple choices selected in list view
    def get_choices(self, obj):
        return ", ".join([choice.text for choice in obj.choices.all()])
    # get_choices.short_description = 'Choix'

admin.site.register(Timer, TimerAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(UserResponse, UserResponseAdmin)
admin.site.register(AppUser, AppUserAdmin)

