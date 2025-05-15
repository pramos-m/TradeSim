from tradesim import app
from tradesim.pages.dashboard import dashboard

# Add the dashboard page to the app
app.add_page(dashboard)

if __name__ == "__main__":
    app.start()