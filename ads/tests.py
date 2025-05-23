from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Ad, ExchangeProposal
from django.urls import reverse


# Create your tests here.

class AdTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.ad = Ad.objects.create(
            user=self.user,
            title='Телефон',
            description='Смартфон',
            category='Электроника',
            condition='новый'
        )

    def test_create_ad(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ads:create_ad'), {
            'title': 'Книга',
            'description': 'Фантастика',
            'category': 'Книги',
            'condition': 'б/у'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Ad.objects.count(), 2)

    def test_edit_ad(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ads:edit_ad', args=[self.ad.id]), {
            'title': 'Телефон (обновлён)',
            'description': 'Смартфон',
            'category': 'Электроника',
            'condition': 'новый'
        })
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Телефон (обновлён)')

    def test_ad_search(self):
        self.client.login(username='testuser', password='password')
        Ad.objects.create(
            user=self.user,
            title='Редкая книга',
            description='Очень интересная',
            category='Книги',
            condition='б/у'
        )
        response = self.client.get(reverse('ads:ad_list'), {'q': 'Редкая'})
        self.assertContains(response, 'Редкая книга')
        self.assertNotContains(response, 'Телефон')

    def test_delete_ad(self):
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('ads:delete_ad', args=[self.ad.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(id=self.ad.id).exists())


class ExchangeProposalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass1')
        self.user2 = User.objects.create_user(username='user2', password='pass2')
        self.ad1 = Ad.objects.create(user=self.user1, title='Книга', description='...', category='Книги',
                                     condition='новый')
        self.ad2 = Ad.objects.create(user=self.user2, title='Наушники', description='...', category='Электроника',
                                     condition='б/у')

    def test_create_proposal(self):
        self.client.login(username='user1', password='pass1')
        response = self.client.post(reverse('ads:create_proposal'), {
            'ad_sender': self.ad1.id,
            'ad_receiver': self.ad2.id,
            'comment': 'Обмен интересует?'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExchangeProposal.objects.count(), 1)

    def test_reject_self_exchange(self):
        self.client.login(username='user1', password='pass1')
        response = self.client.post(reverse('ads:create_proposal'), {
            'ad_sender': self.ad1.id,
            'ad_receiver': self.ad1.id,
            'comment': '...',
        })
        self.assertIn(response.status_code, [403, 200])
        self.assertEqual(ExchangeProposal.objects.count(), 0)

    def test_accept_proposal(self):
        self.client.login(username='user1', password='pass1')
        proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad1,
            ad_receiver=self.ad2,
            comment='Обмен?',
            status='awaits'
        )
        self.client.logout()
        self.client.login(username='user2', password='pass2')
        response = self.client.post(reverse('ads:update_proposal_status', args=[proposal.id]), {
            'status': 'accepted'
        })
        proposal.refresh_from_db()
        self.assertEqual(proposal.status, 'accepted')
