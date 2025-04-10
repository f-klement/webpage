# core/utils.py (continued)
from django.http import HttpResponse
from django.urls import reverse
import logging
from apscheduler.schedulers.background import BackgroundScheduler

def start_scheduler():
    """
    Initializes and starts the APScheduler BackgroundScheduler.
    
    Note: Modify the job addition (currently commented out) to schedule
    specific functions (e.g. XYZ) as needed.
    """
    scheduler = BackgroundScheduler()
    # Example: Uncomment and modify the following line to add a scheduled job.
    # scheduler.add_job(XYZ, 'cron', hour=17, minute=0)
    scheduler.start()
    logging.info("Scheduler started: Test run scheduled for 17:00 daily.")

def render_error_page(error):
    """
    Return a styled HTML error page as an HttpResponse with a 500 status code.
    """
    # Reverse the URL for the view named 'list_reports'
    list_reports_url = reverse("list_reports")
    
    html = f"""
    <html>
      <head>
        <meta charset="utf-8">
        <title>Test Error</title>
        <style>
          body {{
            margin: 0; padding: 0; background-color: #f3f3f3;
            font-family: Arial, sans-serif;
          }}
          .container {{
            background-color: #fff;
            width: 80%;
            max-width: 900px;
            margin: 3rem auto;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          }}
          .error {{
            background-color: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 6px;
          }}
          a {{
            color: #007BFF;
            text-decoration: none;
          }}
          a:hover {{
            text-decoration: underline;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h1>Test Run Error</h1>
          <div class="error">
            <strong>Error running tests:</strong><br>{error}
          </div>
          <p><a href="{list_reports_url}">Return to Test Reports</a></p>
        </div>
      </body>
    </html>
    """
    return HttpResponse(html, status=500)
