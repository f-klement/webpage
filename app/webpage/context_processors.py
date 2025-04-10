# webpage/context_processors.py
def app_data(request):
    return {
        "app_data": {
            "name": "local ghost",
            "description": "A page for home automation and resource sharing.",
            "html_title": "local ghost",
            "project_name": "local ghost page",
            "keywords": "flask, webapp, home-automation, self-hosting",
        }
    }
