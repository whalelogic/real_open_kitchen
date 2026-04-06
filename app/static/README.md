# Static Assets Directory

This directory contains static files for the Open Kitchen application.

## Structure

- **css/** - Custom CSS stylesheets (Bulma theme customizations)
- **images/** - Images, icons, avatars, and other visual assets
  - Place recipe photos here
  - Avatar images
  - Category icons
  - Logo files

## Usage

Reference static files in templates using Flask's `url_for()` function:

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
<img src="{{ url_for('static', filename='images/recipe-placeholder.png') }}" alt="Recipe">
```

## Adding Images

To add images to recipes:
1. Upload images to the `images/` directory
2. Reference them in templates using the syntax above
3. Consider using subdirectories for organization (e.g., `images/recipes/`, `images/avatars/`)

## CDN Assets

The application uses the following CDN resources:
- Bulma CSS Framework (v0.9.4)
- Font Awesome Icons (v6.4.0)
