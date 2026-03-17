"""
Case Management Service
Handles all business logic related to funeral cases.
"""
from django.utils import timezone
from fhms.models import FuneralCase, Deceased, CaseService, ServiceType, Invoice
from fhms.utils.helpers import generate_case_number, generate_invoice_number
from fhms.utils.audit import log_action


class CaseService:
    """Service for managing funeral cases."""
    
    @staticmethod
    def create_case(deceased_id, client_family, funeral_director, scheduled_date, venue, special_requests=""):
        """
        Create a new funeral case.
        
        Args:
            deceased_id: UUID of the deceased
            client_family: CustomUser instance (family client)
            funeral_director: CustomUser instance (funeral director)
            scheduled_date: DateTime of the funeral
            venue: Location of the funeral
            special_requests: Any special requests
            
        Returns:
            FuneralCase instance
        """
        try:
            deceased = Deceased.objects.get(id=deceased_id)
            case = FuneralCase.objects.create(
                deceased=deceased,
                case_number=generate_case_number(),
                client_family=client_family,
                funeral_director=funeral_director,
                scheduled_date=scheduled_date,
                venue=venue,
                special_requests=special_requests
            )
            log_action(None, 'CREATE', 'FuneralCase', case.id, 
                      f'Created case {case.case_number} for {deceased.full_name}')
            return case
        except Deceased.DoesNotExist:
            raise ValueError("Deceased not found")
    
    @staticmethod
    def update_case_status(case_id, new_status):
        """Update the status of a funeral case."""
        try:
            case = FuneralCase.objects.get(id=case_id)
            old_status = case.status
            case.status = new_status
            case.save()
            log_action(None, 'UPDATE', 'FuneralCase', case.id,
                      f'Status changed from {old_status} to {new_status}')
            return case
        except FuneralCase.DoesNotExist:
            raise ValueError("Case not found")
    
    @staticmethod
    def add_service_to_case(case_id, service_type_id, cost=None, notes=""):
        """
        Add a service to a funeral case.
        
        Args:
            case_id: UUID of the funeral case
            service_type_id: UUID of the service type
            cost: Optional custom cost (uses base_cost if not provided)
            notes: Optional notes for the service
            
        Returns:
            CaseService instance
        """
        try:
            case = FuneralCase.objects.get(id=case_id)
            service_type = ServiceType.objects.get(id=service_type_id)
            
            final_cost = cost if cost is not None else service_type.base_cost
            
            case_service = CaseService.objects.create(
                case=case,
                service_type=service_type,
                cost=final_cost,
                notes=notes
            )
            log_action(None, 'CREATE', 'CaseService', case_service.id,
                      f'Added service {service_type.name} to case {case.case_number}')
            return case_service
        except (FuneralCase.DoesNotExist, ServiceType.DoesNotExist):
            raise ValueError("Case or Service Type not found")
    
    @staticmethod
    def get_case_details(case_id):
        """Get complete details of a funeral case."""
        try:
            case = FuneralCase.objects.prefetch_related(
                'services', 'assigned_staff', 'caseservice_set'
            ).get(id=case_id)
            return {
                'case': case,
                'deceased': case.deceased,
                'services': case.caseservice_set.all(),
                'total_cost': case.total_cost,
                'status': case.status
            }
        except FuneralCase.DoesNotExist:
            return None
    
    @staticmethod
    def assign_staff_to_case(case_id, staff_user_ids):
        """Assign staff members to a funeral case."""
        try:
            case = FuneralCase.objects.get(id=case_id)
            case.assigned_staff.set(staff_user_ids)
            log_action(None, 'UPDATE', 'FuneralCase', case.id,
                      f'Assigned {len(staff_user_ids)} staff members to case')
            return case
        except FuneralCase.DoesNotExist:
            raise ValueError("Case not found")
