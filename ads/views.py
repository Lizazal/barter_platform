from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from .models import Ad, ExchangeProposal
from .forms import AdForm, ExchangeProposalForm
from django.core.paginator import Paginator
from django.db.models import Q


# Только вошедшие пользователи могут создавать объявления
@login_required
def create_ad(request):
    # Обрабатываем отправку формы
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            # Привязка объявления к вошедшему пользователю
            ad.user = request.user
            ad.save()
            return redirect('ads:ad_list')
    # Показываем пустую форму для заполнения
    else:
        form = AdForm()
    return render(request, 'ads/create_ad.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Автоматически войти после регистрации
            login(request, user)
            return redirect('ads:ad_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# Только вошедший пользователь может редактировать обявление
@login_required
def edit_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if ad.user != request.user:
        return HttpResponseForbidden("Вы не можете редактировать это объявление.")
    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            # User уже установлен, поэтому здесь его не добавляем
            form.save()
            return redirect('ads:ad_list')
    else:
        form = AdForm(instance=ad)
    return render(request, 'ads/edit_ad.html', {'form': form, 'ad': ad})


@login_required
def delete_ad(request, ad_id):
    ad = get_object_or_404(Ad, id=ad_id)
    if ad.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить это объявление.")
    if request.method == 'POST':
        ad.delete()
        return redirect('ads:ad_list')
    # Подтверждение удаления
    return render(request, 'ads/confirm_delete.html', {'ad': ad})


def ad_list(request):
    # Ключевые слова
    query = request.GET.get('q', '')
    # Фильтр по категории
    category = request.GET.get('category', '')
    # Фильтр по состоянию
    condition = request.GET.get('condition', '')
    ads = Ad.objects.all().order_by('-created_at')
    if query:
        ads = ads.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category:
        ads = ads.filter(category__iexact=category)
    if condition:
        ads = ads.filter(condition__iexact=condition)
    # 5 объявлений на страницу
    paginator = Paginator(ads, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'ads/ad_list.html', {
        'page_obj': page_obj,
        'query': query,
        'category': category,
        'condition': condition,
    })


# Только вошедший пользователь может создавать предложения
@login_required
def create_proposal(request):
    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            if proposal.ad_sender.user == proposal.ad_receiver.user:
                form.add_error(None, "Нельзя обмениваться с самим собой.")
                return render(request, 'ads/create_proposal.html', {'form': form})
            proposal.status = 'awaits'
            proposal.save()
            return redirect('ads:proposal_list')
    else:
        form = ExchangeProposalForm(user=request.user)
    return render(request, 'ads/create_proposal.html', {'form': form})


# Только вошедший пользователь может обновлять предложения
@login_required
def update_proposal_status(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['accepted', 'rejected']:
            # Только автор объявления-получателя может менять статус
            if proposal.ad_receiver.user == request.user:
                proposal.status = new_status
                proposal.save()
                return redirect('ads:proposal_list')
            else:
                return HttpResponseForbidden("Вы не можете изменить статус.")
    return redirect('ads:proposal_list')


# Только вошедший пользователь может просматривать предложения
@login_required
def proposal_list(request):
    proposals = ExchangeProposal.objects.all().order_by('-created_at')
    # фильтрация
    sender = request.GET.get('sender', '')
    receiver = request.GET.get('receiver', '')
    status = request.GET.get('status', '')
    if sender:
        proposals = proposals.filter(Q(ad_sender__user__username__icontains=sender) |
                                     Q(ad_sender__title__icontains=sender))
    if receiver:
        proposals = proposals.filter(Q(ad_receiver__user__username__icontains=receiver) |
                                     Q(ad_receiver__title__icontains=receiver))
    if status:
        proposals = proposals.filter(status=status)
    return render(request, 'ads/proposal_list.html', {
        'proposals': proposals,
        'sender': sender,
        'receiver': receiver,
        'status': status,
    })


@login_required
def cancel_proposal(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)
    if proposal.status != 'awaits':
        return HttpResponseForbidden("Нельзя отменить принятое или отклонённое предложение.")
    if proposal.ad_sender.user != request.user:
        return HttpResponseForbidden("Вы можете отменить только свои предложения.")
    if request.method == 'POST':
        proposal.delete()
        return redirect('ads:proposal_list')
    return render(request, 'ads/confirm_cancel.html', {'proposal': proposal})
