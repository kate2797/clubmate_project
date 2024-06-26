from datetime import datetime

from django.contrib.auth import authenticate
from django.test import TestCase
from django.urls import reverse

from clubmate.forms import RatingDetailForm, RateDetailForm, UserProfileForm, UserForm
from clubmate.models import Club, Rating, UserProfile, User


class ClubModelTests(TestCase):
    def setUp(self):
        Club.objects.get_or_create(name='Test', club_description='Test', city='Test',
                                   website_url='https://swg3.tv/',
                                   genre='Test', location_coordinates='Test', opening_hours_week='Test',
                                   opening_hours_weekend='Test')[0].save()

    def test_ensure_min_entry_free_is_zero(self):
        """ Ensures that the default value for entry fee is zero. """
        club = Club.objects.get_or_create(name='Test')[0]
        self.assertEqual((club.entry_fee == 0.0), True)


class UserProfileModelTests(TestCase):
    def setUp(self):
        User.objects.create_user('myusername', 'myusername@myusername.com', 'mypassword').save()

    def test_custom_user_is_created_correctly(self):
        """ Tests the correctness of custom user creation. """
        user = User.objects.get(id=1)
        clubmate_user = UserProfile(user=user)
        clubmate_user.bio = 'this is my bio'
        clubmate_user.is_club_owner = True
        clubmate_user.save()
        self.assertEqual(clubmate_user.bio, 'this is my bio')  # Access one of the custom fields


class UserModelTest(TestCase):
    def test_creating_superuser(self):
        """ Tests the correctness of superusercreation. """
        user = User.objects.create_superuser('group33', 'group33@group33.com', 'group33')
        self.assertIsNotNone(user)


class ClubDetailViewTests(TestCase):
    def setUp(self):
        Club.objects.get_or_create(name='Test', club_description='Test', city='Test',
                                   website_url='https://swg3.tv/',
                                   genre='Test', location_coordinates='Test', opening_hours_week='Test',
                                   opening_hours_weekend='Test')[0].save()

    def test_club_detail_club_does_not_exist(self):
        """ If no categories exist, the appropriate message should be displayed. """
        response = self.client.get(reverse('clubmate:club_detail', kwargs={'club_id': 1000}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'The specified club does not exist')
        self.assertIsNone(response.context['club'])

    def test_get_absolute_url(self):
        club = Club.objects.get(id=1)
        self.assertEqual(club.get_absolute_url(), '/club_detail/1/')  # The club must be found under this URL


class DiscoverViewTests(TestCase):
    def setUp(self):
        Club.objects.get_or_create(name='Inn Deep', club_description='Test', city='Test',
                                   website_url='https://swg3.tv/',
                                   genre='Test', location_coordinates='Test', opening_hours_week='Test',
                                   opening_hours_weekend='Test')[0].save()

        Club.objects.get_or_create(name='SWG3', club_description='Test', city='Test',
                                   website_url='https://swg3.tv/',
                                   genre='Test', location_coordinates='Test', opening_hours_week='Test',
                                   opening_hours_weekend='Test')[0].save()

    def test_clubs_display_correctly_on_discover(self):
        """ Checks if clubs are correctly retrieved from the database on Discover. """
        count = Club.objects.count()
        self.assertEqual(count, 2)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('clubmate:discover'))  # Test that reverse naming works
        self.assertEqual(response.status_code, 200)


class IndexViewTests(TestCase):
    def test_index_subheading(self):
        """ Checks if the HTML subheading of the homepage is correctly displayed. """
        response = self.client.get(reverse('clubmate:index'))
        subheading = '<h4 class="mt-3 mb-3">Student clubbing made fun, safe and easy 🥤</h4>' in response.content.decode()
        self.assertTrue(subheading)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('clubmate:index'))
        self.assertEqual(response.status_code, 200)


class AboutViewTests(TestCase):
    def about_display(self):
        """ Checks if the HTML of the about page is correctly displayed. """
        response = self.client.get(reverse('clubmate:about'))
        heading = '<h1>About</h1>' in response.content.decode()
        content = 'ClubMate also intends to help club owners get their clubs noticed' in response.content.decode()
        self.assertTrue(heading)
        self.assertTrue(content)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('clubmate:about'))
        self.assertEqual(response.status_code, 200)


