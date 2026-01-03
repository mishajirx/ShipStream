# ShipStream - Portable Delivery Service Platform

An open-source, customizable delivery service application designed for small businesses to quickly deploy their own local delivery operations.

## What Is This?

This project provides a ready-to-use delivery service platform that small businesses can fork, customize, and deploy for their own needs. Whether you're running a local shop, restaurant, or any business requiring delivery logistics, this template gives you:

- A complete user registration and role management system
- Order placement and tracking functionality
- Courier management with ratings
- Admin controls for hiring and managing staff
- A full REST API for integration with other systems

Simply clone the repository, customize the branding, and deploy—no need to build a delivery platform from scratch.

## Live Demo
**[View Demo](https://mzhernevskii.pythonanywhere.com)**

---

## Features & User Roles

The platform supports three distinct user roles:

**Regular Users** can place delivery orders and track their status.

**Couriers** accept and complete deliveries, receive payments, and build their rating over time.

**Admins** hire and dismiss couriers, and can promote users to admin status.

The REST API provides both admin and courier privileges, enabling seamless integration with external systems. A default admin account is always present in the database to bootstrap your team.

---

## Getting Started

### 1. Fork & Clone the Repository

1. Click the **Fork** button at [github.com/mishajirx/RostovExpress](https://github.com/mishajirx/RostovExpress)
2. Open your terminal and navigate to your preferred directory
3. Run: `git clone https://github.com/<YourUsername>/RostovExpress`

### 2. Install Dependencies

Navigate to the project directory and install requirements:

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python3 main.py
```

### 4. Run Tests

1. Start the application as shown above
2. Press `Ctrl+Z`, then run `bg` to background the process
3. Execute: `pytest-3 test.py -x -s`
4. Confirm with `y` when prompted

### 5. Auto-Start on Boot (Optional)

To launch the server automatically on system startup:

1. Run `crontab -e`
2. Add this line at the end: `@reboot python3 /path_to_project/main.py`

---

## API Endpoints Reference

| Role | Endpoint | Function |
|------|----------|----------|
| Bot/User | `/orders` | Place an order |
| Bot/User | — | Submit courier application |
| Admin | `/couriers` | Approve courier applications |
| Courier | `/orders/assign` | Accept available orders |
| Courier | `/courier/<courier_id>` | Update courier parameters |
| Courier | `/orders/complete` | Mark order as completed |
| Courier | `/couriers/<courier_id>` | Get courier information |

---

## Customization

To adapt this platform for your business, you'll want to update the branding, modify the frontend styling, and configure your database connection. The modular structure makes it straightforward to add new features or integrate with your existing systems.
