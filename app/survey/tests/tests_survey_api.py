# user/tests/test_user_api.py
from django.test import TestCase
from django.contrib.auth.models import User
from core.models import Survey
from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from datetime import date, timedelta
from dateutil.parser import parse as parse_datetime
from survey.serializers import SurveySerializer


SURVEY_LIST_URL = reverse('survey:surveys-list')


def create_user(**params):
    return User.objects.create(**params)


def create_survey(user, **params):
    default = {
        'title': 'Sample Title',
        'description': 'Sample Description',
        'created_by': user,
        'created_at': date.today()
    }
    default.update(params)
    return Survey.objects.create(**default)


class PublicArticleApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_create(self):
        """Test unauthorized creation returns error."""
        payload = {
            'title': 'Unauthorized',
            'description': 'Should not work',
            'created_at': date.today()
        }
        res = self.client.post(SURVEY_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_surveys(self):
        """Test everyone can list surveys."""
        user = create_user(
            username='user1',
            email='u1@example.com',
            password='pass1234',
        )
        create_survey(user, title='Survey 1')
        create_survey(user, title='Survey 2')

        res = self.client.get(SURVEY_LIST_URL)
        surveys = Survey.objects.all().order_by('-created_at')
        serializer = SurveySerializer(surveys, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_list_surveys_pagination(self):
        """Test that surveys list is paginated"""
        user = create_user(
            username='user1',
            email='u1@example.com',
            password='pass1234',
        )
        for i in range(15):
            create_survey(user=user, title=f"Survey {i}")
        res = self.client.get(SURVEY_LIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('results', res.data)
        self.assertLessEqual(len(res.data['results']), 10)  # default PAGE_SIZE

    def test_list_surveys_ordered_by_created_at(self):
        """Test surveys are returned ordered by created_at descending"""
        user = create_user(
            username='user1',
            email='u1@example.com',
            password='pass1234',
        )
        s1 = create_survey(user=user, title="Older")
        s2 = create_survey(user=user, title="Newer")
        s1.created_at = s2.created_at - timedelta(hours=1)
        s1.save()

        res = self.client.get(SURVEY_LIST_URL)
        titles = [s['title'] for s in res.data['results']]
        self.assertEqual(titles, ['Newer', 'Older'])


class PrivateSurveyApiTest(APITestCase):
    def setUp(self):
        self.user = create_user(
            username='researcher1',
            email='r1@example.com',
            password='strongpass123'
        )
        self.user.profile.role = 'researcher'
        self.user.profile.save()

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_survey_successful(self):
        """Test creating a survey as authenticated researcher"""
        payload = {
            'title': 'EEG Brain Study',
            'description': 'Study to measure brain response in smokers.',
        }
        res = self.client.post(SURVEY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Survey.objects.count(), 1)
        survey = Survey.objects.first()
        self.assertEqual(survey.title, payload['title'])
        self.assertEqual(survey.created_by, self.user)

    def test_create_survey_invalid_data(self):
        """Test that invalid payload results in a 400 error"""
        payload = {
            'title': '',  # required but empty
            'description': '',
        }
        res = self.client.post(SURVEY_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Survey.objects.count(), 0)

    def test_update_own_survey(self):
        """Test authorized update of article."""
        survey = create_survey(user=self.user, title='Original title')
        url = reverse('survey:surveys-detail', args=[survey.id])
        payload = {'title': 'Updated title'}
        res = self.client.patch(url, payload)
        survey.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(survey.title, payload['title'])

    def test_update_other_user_survey_error(self):
        """Test unauthorized updated of article returns error."""
        new_user = create_user(
            username='other',
            email='other@example.com',
            password='pass'
        )
        survey = create_survey(user=new_user)
        url = reverse('survey:surveys-detail', args=[survey.id])
        res = self.client.patch(url, {'title': 'Hacked'})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_own_survey(self):
        """Test authorized deletion of survey."""
        survey = create_survey(user=self.user)
        url = reverse('survey:surveys-detail', args=[survey.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Survey.objects.filter(id=survey.id).exists())

    def test_delete_other_user_survey_error(self):
        """Test unauthorized deletion of survey returns error."""
        new_user = create_user(
            username='other',
            email='other@example.com',
            password='pass'
        )
        survey = create_survey(user=new_user)
        url = reverse('survey:surveys-detail', args=[survey.id])
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Survey.objects.filter(id=survey.id).exists())

    def test_retrieve_survey_detail(self):
        """Test authorized retrieve of survey return the correct details."""
        survey = create_survey(user=self.user)
        url = reverse('survey:surveys-detail', args=[survey.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], survey.title)
        self.assertEqual(res.data['description'], survey.description)
        self.assertEqual(
            parse_datetime(res.data['created_at']),
            survey.created_at
        )

    def test_only_researcher_can_create_survey(self):
        """Test that only users with role 'researcher' can create surveys"""

        # Create a subject user
        subject_user = create_user(
            username='subject1',
            email='subject@example.com',
            password='testpass123'
        )

        # Assign subject role to profile
        subject_user.profile.role = 'subject'
        subject_user.profile.save()

        self.client.force_authenticate(user=subject_user)

        payload = {
            'title': 'Should Not Work',
            'description': 'Only researchers can post this',
        }

        res = self.client.post(SURVEY_LIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Survey.objects.count(), 0)
