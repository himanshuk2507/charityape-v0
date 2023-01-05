from src.app_config import db
from src.tests.integration.admin.fixtures import AdminFixture
from src.integrations.eventbrite.models import EventBriteKey, EventbriteEvents



class EventBriteKeyFixture:
     '''
     Create an instance of EventBriteKey for testing with.
     '''

     def __init__(self, data=None):
          if not data:
                data = self.default_obj()

          self.organization_id = AdminFixture().admin.organization_id

          data["organization_id"] = self.organization_id
          event: EventBriteKey = EventBriteKey(**data)

          db.session.add(event)
          db.session.flush()
          db.session.commit()

          self.field = event

     @classmethod
     def default_obj(cls):
          return dict(oauth_token="GQJQEU6QGKXRBKA32RC5")
     


class EventbriteEventsFixtures:
     '''
     Create an instance of EventBriteKEvents for testing with.
     '''
     def __init__(self, data=None):
          if not data:
                data = self.default_obj()

          self.organization_id = AdminFixture().admin.organization_id
          
          event_info = EventbriteEvents.query.filter_by().first()
          if not event_info:
               data["organization_id"] = self.organization_id
               event_info: EventbriteEvents = EventbriteEvents(**data)

               db.session.add(event_info)
               db.session.flush()
               db.session.commit()

          self.event_info = event_info
          self.id = event_info.id
     
     @classmethod
     def default_obj(cls):
          return dict(
               event_name = "Skraggle Event",
               description = "Donation for Test",
               time_zone = "America/Los_Angeles",
               start_time = "2022-08-12T02:00:00Z",
               end_time = "2022-09-01T05:00:00Z",
               event_sold_out_message = "This is Test",
               venue = "USA",
               address = "California",
               city = "California",
               state = "California",
               zip_country = "600337",
               enable_map = False,
               display_option = "test",
               total_participant = 100,
               enable_one_time_donation = True,
               event_has_reg_cutoff_date = False,
               admin_notification = "test",
               event_image = "https://image.com",
               reciept_type = "test",
               reciept_title = "Test",
               reciept_category = "test",
               reciept_description = "This is test",
               sender_name = "Skraggle Test",
               reply_email = "test@gmail.com",
               subject = "Test",
               body = "This is just test"
          )