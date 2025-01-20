# Digital ID Backend

This project is a multiuse digital ID system for residents of Sheger city, designed to streamline the management of various identification documents through a single digital ID issued by the government. The system utilizes biometrics for user registration and provides both a web application and a mobile application for user interaction.

## Project Structure

The project is structured as follows:

```sh
digital-id-backend
├── digital_id
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── apps
│       ├── __init__.py
│       ├── users
│       │   ├── __init__.py
│       │   ├── admin.py
│       │   ├── apps.py
│       │   ├── models.py
│       │   ├── serializers.py
│       │   ├── tests.py
│       │   ├── urls.py
│       │   └── views.py
│       ├── ids
│       │   ├── __init__.py
│       │   ├── admin.py
│       │   ├── apps.py
│       │   ├── models.py
│       │   ├── serializers.py
│       │   ├── tests.py
│       │   ├── urls.py
│       │   └── views.py
│       └── biometrics
│           ├── __init__.py
│           ├── admin.py
│           ├── apps.py
│           ├── models.py
│           ├── serializers.py
│           ├── tests.py
│           ├── urls.py
│           └── views.py
├── manage.py
├── requirements.txt
└── README.md
```

## Technologies Used

- **Backend Framework**: Django
- **Database**: Supabase
- **Frontend Framework**: React (JavaScript/TypeScript)
- **Mobile Framework**: Flutter (Dart)
- **Deployment**: Render

## Features

- **User Registration**: Users can register using biometric data (fingerprints and photos).
- **ID Management**: Users can view and manage their digital IDs and other identification documents.
- **Expiration Tracking**: Users can check expiration dates and receive notifications for renewals.
- **Admin Interface**: Admins can manage users and IDs through the Django admin panel.

## Setup Instructions

1. **Clone the Repository**:

```bash
   git clone <repository-url>
   cd digital-id-backend
```

2. **Install Dependencies**:

```bash
   pip install -r requirements.txt
```

3. **Run Migrations**:

```bash
   python manage.py migrate
```

4. **Start the Development Server**:

```bash
   python manage.py runserver
```

5. **Access the Application**:
   Open your web browser and navigate to `http://127.0.0.1:8000/`.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