class LoginViewTests(TestCase):
    def setUp(self):
        User.objects.create_user('myusername', 'myusername@myusername.com', 'mypassword').save()

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('clubmate:log_in'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """ Checks if correct template is returned. """
        response = self.client.get(reverse('clubmate:log_in'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'clubmate/login.html')

    def test_authentication_valid(self):
        u = authenticate(username='myusername', password='mypassword')
        self.assertIsNotNone(u)

    def test_authentication_invalid(self):
        u = authenticate(username='test', password='mypassword')  # Credentials do not match any user, None returned
        self.assertIsNone(u)


class FormsTests(TestCase):
    """ A test class checking a proper creation of the website's forms. """

    def test_rating_detail_form_is_being_created(self):
        self.assertIsNotNone(RatingDetailForm())

    def test_rate_detail_form_is_being_created(self):
        self.assertIsNotNone(RateDetailForm())

    def test_user_profile_form_is_being_created(self):
        self.assertIsNotNone(UserProfileForm())

    def test_user_form_is_being_created(self):
        self.assertIsNotNone(UserForm())


class RatingTests(TestCase):
    def setUp(self):
        test_club = Club.objects.get_or_create(name='testClub', club_description='Test', city='Test',
                                               website_url='https://swg3.tv/',
                                               genre='Test', location_coordinates='Test', opening_hours_week='Test',
                                               opening_hours_weekend='Test')[0]
        test_club.save()
        test_club2 = Club.objects.get_or_create(name='testClub2', club_description='Test2', city='Test2',
                                                website_url='https://swg3.tv/',
                                                genre='Test', location_coordinates='Test2', opening_hours_week='Test2',
                                                opening_hours_weekend='Test2')[0]
        test_club2.save()
        test_user = User.objects.get_or_create(name='testUser', email='text@text.com', password='testtesttest',
                                               date_join=datetime.date.today(), is_staff=False)[0]
        test_user2 = User.objects.get_or_create(name='testUser2', email='text2@text.com', password='testtesttest2',
                                                date_join=datetime.date.today(), is_staff=False)[0]
        test_user.save()
        test_user2.save()

        test_user_profile = UserProfile.objects.get_or_create(user=test_user, is_club_owner=False)[0]
        test_user_profile2 = UserProfile.objects.get_or_create(user=test_user2, is_club_owner=False)[0]
        test_user_profile.save()
        test_user_profile2.save()

        test_club_rating1 = Rating.objects.get_or_create(title='testRating1', club=test_club, author=test_user_profile,
                                                         rating_score=3.5, is_safe=True,
                                                         user_commentary='texttesttesttest',
                                                         number_of_upvotes=0)[0]

        test_club_rating2 = \
            Rating.objects.get_or_create(title='testRating2', club=test_club2, author=test_user_profile2,
                                         rating_score=4, is_safe=True,
                                         user_commentary='texttesttesttest2',
                                         number_of_upvotes=0)[0]
        test_club_rating1.save()
        test_club_rating2.save()

    def text_rating_author_match_correctly_to_club_rating_content(self):
        count = Rating.objects.count()
        test_user_content = User.objects.get_or_create(name='testUser')[0]
        test_profile_content = UserProfile.objects.get_or_create(user=test_user_content)[0]

        test_user_content2 = User.objects.get_or_create(name='testUser2')[0]
        test_profile_content2 = UserProfile.objects.get_or_create(user=test_user_content2)[0]

        club = Club.objects.get_or_create(name='testClub')[0]
        club2 = Club.objects.get_or_create(name='testClub2')[0]

        test_rating_content1 = Rating.objects.get_or_create(title='testRating1')[0]
        test_rating_content2 = Rating.objects.get_or_create(title='testRating2')[0]

        self.assertEqual(count, 2)
        self.assertEqual(test_rating_content1.club, club)
        self.assertEqual(test_rating_content1.author, test_profile_content)
        self.assertEqual(test_rating_content2.club, club2)
        self.assertEqual(test_rating_content2.author, test_profile_content2)


class RatingDetailTests(TestCase):
    def setUp(self):
        test_club = Club.objects.get_or_create(name='testClub', club_description='Test', city='Test',
                                               website_url='https://swg3.tv/',
                                               genre='Test', location_coordinates='Test', opening_hours_week='Test',
                                               opening_hours_weekend='Test')[0]
        test_club.save()

    def invalid_club(self):
        response = self.client.get(reverse('clubmate:rate_detail', kwargs={'club_id': 51515151}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid Club')
        self.assertIsNone(response.context['club'])

    def normal_club(self):
        response = self.client.get(reverse('clubmate:rate_detail', kwargs={'club_id': 1}))
        heading = 'Rate testClub' in response.content.decode()
        self.assertTrue(heading)
