# sitio_web/forms.py

from django import forms
from .models import ProjectUpdate, Message


class ProjectUpdateForm(forms.ModelForm):
    """
    Formulario para que el trabajador registre una actualización de avance
    de un proyecto (porcentaje, comentario e imagen).
    """
    class Meta:
        model = ProjectUpdate
        fields = ['progress_percent', 'comment', 'image']
        widgets = {
            'progress_percent': forms.NumberInput(attrs={
                'min': 0,
                'max': 100,
                'step': 0.01,
            }),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_progress_percent(self):
        value = self.cleaned_data['progress_percent']
        if value < 0 or value > 100:
            raise forms.ValidationError("El porcentaje debe estar entre 0 y 100.")
        return value


class MessageForm(forms.ModelForm):
    """
    Formulario para que el cliente envíe un mensaje sobre un proyecto.
    El receptor lo maneja el sistema (por ahora, pensado para el equipo admin).
    """
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Asunto del mensaje'}),
            'body': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe tu mensaje aquí...'}),
        }

class MessageReplyForm(forms.ModelForm):
    """
    Formulario simple para responder a un mensaje existente (solo cuerpo).
    """
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Escribe tu respuesta al cliente aquí...'
            }),
        }