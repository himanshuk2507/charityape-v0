from src.app_config import ModelMixin, OrganizationMixin, db


class ImpactArea(ModelMixin, OrganizationMixin, db.Model):
    __tablename__ = 'ImpactArea'

    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)


    def __init__(
        self, name = None,
        description = None,
        organization_id = None
    ):
        self.name = name
        self.description = description
        self.organization_id = organization_id


    @classmethod
    def register(cls, data: dict = None):
        if data is None:
            raise Exception('ImpactArea.register() requires an argument for `data`')

        required_fields = ['name', 'organization_id']
        for field in required_fields:
            if field not in data.keys():
                return False, f"{field} is a required field"

        try:
            # does ImpactArea with this name already exist?
            impact_area = cls.fetch_by_name(data.get('name'), data.get('organization_id'))
            if impact_area:
                return False, 'This impact area has already been saved. Try again with a different name.'

            impact_area = cls(**data)
            db.session.add(impact_area)
            db.session.flush()
            db.session.commit()

            return True, impact_area
        except Exception as e:
            return False, str(e)


    def update(self, data: dict = None):
        if not data:
            raise Exception('ImpactArea.update() requires an argument for `data`')

        try:
            # prevent renaming a ImpactArea to an existing name
            old_name = data.get('name')
            if old_name is not None:
                impact_area = ImpactArea.fetch_by_name(
                    name=old_name,
                    organization_id=self.organization_id,
                )
                if impact_area is not None:
                    return False, 'Another impact area has already been saved with this name'

            return super().update(data)
        except Exception as e:
            print(e)
            return False, str(e)


    @classmethod
    def fetch_by_name(cls, name: str = None, organization_id: str = None):
        if not name or not organization_id:
            raise Exception('`name` and `organization_id` are required in ImpactArea.fetch_by_name()')
        return ImpactArea.query.filter_by(
                name=name,
                organization_id=organization_id,
            ).one_or_none()