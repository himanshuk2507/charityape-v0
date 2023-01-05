from datetime import datetime
from typing import List

from werkzeug.security import generate_password_hash

from src.app_config import db
from src.profile.models import Admin


def seed_admin():
    now = datetime.now()

    data = [
        dict(
            email='precious@skraggle.test',
            first_name='Precious',
            last_name='Skraggle',
        ),
        dict(
            email='clinton@skraggle.test',
            first_name='Clinton',
            last_name='Skraggle',
        ),
        dict(
            email='fateh@skraggle.test',
            first_name='Fateh',
            last_name='Skraggle',
        ),
        dict(
            email='agboola@skraggle.test',
            first_name='Agboola',
            last_name='Skraggle',
        ),
        dict(
            email='victoria@skraggle.test',
            first_name='Victoria',
            last_name='Skraggle',
        ),
        dict(
            email='james@skraggle.test',
            first_name='James',
            last_name='Skraggle',
        ),
        dict(
            email='laila@skraggle.test',
            first_name='Laila',
            last_name='Skraggle',
        ),
        dict(
            email='samson@skraggle.test',
            first_name='Samson',
            last_name='Skraggle',
        ),
        dict(
            email='icheka@skraggle.test',
            first_name='Icheka',
            last_name='Skraggle',
        ),
    ]

    accounts: List[Admin] = []
    print('** Seeding: Admin **')
    for d in data:
        exists = Admin.fetch_one_by_email(d.get('email')) != None
        
        if exists:
            continue
        
        password = generate_password_hash(d.get('email'), method="sha256")
        account = Admin(**d, password=password, confirmed=True, confirmed_at=now)
        accounts.append(account)

    db.session.add_all(accounts)
    db.session.flush()
    db.session.commit()

    print('***** Admin: Seeded successfully')