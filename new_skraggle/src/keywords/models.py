from src.app_config import ModelMixin, OrganizationMixin, db


class Keyword(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'Keyword'

    name = db.Column(db.String(255), nullable=False)


    def __init__(
        self, name = None,
        organization_id = None
    ):
        self.name = name
        self.organization_id = organization_id


    @classmethod
    def register(cls, data: dict = None):
        if data is None:
            raise Exception('Keyword.register() requires an argument for `data`')

        required_fields = ['name', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"

        try:
            # does keyword with this name already exist?
            keyword = cls.fetch_by_name(data.get('name'), data.get('organization_id'))
            if keyword:
                return False, 'This keyword has already been saved. Try again with a different name.'

            keyword = cls(**data)
            db.session.add(keyword)
            db.session.flush()
            db.session.commit()

            return True, keyword
        except Exception as e:
            return False, str(e)


    def update(self, data: dict = None):
        if not data:
            raise Exception('Keyword.update() requires an argument for `data`')

        try:
            # prevent renaming a keyword to an existing name
            old_name = data.get('name')
            if old_name is not None:
                keyword = Keyword.fetch_by_name(
                    name=old_name,
                    organization_id=self.organization_id,
                )
                if keyword is not None:
                    return False, 'Another keyword has already been saved with this name'

            return super().update(data)
        except Exception as e:
            print(e)
            return False, str(e)


    @classmethod
    def fetch_by_name(cls, name: str = None, organization_id: str = None):
        if not name or not organization_id:
            raise Exception('`name` and `organization_id` are required in Keyword.fetch_by_name()')
        return Keyword.query.filter_by(
                name=name,
                organization_id=organization_id,
            ).one_or_none()