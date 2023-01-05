from sqlalchemy.dialects.postgresql import UUID, ARRAY

from src.app_config import ModelMixin, OrganizationMixin, db
from src.contacts.companies.models import ContactCompanies
from src.contacts.contact_users.models import ContactUsers


class ContactTodo(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = "ContactTodo"

    todo = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True)
    
    due_at = db.Column(db.DateTime, nullable=True)
    
    assignees = db.Column(ARRAY(UUID(as_uuid=True)), nullable=False, default=[])
    attachments = db.Column(ARRAY(db.String(255)), nullable=False, default=[])

    completed = db.Column(db.Boolean, default=False, nullable=False)

    def __init__(
        self, todo=None, details=None, due_at=None, assignees=[], attachments=[], organization_id=None, completed=None
    ):
        self.todo = todo 
        self.details = details

        self.due_at = due_at

        self.assignees = assignees
        self.attachments = attachments
        self.organization_id = organization_id

        self.completed = completed

    @classmethod 
    def register(cls, data: dict):
        if not data:
            raise Exception('ContactTodo.register() requires an argument for `data`')

        # validations 
        required_fields = ['todo', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"`{field}` is a required field"
        
        # there can be multiple todos with the same `todo` field

        # ensure assignees are valid contacts
        valid_assignees = []
        if data.get('assignees'):
            for assignee in data.get('assignees'):
                if ContactUsers.id_exists(assignee, data.get('organization_id'))\
                    or ContactCompanies.id_exists(assignee, data.get('organization_id')):
                        valid_assignees.append(assignee)

        data['assignees'] = valid_assignees

        try:
            todo = cls(**data)
            db.session.add(todo)
            db.session.flush()
            db.session.commit()
            
            return True, todo
        except Exception as e:
            print(e)
            return False, str(e)

    @classmethod
    def get_query_for_contact(cls, contact_id=None, organization_id=None):
        '''
        Returns an SQLAlchemy Query object with filters for fetching Todos that have `contact_id` in their `assignees` field.
        More queries can be added to the result for a more exhaustive filter.
        For example:

        ```
        query = ContactTodos.get_query_for_contact(contact_id="ID", organization_id="ORG")
        results = Paginator(
            model=ContactTodos,
            query=query,
            query_string=Paginator.get_query_string(request.url),
            organization_id="ORG"
        ).result
        ```
        '''
        query = cls.query.filter(cls.assignees.contains(f"{{{contact_id}}}"))
        if organization_id:
            query = query.filter_by(organization_id=organization_id)
        return query