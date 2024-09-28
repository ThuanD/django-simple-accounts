# Django Accounts

Django accounts site


## Simple usage

1. Install by running the following command

    ```bash
    pip install django-simple-accounts
    ```

2. Add the following settings to your `settings.py` file

    ```python
    INSTALLED_APPS = [
        'accounts',
        # etc
    ]
    
    # example custom for accounts settings 
    LOGIN_URL = '/login/'
    ACCOUNTS = dict(
        LOGIN_URL='/login/',
        LOGIN_REDIRECT_URL='/',
    )
    ```

3. Add the account URLs to your `urls.py` file
    ```python
    from django.urls import path, include
    
    urlpatterns = [
        path('', include("accounts.urls")),
    ]
    ```