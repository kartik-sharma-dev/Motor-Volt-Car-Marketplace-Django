
   

# 🚗 Motor Volt

## 🌐 Live Demo
👉 **[https://motor-volt.onrender.com](https://motor-volt.onrender.com)** 
 
## 📸 Screenshots    

### Home Page
<img width="1897" height="834" alt="image" src="https://github.com/user-attachments/assets/90f0cb24-326b-46a0-9ff4-747bd2fe08c6" />


### Dashboard
<img width="1897" height="834" alt="image" src="https://github.com/user-attachments/assets/19b794db-fac8-4d69-bc74-a344ba49bc55" />


### Car Detail
<img width="1897" height="834" alt="image" src="https://github.com/user-attachments/assets/cb382cab-33ed-4236-9307-893f0c2aaf7e" />


![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)

Motor Volt is a full-featured car sales web platform built with Django. It allows users to list, browse, and manage car listings, with a secure OTP-based registration flow and a powerful admin dashboard for platform management.

---

## ✨ Features

### 🔐 Authentication & OTP Email Verification
- User registration with email-based OTP verification via the **Brevo API**
- Secure login with password hashing
- Session-based OTP flow with resend support
- Accounts that fail verification are not created until OTP is confirmed

### 🏠 Home & Listings
- Featured car listings on the homepage (latest 6 approved listings)
- Filter by make and year
- Total listing count displayed dynamically
- Car detail pages with similar car suggestions

### 🚘 Sell a Car
- Authenticated users can submit car listings with multiple image uploads
- Users can select a main/primary image from uploaded images
- Listings are held for admin approval before going live

### 📋 User Dashboard
- Regular users see their own listings with options to edit or delete
- Sellers can manage their car inventory from a single view

### 🛡️ Admin Dashboard
- Superadmin view with platform-wide stats:
  - Total users, total listings, pending approvals, verified users
- Approve or unapprove car listings with a single click
- Ban / unban users (supports AJAX for seamless UX)
- Delete users and their data
- Edit full user profiles including name, age, phone, user type, and profile picture
- View and manage all cars across all users

### 👤 Profile Management
- Users can update their profile information and upload a profile picture

### 🚫 User Moderation
- Banned users are blocked from logging in with a clear error message
- Admins can toggle ban status with instant AJAX feedback

---

## 🗂️ Project Structure

```
motorvolt/
├── views.py          # All view logic (auth, listings, dashboard, admin)
├── models.py         # User and Car models
├── forms.py          # UserForm, CarForm, UpdateProfileForm
├── urls.py           # URL routing
├── templates/        # HTML templates
│   ├── home.html
│   ├── signup.html
│   ├── login.html
│   ├── verify_otp.html
│   ├── dashboard.html
│   ├── sell.html
│   ├── car_detail.html
│   ├── edit_user.html
│   └── update_profile.html
└── static/           # CSS, JS, images
```

---

## ⚙️ Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/motor-volt.git
cd motor-volt
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and add the following:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True

# Brevo (email OTP)
BREVO_API_KEY=your_brevo_api_key
BREVO_SENDER_NAME=Motor Volt
BREVO_SENDER_EMAIL=noreply@yourdomain.com

# Database (optional if using default SQLite)
DATABASE_URL=your_database_url
```

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create a superadmin

```bash
python manage.py createsuperuser
```

> Make sure to set `user_type = 1` for the superadmin in the database or via the Django shell.

### 7. Run the development server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

---

## 🔑 User Roles

| Role | `user_type` | Access |
|------|-------------|--------|
| Superadmin | `1` | Full platform management |
| Regular User | `3` | List and manage own cars |

---

## 📧 OTP Email Flow

1. User fills in the signup form
2. An OTP is generated and emailed via the **Brevo SMTP API**
3. User is redirected to the OTP verification page
4. On successful verification, the account is created and the user is logged in
5. OTP can be resent if not received

---

## 🔒 Security Notes

- Passwords are hashed using Django's built-in `set_password` / `check_password`
- CSRF protection is applied across all forms
- `@login_required` guards protect all authenticated views
- Admin actions are restricted by `user_type` checks
- Inactive (banned) users cannot log in



---

## 🙌 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

---

## 📬 Contact

For support or inquiries, please use the contact page on the platform or open a GitHub issue.
