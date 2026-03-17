```
MEMORIAL CARE FUNERAL HOME MANAGEMENT SYSTEM (FHMS)
Project Architecture Summary & Implementation Guide
```

# PROJECT OVERVIEW

MemorialCare FHMS is a comprehensive Django-based management system for funeral homes with:
- Role-Based Access Control (5 user roles)
- Complete death case management
- Inventory tracking with automated alerts
- Invoice and payment processing
- Comprehensive financial & operational reporting
- Family client portal
- Audit logging system

---

# LAYERED ARCHITECTURE

## 1. PRESENTATION LAYER (Templates & Static Files)
```
templates/
├── base/base.html              - Master template with responsive design
├── auth/                        - Authentication templates
│   ├── login.html
│   ├── register.html
│   └── profile.html
├── dashboard/                   - Role-specific dashboards
│   ├── admin_dashboard.html
│   ├── director_dashboard.html
│   └── family_dashboard.html
├── case/, invoice/, inventory/  - CRUD templates
└── reports/                     - Report templates
```

## 2. VIEW LAYER (URL Handlers)
```
fhms/views/
├── __init__.py
├── auth.py                      - Authentication & profile (6 views)
├── dashboard.py                 - Dashboard management (2 views)
├── case_management.py           - Cases & deceased (9 views)
├── inventory_management.py      - Inventory operations (7 views)
├── payment_management.py        - Invoices & payments (9 views)
└── reporting.py                 - Reports generation (6 views)

Total: ~40 views cove ring all CRUD operations
```

## 3. BUSINESS LOGIC LAYER (Services)
```
fhms/services/
├── case_service.py              - Case operations (5 static methods)
├── inventory_service.py         - Inventory management (10 static methods)
├── payment_service.py           - Invoicing & payments (8 static methods)
└── reporting_service.py         - Report generation (6 static methods)

All business logic separated from views for reusability
```

## 4. DATA ACCESS LAYER (Models)
```
fhms/models.py contains 12 models:

User Management:
- CustomUser                    - Extended user with role-based access

Core Entities:
- Deceased                      - Deceased person records
- NextOfKin                     - Next of kin information
- ServiceType                   - Funeral service offerings
- FuneralCase                   - Main case management entity
- CaseService                   - M2M table (Case ↔ Services)

Inventory:
- InventoryItem                 - Stock items
- InventoryTransaction          - Audit trail for stock

Financial:
- Invoice                       - Funeral invoices
- Payment                       - Payment records

System:
- AuditLog                      - Action logging
- Report                        - Generated reports
```

## 5. UTILITIES LAYER
```
fhms/utils/
├── rbac.py                      - Role-based decorators (6 decorators)
├── audit.py                     - Audit logging functions
├── helpers.py                   - Helper utilities (10+ functions)
└── forms.py                     - Django forms (12 forms)
```

---

# USER ROLES & PERMISSIONS

## 1. Administrator (@admin_required)
- Full system access
- User management
- System configuration
- All reports access
- Dashboard: /dashboard/admin/

## 2. Funeral Director (@director_required)
- Case management (CRUD)
- Service assignment
- Staff coordination
- Operational reports
- Dashboard: /dashboard/ (director view)

## 3. Accountant (@accountant_required)
- Invoice management
- Payment processing
- Financial reports
- Revenue tracking
- Dashboard: /dashboard/ (accountant view)

## 4. Inventory Manager (@inventory_manager_required)
- Inventory CRUD
- Stock adjustments
- Low-stock alerts
- Inventory reports
- Dashboard: /dashboard/ (inventory view)

## 5. Family Client (Default)
- View own cases
- Pay invoices
- Download receipts
- Manage profile
- Dashboard: /dashboard/ (family view)

---

# KEY FEATURES IMPLEMENTATION

## 1. ROLE-BASED ACCESS CONTROL
```python
# Decorator usage in views
@role_required('admin', 'director')
def deceased_create(request):
    # Only admin and directors can access
    pass

# Property checks
if user.is_admin:
    # Show admin features
    pass
```

## 2. BUSINESS LOGIC EXAMPLE
```python
# Separated in services, not in views
from fhms.services.case_service import CaseService

case = CaseService.create_case(
    deceased_id, client_family, funeral_director,
    scheduled_date, venue, special_requests
)
```

## 3. AUDIT LOGGING
```python
# Automatic logging of actions
log_action(user, 'CREATE', 'Deceased', obj_id, description, request)

# Tracks: User, Action, Object, Details, IP, Timestamp
```

## 4. INVENTORY MANAGEMENT
```python
service = InventoryService()
service.add_stock(item_id, quantity, reason)
service.remove_stock(item_id, quantity, reason)
service.get_low_stock_items()  # Auto alerts
```

## 5. PAYMENT PROCESSING
```python
payment = PaymentService.process_payment(
    invoice_id, amount, payment_method, 
    transaction_reference
)
# Atomically updates invoice, creates payment record
```

---

# DATABASE SCHEMA HIGHLIGHTS

## Relationships
```
Deceased 1──→ FuneralCase ──→ CaseService ←──M ServiceType
    │
    └─→ NextOfKin

FuneralCase ──→ Invoice ←───M Payment
              └─→ Staff (M2M)

InventoryItem ──M─→ InventoryTransaction
```

## Key Constraints
- UUID primary keys for security
- Foreign key constraints for data integrity
- Unique constraints on codes/numbers
- Auto-timestamps on all entities
- Soft delete support where needed

---

# API ENDPOINTS (if REST API enabled)

