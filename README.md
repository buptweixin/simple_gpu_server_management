# GPU Server Management System

A web-based system for managing and monitoring GPU servers.

[中文版 README](README_CN.md)

## Introduction

The GPU Server Management System is a Flask-based web application designed to help organizations manage and monitor their GPU servers. It provides features such as server occupation, real-time GPU usage monitoring, and user management.

## Features

- User authentication and authorization
- GPU server management (add, delete, update)
- Real-time GPU usage monitoring
- Server occupation and release
- User management (for administrators)
- Dashboard with server statistics and GPU usage history

## Installation

1. Clone the repository:
   ```
   git clone  https://github.com/buptweixin/simple_gpu_server_management.git
   cd simple_gpu_server_management
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Create a `.env` file in the project root and add the following:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=sqlite:///site.db
   ```

## Usage

1. Start the application:
   ```
   flask run
   ```

2. Open a web browser and navigate to `http://localhost:5000`

3. Log in with the default admin account:
   - Username: admin
   - Password: admin

4. Change the admin password after first login

5. Start adding servers and managing users

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.