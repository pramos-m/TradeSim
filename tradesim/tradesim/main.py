from tradesim import app
from tradesim.pages.dashboard_page import dashboard_page

# Add the dashboard page to the app
app.add_page(dashboard_page)

if __name__ == "__main__":
    app.start()