from app.extensions import db
from app.admin.models import Auditlog

def create_auditlog(admin_id, action, target):
    log = Auditlog(
        admin_id=admin_id,
        action=action,
        target=target
    )

    db.session.add(log)
    db.session.commit()