from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from users.models import UserProfile, ShelterProfile
from pets.models import Pet, AdoptionRequest, DeliveryPartner, DeliveryRequest

class Phase51DeliveryTestMatrix(TestCase):
    def setUp(self):
        self.client = Client()

        # Shelter A
        self.shelter_user_a = User.objects.create_user(username='shelter_a', password='Password123!', email='shelter_a@kindheart.org')
        UserProfile.objects.create(user=self.shelter_user_a, role='SHELTER', is_active=True, is_verified=True, verification_status='VERIFIED')
        self.shelter_profile_a = ShelterProfile.objects.create(user=self.shelter_user_a, shelter_name='Shelter Alpha', location='Kochi', verification_status='VERIFIED')

        # Shelter B
        self.shelter_user_b = User.objects.create_user(username='shelter_b', password='Password123!', email='shelter_b@kindheart.org')
        UserProfile.objects.create(user=self.shelter_user_b, role='SHELTER', is_active=True, is_verified=True, verification_status='VERIFIED')
        self.shelter_profile_b = ShelterProfile.objects.create(user=self.shelter_user_b, shelter_name='Shelter Beta', location='Trivandrum', verification_status='VERIFIED')

        # Adopter User
        self.adopter_user = User.objects.create_user(username='adopter1', password='Password123!', email='adopter1@gmail.com')
        UserProfile.objects.create(user=self.adopter_user, role='ADOPTER', is_active=True)

        # Pets
        self.pet1 = Pet.objects.create(shelter=self.shelter_profile_a, name='Bruno', species='Dog', breed='Labrador', age=2)
        self.pet2 = Pet.objects.create(shelter=self.shelter_profile_a, name='Luna', species='Cat', breed='Persian', age=1)

        # Delivery Partner for Shelter A (Rahul)
        self.rahul_user = User.objects.create_user(username='rahul_driver', password='Password123!', first_name='Rahul', last_name='Kumar')
        UserProfile.objects.create(user=self.rahul_user, role='DELIVERY', is_active=True)
        self.rahul_partner = DeliveryPartner.objects.create(
            user=self.rahul_user,
            partner_id='DP-2001',
            shelter=self.shelter_profile_a,
            phone='+91 98470 11111',
            vehicle_number='KL-07-CD-1001',
            is_active=True
        )

        # Delivery Partner for Shelter B (Suresh)
        self.suresh_user = User.objects.create_user(username='suresh_driver', password='Password123!', first_name='Suresh', last_name='Nair')
        UserProfile.objects.create(user=self.suresh_user, role='DELIVERY', is_active=True)
        self.suresh_partner = DeliveryPartner.objects.create(
            user=self.suresh_user,
            partner_id='DP-2002',
            shelter=self.shelter_profile_b,
            phone='+91 98470 22222',
            vehicle_number='KL-01-AB-2002',
            is_active=True
        )

        # Adoption Request 1 (Shelter A)
        self.adopt_req1 = AdoptionRequest.objects.create(
            shelter=self.shelter_profile_a,
            pet=self.pet1,
            customer=self.adopter_user,
            status='APPROVED'
        )
        self.deliv_req1 = DeliveryRequest.objects.create(
            adoption_request=self.adopt_req1,
            status='UNASSIGNED'
        )

        # Adoption Request 2 (Shelter A)
        self.adopt_req2 = AdoptionRequest.objects.create(
            shelter=self.shelter_profile_a,
            pet=self.pet2,
            customer=self.adopter_user,
            status='APPROVED'
        )
        self.deliv_req2 = DeliveryRequest.objects.create(
            adoption_request=self.adopt_req2,
            status='UNASSIGNED'
        )

    def test_01_normal_assignment(self):
        """Test 1: Normal assignment of available driver"""
        self.client.force_login(self.shelter_user_a)
        response = self.client.post(
            '/users/api/shelter/assign-delivery/',
            data={'adoption_id': self.adopt_req1.id, 'partner_id': self.rahul_partner.user.id},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))

        self.deliv_req1.refresh_from_db()
        self.assertEqual(self.deliv_req1.status, 'ASSIGNED')
        self.assertEqual(self.deliv_req1.delivery_partner, self.rahul_partner)
        self.assertEqual(self.rahul_partner.get_availability_status(), 'BUSY')

    def test_02_busy_driver_rejection(self):
        """Test 2: Reject second active assignment when driver is busy"""
        # Assign Rahul to Order 1
        self.deliv_req1.delivery_partner = self.rahul_partner
        self.deliv_req1.status = 'ASSIGNED'
        self.deliv_req1.save()

        # Try assigning Rahul to Order 2
        self.client.force_login(self.shelter_user_a)
        response = self.client.post(
            '/users/api/shelter/assign-delivery/',
            data={'adoption_id': self.adopt_req2.id, 'partner_id': self.rahul_partner.user.id},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get('success'))

        self.deliv_req2.refresh_from_db()
        self.assertEqual(self.deliv_req2.status, 'UNASSIGNED')
        self.assertIsNone(self.deliv_req2.delivery_partner)
        self.assertEqual(self.rahul_partner.get_availability_status(), 'BUSY')

    def test_03_delivery_completion(self):
        """Test 3: Completing delivery makes order DELIVERED/COMPLETED and driver AVAILABLE"""
        self.deliv_req1.delivery_partner = self.rahul_partner
        self.deliv_req1.status = 'OUT_FOR_DELIVERY'
        self.deliv_req1.save()

        self.client.force_login(self.rahul_user)
        response = self.client.post(
            '/users/api/delivery/update-status/',
            data={'delivery_id': self.deliv_req1.id, 'status': 'COMPLETED'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))

        self.deliv_req1.refresh_from_db()
        self.assertEqual(self.deliv_req1.status, 'COMPLETED')
        self.assertEqual(self.rahul_partner.get_availability_status(), 'AVAILABLE')

    def test_04_all_drivers_busy(self):
        """Test 4: When all drivers are busy, delivery order stays UNASSIGNED"""
        self.deliv_req1.delivery_partner = self.rahul_partner
        self.deliv_req1.status = 'ASSIGNED'
        self.deliv_req1.save()

        # All drivers for Shelter A are busy
        available_drivers = DeliveryPartner.objects.filter(shelter=self.shelter_profile_a, is_active=True)
        available_list = [dp for dp in available_drivers if dp.is_available_for_assignment()]
        self.assertEqual(len(available_list), 0)
        self.assertEqual(self.deliv_req2.status, 'UNASSIGNED')

    def test_05_cross_shelter_assignment_rejection(self):
        """Test 5: Shelter A cannot assign driver belonging to Shelter B"""
        self.client.force_login(self.shelter_user_a)
        response = self.client.post(
            '/users/api/shelter/assign-delivery/',
            data={'adoption_id': self.adopt_req1.id, 'partner_id': self.suresh_partner.user.id},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.json().get('success'))

    def test_06_persistence_after_refresh(self):
        """Test 7: Verify database state persists after assignment"""
        self.client.force_login(self.shelter_user_a)
        self.client.post(
            '/users/api/shelter/assign-delivery/',
            data={'adoption_id': self.adopt_req1.id, 'partner_id': self.rahul_partner.user.id},
            content_type='application/json'
        )
        # Fetch profile page
        response = self.client.get('/users/profile/')
        self.assertEqual(response.status_code, 200)

        self.deliv_req1.refresh_from_db()
        self.assertEqual(self.deliv_req1.status, 'ASSIGNED')
        self.assertEqual(self.rahul_partner.get_availability_status(), 'BUSY')
