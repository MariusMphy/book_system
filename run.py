from book_system_project import create_app
from book_system_project.models import db

app = create_app('app_config.py')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
