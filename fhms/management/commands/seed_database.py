"""
Django management command to generate test data.

Usage: python manage.py seed_database
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from fhms.models import (
    CustomUser, Deceased, NextOfKin, ServiceType, FuneralCase,
    CaseService, InventoryItem, Invoice, Payment
)


class Command(BaseCommand):
    help = 'Populate the database with test data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # Create admin user
        admin_user, created = CustomUser.objects.get_or_create(
            email='admin@memorialcare.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'username': 'admin',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Created admin user'))

        # Create funeral director
        director, created = CustomUser.objects.get_or_create(
            email='director@memorialcare.com',
            defaults={
                'first_name': 'John',
                'last_name': 'Director',
                'username': 'director',
                'role': 'director',
                'phone': '08012345678'
            }
        )
        if created:
            director.set_password('director123')
            director.save()
            self.stdout.write(self.style.SUCCESS('✓ Created funeral director'))

        # Create accountant
        accountant, created = CustomUser.objects.get_or_create(
            email='accountant@memorialcare.com',
            defaults={
                'first_name': 'Jane',
                'last_name': 'Accountant',
                'username': 'accountant',
                'role': 'accountant',
                'phone': '08098765432'
            }
        )
        if created:
            accountant.set_password('accountant123')
            accountant.save()
            self.stdout.write(self.style.SUCCESS('✓ Created accountant'))

        # Create family client
        family, created = CustomUser.objects.get_or_create(
            email='family@example.com',
            defaults={
                'first_name': 'Samuel',
                'last_name': 'Family',
                'username': 'family',
                'role': 'family_client',
                'phone': '08055555555'
            }
        )
        if created:
            family.set_password('family123')
            family.save()
            self.stdout.write(self.style.SUCCESS('✓ Created family client'))

        # Create service types
        services = [
            ('Full Funeral Service', 'Complete funeral arrangement with all services', Decimal('150000.00')),
            ('Wake Keeping', 'Night vigil service', Decimal('50000.00')),
            ('Graveside Service', 'Cemetery burial service', Decimal('75000.00')),
            ('Embalming', 'Body preservation', Decimal('50000.00')),
            ('Transportation', 'Hearse and vehicle service', Decimal('30000.00')),
        ]
        
        for name, desc, cost in services:
            service, created = ServiceType.objects.get_or_create(
                name=name,
                defaults={
                    'description': desc,
                    'base_cost': cost,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created service: {name}'))

        # Create deceased records
        deceased_data = [
            ('Mary', 'Johnson', '1945-05-15', '2024-01-10', 'F', 'ID123456'),
            ('Peter', 'Smith', '1950-08-20', '2024-01-15', 'M', 'ID123457'),
            ('Grace', 'Williams', '1948-03-10', '2024-01-20', 'F', 'ID123458'),
        ]
        
        deceased_list = []
        for first, last, dob, dod, gender, id_num in deceased_data:
            deceased, created = Deceased.objects.get_or_create(
                identity_number=id_num,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'date_of_birth': dob,
                    'date_of_death': dod,
                    'gender': gender,
                    'address': '123 Sample Street',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created deceased: {first} {last}'))
            deceased_list.append(deceased)

        # Create next of kin
        for deceased in deceased_list:
            if not hasattr(deceased, 'next_of_kin'):
                NextOfKin.objects.get_or_create(
                    deceased=deceased,
                    defaults={
                        'full_name': f'{deceased.first_name} Junior' ,
                        'relationship': 'Son',
                        'email': f'kin{deceased.id}@example.com',
                        'phone': '08011111111',
                        'address': '456 Family Avenue'
                    }
                )
                self.stdout.write(self.style.SUCCESS(f'✓ Created next of kin for {deceased.full_name}'))

        # Create funeral cases
        for i, deceased in enumerate(deceased_list):
            case, created = FuneralCase.objects.get_or_create(
                deceased=deceased,
                defaults={
                    'case_number': f'CASE-2024-{1001+i}',
                    'client_family': family,
                    'funeral_director': director,
                    'status': 'confirmed',
                    'scheduled_date': timezone.now() + timedelta(days=3),
                    'venue': 'MemorialCare Chapel',
                    'special_requests': 'Traditional ceremony'
                }
            )
            if created:
                # Add services to case
                for service in ServiceType.objects.all()[:3]:
                    CaseService.objects.get_or_create(
                        case=case,
                        service_type=service,
                        defaults={'cost': service.base_cost}
                    )
                self.stdout.write(self.style.SUCCESS(f'✓ Created case for {deceased.full_name}'))

        # Create inventory items
        inventory_items = [
            ('CAS001', 'Premium Casket', 'casket', 5, 2, Decimal('200000.00')),
            ('CAS002', 'Standard Casket', 'casket', 8, 3, Decimal('100000.00')),
            ('EQP001', 'Wheelchair', 'equipment', 4, 2, Decimal('50000.00')),
            ('FLW001', 'Flower Arrangement', 'flower', 15, 5, Decimal('10000.00')),
            ('ACC001', 'Cushion Set', 'accessory', 20, 5, Decimal('5000.00')),
        ]
        
        for code, name, cat, qty, reorder, cost in inventory_items:
            item, created = InventoryItem.objects.get_or_create(
                item_code=code,
                defaults={
                    'name': name,
                    'category': cat,
                    'quantity_in_stock': qty,
                    'reorder_level': reorder,
                    'unit_cost': cost,
                    'supplier': 'MemorialCare Suppliers',
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created inventory item: {name}'))

        self.stdout.write(self.style.SUCCESS('\n✓ Database seeding completed successfully!'))
        self.stdout.write(self.style.WARNING('\nTest Credentials:'))
        self.stdout.write('Admin: admin@memorialcare.com / admin123')
        self.stdout.write('Director: director@memorialcare.com / director123')
        self.stdout.write('Accountant: accountant@memorialcare.com / accountant123')
        self.stdout.write('Family: family@example.com / family123')
