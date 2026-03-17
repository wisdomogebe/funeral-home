# MemorialCare FHMS - Documentation Index

Welcome to the MemorialCare Funeral Home Management System! This index helps you navigate the complete documentation.

## 📚 DOCUMENTATION ROADMAP

### Getting Started
1. **[README.md](README.md)** ← Start here
   - Project overview
   - Feature highlights
   - Architecture introduction
   - Quick start guide

2. **[SETUP.md](SETUP.md)** ← Installation & Setup
   - Prerequisites
   - Installation steps
   - Database configuration
   - Running the application
   - Troubleshooting

### Understanding the System
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** ← Deep Dive
   - Layered architecture overview
   - Complete file organization
   - Database schema
   - API endpoints structure
   - Deployment checklist

4. **[PROJECT_COMPLETION.md](PROJECT_COMPLETION.md)** ← Project Details
   - Complete requirement verification
   - Statistics and metrics
   - Security features
   - Feature list
   - Quick start examples

### Advanced Features
5. **[API_CONFIG.md](API_CONFIG.md)** ← REST API Setup
   - Optional REST API configuration
   - API endpoint listing
   - Query parameter examples
   - Usage patterns

## 🎯 QUICK NAVIGATION BY ROLE

### For Administrators
- Read: README.md → SETUP.md
- Focus: User management, system configuration
- Start: Create admin account, seed database
- Navigate: Admin Dashboard → System Settings

### For Developers
- Read: ARCHITECTURE.md → Inline code comments
- Focus: Models, Services, Views structure
- Start: SETUP.md → Explore app structure
- Extend: Services layer for new features

### For Business Users
- Read: README.md (Features section)
- Focus: Workflows and reports
- Start: SETUP.md → seed_database
- Navigate: Appropriate dashboard for your role

### For DevOps/Deployment
- Read: SETUP.md → Deployment section
- Focus: Environment configuration, security
- Start: Configure .env file → Database setup
- Reference: ARCHITECTURE.md (Deployment Checklist)

## 📋 QUICK REFERENCE

### Test Credentials (after `python manage.py seed_database`)
```
Admin:      admin@memorialcare.com       / admin123
Director:   director@memorialcare.com    / director123
Accountant: accountant@memorialcare.com  / accountant123
Family:     family@example.com           / family123
```

### Essential Commands
```bash
# Installation
pip install -r requirements.txt

# First Time Setup
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Load Test Data
python manage.py seed_database

# Run Server
python manage.py runserver

# Access System
http://localhost:8000
http://localhost:8000/admin
```

### Windows vs Linux
```bash
# Create Virtual Environment
Windows:  python -m venv venv → venv\Scripts\activate
Linux:    python3 -m venv venv → source venv/bin/activate

# Install Dependencies (Both)
pip install -r requirements.txt
```

## 🏗️ SYSTEM STRUCTURE AT A GLANCE

```
memorial_care/          → Django project settings
fhms/                   → Main application
  ├── models.py        → 12 database models
  ├── views/           → 40+ request handlers
  ├── services/        → Business logic layer
  ├── forms.py         → Input validation
  └── utils/           → RBAC, audit, helpers
templates/              → 20+ HTML templates
static/                 → CSS, JavaScript
manage.py              → Django management tool
```

## 🔐 USER ROLES & PERMISSIONS

| Role | Access Level | Dashboard | Key Permissions |
|------|-------------|-----------|-----------------|
| Admin | Full | `/dashboard/admin/` | Everything + system config |
| Funeral Director | High | `/dashboard/` | Cases, services, staff |
| Accountant | High | `/dashboard/` | Invoices, payments, reports |
| Inventory Manager | Medium | `/dashboard/` | Stock, items, alerts |
| Family Client | Limited | `/dashboard/` | View cases, pay invoices |

## 📊 KEY WORKFLOWS

### Workflow 1: Creating a Funeral Case
1. Admin logs in → Deceased Management → Add deceased
2. Director logs in → Cases → Create case
3. Accountant → Invoices → Generate invoice
4. Family Client → Portal → View & pay

### Workflow 2: Inventory Management
1. Inventory Manager → Inventory → Low Stock Alerts
2. Create purchase order
3. Receive stock → Adjust inventory
4. System logs transaction

### Workflow 3: Financial Reporting
1. Accountant → Reports → Financial Report
2. Select date range
3. View revenue, collections, outstanding
4. Download for analysis

## ❓ COMMON QUESTIONS

**Q: Where do I find logs?**
A: `funeral-home/logs/debug.log` or console output

**Q: How do I reset the database?**
A: Delete `db.sqlite3`, run `makemigrations → migrate`

**Q: Can I use PostgreSQL instead of SQLite?**
A: Yes! Edit `.env` with PostgreSQL credentials in SETUP.md

**Q: How do I add new functionality?**
A: Follow the layered pattern: Model → Form → Service → View → Template

**Q: Is the system secure for production?**
A: Yes! See ARCHITECTURE.md (Security Checklist) for deployment steps

**Q: Can I enable REST API?**
A: Yes! See API_CONFIG.md for configuration

## 🚀 NEXT STEPS

1. **Install** → Follow SETUP.md exactly
2. **Test** → Use seed_database test accounts
3. **Explore** → Try each user role
4. **Customize** → Modify templates for branding
5. **Deploy** → Follow deployment checklist
6. **Monitor** → Check logs regularly

## 📞 NEED HELP?

### Troubleshooting
1. Check SETUP.md (Troubleshooting section)
2. Review error logs at `logs/debug.log`
3. Check Django console output
4. Verify environment (.env) configuration
5. Ensure database is properly migrated

### Learning More
- Django Official: https://www.djangoproject.com/
- DRF: https://www.django-rest-framework.org/
- Bootstrap: https://getbootstrap.com/

## 📈 PROJECT STATISTICS

- **Models**: 12 database models
- **Views**: 40+ view functions
- **Templates**: 20+ HTML templates
- **URL Routes**: 40+ endpoints
- **Forms**: 12 form classes
- **Services**: 4 service modules with 30+ methods
- **Lines of Code**: 4000+
- **Documentation**: 5 comprehensive guides

## ✅ VERIFICATION CHECKLIST

After installation, verify:
- [ ] Django server runs without errors
- [ ] Can access http://localhost:8000
- [ ] Admin account created successfully
- [ ] Test data loads with `seed_database`
- [ ] Can login as admin
- [ ] Dashboard loads for each role
- [ ] Can view database in admin panel
- [ ] Forms validate correctly
- [ ] All menu items are visible

## 🎓 EDUCATIONAL VALUE

This project teaches:
- Full-stack Django development
- Layered architecture patterns
- Role-based access control
- Business logic separation
- Database relationships (ORM)
- Form handling and validation
- Template inheritance
- Service-oriented architecture
- Admin customization
- RESTful API design

---

## Document Map

```
funeral-home/
├── README.md                    ← Start here (Overview)
├── SETUP.md                     ← Installation guide
├── ARCHITECTURE.md              ← Technical deep dive
├── PROJECT_COMPLETION.md        ← Feature verification
├── API_CONFIG.md                ← REST API setup
└── INDEX.md                     ← This file
```

---

**Last Updated:** 2024  
**Version:** 1.0  
**Status:** Complete & Production Ready

**For questions, refer to the specific documentation file above.**
