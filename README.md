# Open Kitchen - Recipe Sharing Application

A collaborative recipe management system designed for community and family environments, built with Flask and SQLite.

## Features

- **User Authentication**: Secure registration and login system with role-based access (Contributor, Curator)
- **Recipe Management**: Create, view, and fork recipes with structured ingredient data
- **AI Recipe Generator**: Create recipes from natural language prompts using Google Gemini AI
- **Dynamic Scaling**: Automatically scale ingredient quantities for different serving sizes
- **Recipe Templates**: Support for Standard Recipes and Quick Tips
- **Social Features**: Reviews, comments, and recipe saving
- **Personal Dashboard**: "My Kitchen" view with authored, forked, and saved recipes
- **Admin Tools**: User management, allergen audits, fork reports, and activity tracking
- **Notifications**: Event-triggered notifications for recipe interactions

## Project Structure

### __Important!!__

> Commit to the `test` branch so it can be merged into `main`.

> We all have full access.
> 
---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Getting Started — Clone the Repo](#getting-started--clone-the-repo)
4. [Setting Up Your Local Environment](#setting-up-your-local-environment)
5. [Running the App](#running-the-app)
6. [Git Workflow](#git-workflow)
   - [Everyday Git Commands](#everyday-git-commands)
   - [Branching Strategy](#branching-strategy)
   - [Submitting a Pull Request](#submitting-a-pull-request)
7. [Code Review Process](#code-review-process)
8. [Project Structure](#project-structure)

---

## Project Overview

| Detail | Value |
|--------|-------|
| Framework | Python / Flask |
| App Type | Full-featured CRUD |
| Core Features | Authentication, Create, Read, Update, Delete, and Fork recipes |
| Primary Branch | `main` |

---

## Prerequisites

Make sure you have the following installed before you start:

- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- [pip](https://pip.pypa.io/en/stable/) (comes with Python)
- A code editor such as [VS Code](https://code.visualstudio.com/)

---

## Getting Started — Clone the Repo

**Step 1 — Clone the repository to your local machine:**

```bash
git clone https://github.com/whalelogic/real_open_kitchen.git
```
open-kitchen/
├── app/
│   ├── __init__.py          # Application factory
│   ├── auth.py              # Authentication blueprint
│   ├── recipes.py           # Recipe management blueprint
│   ├── dashboard.py         # User dashboard blueprint
│   ├── admin.py             # Admin tools blueprint
│   ├── db.py                # Database connection and initialization
│   ├── schema.sql           # Database schema with seed data
│   └── templates/           # Jinja2 templates
│       ├── base.html
│       ├── auth/
│       ├── recipes/
│       ├── dashboard/
│       └── admin/
├── instance/
│   └── community_kitchen.db # SQLite database (created after init)
├── requirements.txt
└── README.md
```

## Overview Diagram
```mermaid
graph TB
    Client[Client Browser<br/>HTML/CSS/JS]
    Flask[Flask Application<br/>app/__init__.py]
    Auth[Auth Blueprint<br/>/auth/*]
    Recipes[Recipes Blueprint<br/>/recipes/*]
    Dashboard[Dashboard Blueprint<br/>/dashboard/*]
    Admin[Admin Blueprint<br/>/admin/*]
    DB[Database Layer<br/>db.py]
    SQLite[(SQLite Database<br/>community_kitchen.db)]
    
    Client -->|HTTP Requests| Flask
    Flask --> Auth
    Flask --> Recipes
    Flask --> Dashboard
    Flask --> Admin
    Auth --> DB
    Recipes --> DB
    Dashboard --> DB
    Admin --> DB
    DB --> SQLite
    
    style Flask fill:#3498db,color:#fff
    style SQLite fill:#2c3e50,color:#fff
```

## Installation

1. **Clone the repository** (or use existing directory)

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   
   Create a `.env` file in the project root (or set environment variables):
   
   ```bash
   # Required for AI Recipe Generation
   export GEMINI_API_KEY=your_gemini_api_key_here
   ```
   
   Get your Gemini API key from: [Google AI Studio](https://makersuite.google.com/app/apikey)

5. **Initialize the database**:
   ```bash
   export FLASK_APP=app
   flask init-db
   ```

## Running the Application

1. **Start the development server**:
   ```bash
   export FLASK_APP=app
   export FLASK_ENV=development  # Optional: enables debug mode
   export GEMINI_API_KEY=your_api_key  # Required for AI features
   flask run
   ```
   
   Or use the provided run script:
   ```bash
   ./run.sh
   ```

2. **Access the application**:
   Open your browser to `http://127.0.0.1:8080`

## Database Schema

The application uses SQLite with the following core tables:

### Authentication & Authorization
- `users`: User accounts with role assignments
- `roles`: System roles (Contributor, Curator)

### Recipe System
- `recipes`: Core recipe metadata with template type and fork tracking
- `ingredients`: Structured ingredient data with quantities and units
- `instructions`: Step-by-step cooking instructions
- `units`: Measurement units (Curator-managed)
- `allergens`: Allergen tracking for safety

### Classification
- `categories`: Recipe categories (Appetizer, Dessert, etc.)
- `tags`: Dietary tags (Vegan, Gluten-Free, etc.)
- Many-to-many junction tables

### Social Features
- `reviews`: Star ratings and comments (1-5 stars)
- `comments`: Discussion threads
- `saved_recipes`: User favorites
- `friendships`: Community connections

### System
- `notifications`: Event-triggered user notifications
- `activity_logs`: Activity tracking for reports

## Default User Roles

- **Contributor** (role_id: 1): Standard user with recipe creation and social features
- **Curator** (role_id: 2): Administrator with full system access

To create a Curator account, register normally then update the database:
```bash
sqlite3 instance/community_kitchen.db "UPDATE users SET role_id = 2 WHERE username = 'your_username';"
```

## Key Features Implementation

### AI Recipe Generator
The application includes an AI-powered recipe generator using Google's Gemini API:

- **Toggleable Sidebar**: Click the "AI Assistant" button on the recipe creation page
- **Natural Language Input**: Describe your recipe idea in plain English
- **Automated Creation**: AI generates title, description, ingredients with quantities, and step-by-step instructions
- **Smart Population**: One-click to populate the recipe form with AI-generated content
- **Seamless Integration**: Ingredients and instructions are automatically added to your recipe

**Example prompts:**
- "A creamy tomato pasta with basil and garlic for 4 people"
- "Quick chocolate chip cookies that are crispy on the outside"
- "Spicy Thai chicken curry with coconut milk"

### Recipe Forking
Recipes can be forked to create personalized versions while maintaining lineage tracking via `parent_recipe_id`.

### Dynamic Ingredient Scaling
Ingredients are stored with numeric quantities that can be dynamically scaled:
```
scaled_quantity = (requested_servings / base_servings) * original_quantity
```

### Allergen Safety
Ingredients can be tagged with allergens for safety auditing and filtering.

### Admin Reports
Curators can generate:
- Most Forked Recipes report
- Allergen Audit by specific allergen
- User Activity Report (30-day window)

## Technology Stack

- **Backend**: Flask 3.1.3
- **Database**: SQLite 3
- **Authentication**: Werkzeug password hashing
- **Forms**: Flask-WTF
- **Templates**: Jinja2

## Development

The application follows Flask best practices with:
- Application factory pattern
- Blueprint-based modular architecture
- Proper database connection handling
- Foreign key enforcement
- Role-based authorization decorators

## License

This is a university project for Software Development using Agile methodologies.
