from django import forms
from .models import Departamento

class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Recursos Humanos'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción opcional'}),
        }

from .models import TipoEmpleado

class TipoEmpleadoForm(forms.ModelForm):
    class Meta:
        model = TipoEmpleado
        fields = ['nombre_tipo', 'descripcion']
        widgets = {
            'nombre_tipo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pasante'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del tipo de persona'}),
        }