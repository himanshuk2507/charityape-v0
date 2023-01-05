from operator import and_
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pathlib import Path
from os import getcwd
from src.app_config import ModelMixin, OrganizationMixin, db

import rsa

class EventBriteKey(ModelMixin, OrganizationMixin, db.Model):
     __tablename__ = "EventBriteKey"
     admin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Admin.id'), nullable=False)
     public_key = db.Column(db.Text, nullable=False)
     oauth_token = db.Column(db.LargeBinary, nullable=False)
     
     
     def __init__(self, admin_id = None, public_key = None, oauth_token = None, organization_id = None):
          self.admin_id = admin_id
          self.public_key = public_key
          self.oauth_token = oauth_token
          self.organization_id = organization_id
     
     
     def update(self, data: dict = None):
          if not data:
               raise Exception('EventBriteKey.update() requires an argument for `data`') 
          
          try:
               for field in data:
                    setattr(self, field, data.get(field))
               return super().update(data=data)
          except Exception as e:
               print(e)
               return False, e
     
     
     @classmethod
     def register(cls, data: dict = None):
          if not data:
               raise Exception('EventBriteKey.register() requires an argument for `data`')

          required_fields = ['oauth_token', 'organization_id']
          for field in required_fields:
               if field not in data.keys():
                    return False, f"{field} is a required field"
          
          # 1. create key pair
          # 2. store private key
          # 3. encrypt paypal secret
          # 4. save encrypted secret

          publicKey, privateKey = rsa.newkeys(1024)
          
          file_path = Path(getcwd())/'enc'/'eventbrite'/'oauth_key{}'.format(data.get('organization_id'))
          
          with open(file_path, 'w') as f:
               f.write(str(privateKey)[11:-1])
               
          
          encrypted_oauth_key = rsa.encrypt(data.get('oauth_token').encode(), publicKey)
          
          datas = {}
          datas['public_key'] = str(publicKey)[10:-1]
          datas['oauth_token'] = encrypted_oauth_key
          datas['admin_id'] = data.get('admin_id')
          datas['organization_id'] = data.get('organization_id')
          
          events = cls(**datas)
          db.session.add(events)
          db.session.flush()
          db.session.commit()

          return True, events
     


class EventbriteEvents(ModelMixin, OrganizationMixin, db.Model):
     __tablename__ = "EventbriteEvents"
     
     campaign_id = db.Column(UUID(as_uuid=True), db.ForeignKey('Campaign.id'), nullable=True)
     eventbrite_id = db.Column(db.String(50), nullable=False)
     event_name = db.Column(db.Text, nullable=False)
     description = db.Column(db.Text, nullable=False)
     url = db.Column(db.Text, nullable=False)
     time_zone = db.Column(db.Text, nullable=False)
     start_time = db.Column(db.DateTime, nullable=False)
     end_time = db.Column(db.DateTime, nullable=False)
     event_image = db.Column(db.String(255), nullable=False)
     event_sold_out_message = db.Column(db.String(255), nullable=False)
     venue = db.Column(db.String(255), nullable=False)
     address = db.Column(db.String(255), nullable=False)
     city = db.Column(db.String(255), nullable=False)
     state = db.Column(db.String(255), nullable=False)
     zip_country = db.Column(db.Integer, nullable=False)
     enable_map = db.Column(db.Boolean, nullable=False)
     display_option = db.Column(db.String(100), nullable=False)
     total_participant = db.Column(db.Integer, nullable=False)
     enable_one_time_donation = db.Column(db.Boolean, nullable=False)
     event_has_reg_cutoff_date = db.Column(db.Boolean, nullable=False)
     admin_notification = db.Column(db.PickleType, nullable=False)
     reciept_type = db.Column(db.String(255), nullable=False)
     reciept_title = db.Column(db.String(255), nullable=False)
     reciept_category = db.Column(db.String(255), nullable=False)
     reciept_description = db.Column(db.String(255), nullable=False)
     sender_name = db.Column(db.String(255), nullable=False)
     reply_email = db.Column(db.String(255), nullable=False)
     subject = db.Column(db.String(255), nullable=False)
     body = db.Column(db.Text, nullable=False)
     archived = db.Column(db.Boolean, default=False)
     
     
     def __init__(self,
          eventbrite_id,
          event_name,
          description,
          url,
          time_zone,
          start_time,
          end_time,
          event_image,
          event_sold_out_message,
          venue,
          address,
          city,
          state,
          zip_country,
          enable_map,
          display_option,
          total_participant,
          enable_one_time_donation,
          event_has_reg_cutoff_date,
          admin_notification,
          reciept_type,
          reciept_title,
          reciept_category,
          reciept_description,
          sender_name,
          reply_email,
          subject,
          organization_id,
          archived=None,
          campaign_id=None,
          body=None
                  ):
          self.eventbrite_id = eventbrite_id
          self.event_name = event_name
          self.description = description
          self.url = url
          self.time_zone = time_zone
          self.start_time = start_time
          self.end_time = end_time
          self.event_image = event_image
          self.event_sold_out_message = event_sold_out_message
          self.venue = venue
          self.address = address
          self.city = city
          self.state = state
          self.zip_country = zip_country
          self.enable_map = enable_map
          self.display_option = display_option
          self.total_participant = total_participant
          self.enable_one_time_donation = enable_one_time_donation
          self.event_has_reg_cutoff_date = event_has_reg_cutoff_date
          self.admin_notification = admin_notification
          self.reciept_type = reciept_type
          self.reciept_title = reciept_title
          self.reciept_category = reciept_category
          self.reciept_description = reciept_description
          self.sender_name = sender_name
          self.reply_email = reply_email
          self.subject = subject
          self.organization_id = organization_id
          self.archived = archived
          self.campaign_id = campaign_id
          self.body = body
          
     
     @classmethod
     def register(cls, data: dict):
          if not data:
               raise Exception('Fields.register() requires an argument for `data`')
          
          event = cls(**data)
          db.session.add(event)
          db.session.flush()
          db.session.commit()

          return True, event