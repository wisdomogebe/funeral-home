# MemorialCare Funeral Home Management System

A comprehensive Django-based Funeral Home Management System (FHMS) with role-based access control, case management, inventory tracking, and financial reporting capabilities.

## Features

- **User Management**
  - Role-based access control (Admin, Director, Accountant, Inventory Manager, Family Client)
  - Custom user model with role-specific permissions
  - User activity audit logging

- **Deceased & Case Management**
  - CRUD operations for deceased records
  - Next-of-kin information tracking
  - Funeral case scheduling and management
  - Service assignment and tracking
  - Case status workflow

- **Inventory Management**
  - Complete inventory item management
  - Stock level tracking with automatic low-stock alerts
  - Inventory transactions audit trail
  - Category-based organization

- **Payments & Invoicing**
  - Automated invoice generation from funeral cases
  - Multi-method payment processing (Cash, Bank Transfer, Online Gateways)
  - Payment tracking and reconciliation
  - Receipt generation and download

- **Financial Reports**
  - Financial summaries with revenue tracking
  - Operational metrics and case analysis
  - Revenue breakdown by service type
  - Collection rate calculations

- **Family Portal**
  - Secure family client portal
  - View funeral arrangements
  - Online invoice and payment management
  - Receipt download

## Project Structure

```
funeral-home/
├── memorial_care/          # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── fhms/                   # Main app
│   ├── models.py           # Database models
│   ├── forms.py            # Django forms
│   ├── admin.py            # Admin configuration
│   ├── views/
│   │   ├── auth.py         # Authentication views
│   │   ├── dashboard.py    # Dashboard views
│   │   ├── case_management.py
│   │   ├── inventory_management.py
│   │   ├── payment_management.py
│   │   └── reporting.py
│   ├── services/           # Business logic layer
│   │   ├── case_service.py
│   │   ├── inventory_service.py
│   │   ├── payment_service.py
│   │   └── reporting_service.py
│   ├── utils/
│   │   ├── rbac.py         # Role-based decorators
│   │   ├── audit.py        # Audit logging
│   │   └── helpers.py      # Utility functions
│   └── urls.py
├── templates/              # HTML templates
│   ├── base/
│   │   └── base.html
│   ├── auth/
│   ├── dashboard/
│   ├── case/
│   ├── invoice/
│   ├── payment/
│   ├── inventory/
│   └── reports/
├── static/                 # CSS, JS, images
│   ├── css/
│   └── js/
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL (or SQLite for development)
- pip

### Setup Steps

1. **Clone and navigate to project:**
```bash
cd funeral-home
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
# Create .env file in project root
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_ENGINE=postgresql
DB_NAME=memorial_care_db
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
```

5. **Apply migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser:**
```bash
python manage.py createsuperuser
```

7. **Start development server:**
```bash
python manage.py runserver
```

8. **Access the application:**
- Visit `http://localhost:8000`
- Admin panel: `http://localhost:8000/admin`

## Architecture

### Layered Architecture

1. **Views Layer** - Handles HTTP requests and renders responses
2. **Business Logic Layer** - Services contain all business logic
3. **Models Layer** - Database models and relationships
4. **Utilities Layer** - Helper functions and decorators

### Key Components

#### Services (Business Logic)
- `CaseService` - Funeral case operations
- `InventoryService` - Inventory management
- `InvoiceService` - Invoice operations
- `PaymentService` - Payment processing
- `ReportService` - Report generation

#### RBAC Decorators
- `@role_required()` - Restrict by specific roles
- `@admin_required` - Admin only
- `@director_required` - Director only
- etc.

#### Audit Logging
- All critical actions logged to `AuditLog` model
- Automatic IP address tracking
- Comprehensive action history

## Database Models

### Core Models
- `CustomUser` - Extended user model with roles
- `Deceased` - Deceased person records
- `NextOfKin` - Next of kin information
- `FuneralCase` - Funeral case management
- `ServiceType` - Available funeral services
- `CaseService` - Services assigned to cases

### Inventory Models
- `InventoryItem` - Inventory items
- `InventoryTransaction` - Stock movement audit trail

### Financial Models
- `Invoice` - Funeral invoices
- `Payment` - Payment records

### System Models
- `AuditLog` - System action logging
- `Report` - Generated reports

## Usage Examples

### Creating a Funeral Case
```python
from fhms.services.case_service import CaseService

case = CaseService.create_case(
    deceased_id=deceased_uuid,
    client_family=family_user,
    funeral_director=director_user,
    scheduled_date=datetime.now(),
    venue="Cemetery Chapel",
    special_requests="Custom arrangement"
)
```

### Processing Payment
```python
from fhms.services.payment_service import PaymentService

payment = PaymentService.process_payment(
    invoice_id=invoice_uuid,
    amount=Decimal('50000.00'),
    payment_method='paystack',
    transaction_reference='PSK_123456'
)
```

### Adding Inventory Stock
```python
from fhms.services.inventory_service import InventoryService

InventoryService.add_stock(
    item_id=item_uuid,
    quantity=10,
    reason="Restocking from supplier"
)
```

## Role Permissions

### Administrator
- Full system access
- User management
- System configuration
- All reports

### Funeral Director
- Case management
- Service assignment
- Staff management
- Operational reports

### Accountant
- Invoice management
- Payment processing
- Financial reports
- Revenue tracking

### Inventory Manager
- Inventory CRUD
- Stock adjustments
- Low-stock alerts
- Inventory reports

### Family Client
- View own funeral arrangements
- Pay invoices
- Download receipts
- Manage account

## Security Features

- Password hashing with Django's default PBKDF2
- CSRF protection
- SQL injection prevention
- XSS protection through template escaping
- Role-based access control
- Comprehensive audit logging
- Secure session management

## API Endpoints

The system also provides REST API endpoints (can be extended):
- `/fhms/api/cases/` - Case operations
- `/fhms/api/invoices/` - Invoice operations
- `/fhms/api/payments/` - Payment operations
- `/fhms/api/inventory/` - Inventory operations

## Integration Points

### Payment Gateways
- Paystack integration ready (credentials in settings)
- Flutterwave integration ready
- extensible payment method system

### Email Notifications
- Ready for email confirmations
- Invoice email delivery
- Payment receipts via email

## Performance Considerations

- Database query optimization with `select_related()` and `prefetch_related()`
- Pagination for all list views
- Indexed frequently queried fields
- Transaction-based payment processing

## Future Enhancements

- Mobile app (React Native)
- SMS notifications
- Advanced reporting with charts
- Multi-branch support
- Integration with CRM systems
- Document management system
- Video tutorials

## Support

For issues, feature requests, or questions, please refer to the project documentation or contact the development team.

## License

This project is licensed under the MIT License - see LICENSE file for details.

---

**MemorialCare FHMS v1.0** - Making funeral home management simple and efficient.