```
GET    /api/cases/                    - List cases
GET    /api/cases/{id}/               - Case details
GET    /api/cases/low_stock/          - Low stock alert

GET    /api/invoices/                 - List invoices
GET    /api/invoices/{id}/            - Invoice details

GET    /api/payments/                 - List payments
GET    /api/payments/{id}/            - Payment details

GET    /api/inventory/                - List items
GET    /api/inventory/{id}/           - Item details
GET    /api/inventory/low_stock/      - Low stock items
```

---

# QUICK START COMMANDS

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env
# Edit .env with your database credentials

# 3. Create databases (PostgreSQL)
createdb memorial_care_db

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. Create superuser
python manage.py createsuperuser

# 6. Load test data
python manage.py seed_database

# 7. Run server
python manage.py runserver

# 8. Access at http://localhost:8000
```

---

# TESTING WORKFLOW

## Test Credentials (after seed_database)
```
Admin:      admin@memorialcare.com / admin123
Director:   director@memorialcare.com / director123
Accountant: accountant@memorialcare.com / accountant123
Family:     family@example.com / family123
```

## Test Scenario
1. Admin creates deceased record
2. Director creates funeral case
3. Director assigns services
4. Accountant generates invoice
5. Family client views & pays invoice
6. System generates reports

---

# FILE ORGANIZATION

```
funeral-home/
├── memorial_care/           # Project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
│
├── fhms/                    # Main app
│   ├── models.py            # 12 database models
│   ├── forms.py             # 12 forms
│   ├── admin.py             # Admin configuration
│   ├── apps.py              # App config
│   ├── urls.py              # URL routing (30+ routes)
│   ├── serializers.py       # REST API serializers
│   ├── viewsets.py          # REST API viewsets
│   │
│   ├── views/               # Business request handlers
│   │   ├── auth.py          # 6 auth views
│   │   ├── dashboard.py     # 2 dashboard views
│   │   ├── case_management.py  # 9 case views
│   │   ├── inventory_management.py  # 7 inventory views
│   │   ├── payment_management.py    # 9 payment views
│   │   └── reporting.py     # 6 reporting views
│   │
│   ├── services/            # Business logic layer
│   │   ├── case_service.py
│   │   ├── inventory_service.py
│   │   ├── payment_service.py
│   │   └── reporting_service.py
│   │
│   ├── utils/               # Utilities
│   │   ├── rbac.py          # 6 RBAC decorators
│   │   ├── audit.py         # Audit functions
│   │   └── helpers.py       # 10+ helper functions
│   │
│   ├── management/
│   │   └── commands/
│   │       └── seed_database.py  # Test data command
│   │
│   └── migrations/          # Database migrations
│
├── templates/               # HTML templates (~20 files)
│   ├── base/base.html       # Master template
│   ├── auth/
│   ├── dashboard/
│   ├── case/
│   ├── invoice/
│   ├── payment/
│   ├── inventory/
│   └── reports/
│
├── static/                  # CSS, JS, images
│   ├── css/
│   └── js/
│
├── logs/                    # Log files
│
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore file
├── README.md             # Project documentation
├── SETUP.md              # Setup guide
└── ARCHITECTURE.md       # This file
```

---

# CODE METRICS

## Lines of Code
- Models: ~600 lines
- Views: ~800 lines
- Services: ~700 lines
- Templates: ~1000 lines
- **Total: ~4000+ lines of code**

## Number of Components
- Models: 12
- Views: 40+
- Forms: 12
- Templates: 20+
- Services: 4 (with 30+ methods)
- URL routes: 30+
- Decorators: 6

---

# SECURITY FEATURES

1. **Authentication**
   - Password hashing (PBKDF2)
   - Session-based auth
   - Secure login/logout

2. **Authorization**
   - Role-based access control
   - Decorator-based permissions
   - Model-level permissions

3. **Data Protection**
   - CSRF tokens
   - SQL injection prevention
   - XSS protection
   - UUID instead of sequential IDs

4. **Audit Trail**
   - All actions logged
   - User tracking
   - IP address logging
   - Timestamp audit trail

5. **Database**
   - Atomic transactions
   - Foreign key constraints
   - Unique constraints
   - Data integrity checks

---

# SCALABILITY CONSIDERATIONS

## Current Optimizations
- Database indexing on frequently queried fields
- Query optimization (select_related, prefetch_related)
- Pagination on all list views
- Asynchronous-ready architecture

## Future Scaling
- Add caching layer (Redis)
- Implement queue system (Celery)
- API rate limiting
- Load balancing
- Database replication
- CDN for static files

---

# DEPLOYMENT CHECKLIST

- [ ] Set DEBUG=False
- [ ] Generate strong SECRET_KEY
- [ ] Configure DATABASE_URL
- [ ] Set ALLOWED_HOSTS
- [ ] Configure HTTPS
- [ ] Set up logging to files
- [ ] Configure email backend
- [ ] Run collectstatic
- [ ] Database backups configured
- [ ] SSL certificates setup
- [ ] Environment variables secured
- [ ] Admin panel password set
- [ ] Test payment gateway keys

---

# SUPPORT & MAINTENANCE

## Logs Location
- Application logs: `funeral-home/logs/debug.log`
- Django error logs: Check console

## Management Commands
```bash
python manage.py makemigrations      # Create migrations
python manage.py migrate             # Apply migrations
python manage.py createsuperuser    # Create admin
python manage.py seed_database      # Load test data
python manage.py shell              # Interactive shell
python manage.py test               # Run tests
```

## Backup Strategy
- Regular database backups
- Media files backup
- Settings backup
- Document version control

---

# NEXT STEPS

1. Install and configure the system
2. Run seed_database to load test data
3. Test each user role
4. Customize templates with branding
5. Configure payment gateways
6. Set up email notifications
7. Deploy to production server

---

**Created:** 2024
**Version:** 1.0
**Architecture:** Layered Django application
**Status:** Production-ready
