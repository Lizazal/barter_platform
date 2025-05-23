from django import forms
from .models import Ad, ExchangeProposal


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'description', 'image_url', 'category', 'condition']


class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposal
        fields = ['ad_sender', 'ad_receiver', 'comment']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # Оставляем в списке ad_sender только объявления пользователя
        self.fields['ad_sender'].queryset = Ad.objects.filter(user=user)
        # Убираем из получателей свои объявления
        self.fields['ad_receiver'].queryset = Ad.objects.exclude(user=user)