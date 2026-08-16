from django import forms

from .models import Reservation


class ReservationForm(forms.ModelForm):

    class Meta:
        model = Reservation

        fields = [
            'date',
            'time',
            'guests',
            'comment',
        ]

        widgets = {

            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                }
            ),

            'time': forms.TimeInput(
                attrs={
                    'type': 'time',
                }
            ),

            'guests': forms.NumberInput(
                attrs={
                    'min': 1,
                }
            ),

            'comment': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Дополнительные пожелания'
                }
            ),

        }