from app import create_app
from app.models import Patient

app = create_app()
with app.app_context():
    patients = Patient.query.all()
    print(f"Found {len(patients)} patients:")
    for p in patients:
        print(f"ID: {p.id}, Name: {p.name}")
