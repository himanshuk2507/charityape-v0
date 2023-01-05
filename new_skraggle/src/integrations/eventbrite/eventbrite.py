from src.library.base_helpers.rsa_helpers import decrypt_rsa, eventbrite_private_key
from src.integrations.eventbrite.models import EventBriteKey, EventbriteEvents
import rsa
from src.app_config import Config
from requests import request as json_request
from json import loads as json_loads, dumps as json_dumps
from src.library.base_helpers.model_to_dict import model_to_dict


class EventBrite:
     '''
     Handles event and subscriptions using Eventbrite.
     :param data `The detail of the event to be created`
     '''
     def __init__(self, organization_id = None, admin_id = None):
          
          if not organization_id or not admin_id:
               raise Exception('`data`, `admin_id` and `organization_id` is required in EventBrite()')
          
          self.organization_id = organization_id
          self.admin_id = admin_id
          self.eventbrite_encrypt_data : EventBriteKey = EventBriteKey.query.filter_by(organization_id=self.organization_id, admin_id=self.admin_id).one_or_none()
          self.eventbrite_private = eventbrite_private_key(self.organization_id)
          self.oauthkey = rsa.decrypt(self.eventbrite_encrypt_data.oauth_token, self.eventbrite_private).decode()
          self.base_url = Config.EVENTBRITE_BASE_URL
          
     
     def header(self):
          '''
          This is to return the header
          '''
          return {
               'Authorization': f'Bearer {self.oauthkey}',
               'Accept': 'application/json',
               'Content-Type': 'application/json',
          }
     
     
     def eventbrite_organization_id(self):
          '''
          Return the organization id from eventbrite
          '''
          url = f"{self.base_url}/v3/users/me/organizations/"
          response = json_request("GET", url, headers=self.header())
          json_data = json_loads(response.text)
          organizationId = json_data['organizations'][0]['id']
          return organizationId
     
     
     def publish_event(self, event_id = None):
          '''
          Publish event after it has been created on eventbrite
          '''
          url = f"{self.base_url}/v3/events/{event_id}/publish/"
          response = json_request("POST", url, headers=self.header())
          resp_code = response.status_code
          return resp_code
     
     
     def create_ticket_class(self, event_id = None, capacity = None):
          '''
          Create ticket class for every event created
          '''
          if not event_id or not capacity:
               raise Exception('`event_id` and `capacity` is required')
          
          url = f"{self.base_url}/v3/events/{event_id}/ticket_classes/"

          payload = json_dumps({
               "ticket_class": {
                    "name": "VIP",
                    "quantity_total": int(capacity),
                    "cost": "USD,100"
               }
          })

          response = json_request("POST", url, headers=self.header(), data=payload)
          if response.status_code == 200:
               return True
          return False

          
     def create_event(self, data:dict = None):
          '''
          Created event on eventbrite
          '''
          if not data:
               raise Exception('`data(event information)` is required')
          
          required_fields = [
                    'event_name', 'description', 'time_zone', 'start_time', 
                    'event_sold_out_message','venue',
                    'address','city','state','zip_country',
                    'enable_map','display_option',
                    'total_participant','end_time', 
                    'enable_one_time_donation',
                    'event_has_reg_cutoff_date',
                    'admin_notification', 'event_image',
                    'reciept_type','reciept_title',
                    'reciept_category','reciept_description',
                    'sender_name','reply_email','subject','body'
               ]
          for field in required_fields:
               if field not in data.keys():
                    return False, f"`{field}` is required in the body"
               
          url = f"{self.base_url}/v3/organizations/{self.eventbrite_organization_id()}/events/"

          payload = json_dumps({
               "event": {
                    "name": {
                         "html": data.get('event_name')
                    },
                    "start": {
                         "timezone": data.get('time_zone'),
                         "utc": data.get('start_time')
                    },
                    "end": {
                         "timezone": data.get('time_zone'),
                         "utc": data.get('end_time')
                    },
                    "currency": "USD"
               }
          })
          

          response = json_request("POST", url, headers=self.header(), data=payload)
          if response.status_code == 200:
               resp_data = json_loads(response.text)
               event_id = resp_data.get('id')
               event_url = resp_data.get('url')
               ticket_class = self.create_ticket_class(event_id=event_id, capacity=data.get('total_participant'))
               if ticket_class:
                    self.publish_event(event_id=event_id)
               
               data['eventbrite_id'] = event_id
               data['url'] = event_url
               data['organization_id'] = self.organization_id
               
               event_bool, event = EventbriteEvents.register(data)
               if event_bool:
                    return True, model_to_dict(event)
               return False, event
          return False, response.text
     
     
     def update_event(self, body:dict = None, eventbrite_id = None):
          '''
          Update event on eventbrite
          '''
          if not body or not eventbrite_id:
               raise Exception("`body` and `eventbrite_id` is required")
          
          event = EventbriteEvents.query.filter_by(eventbrite_id=eventbrite_id).first()
          url = f"{self.base_url}/v3/events/{eventbrite_id}/"
          payload = json_dumps({
               "event": {
                    "start": {"timezone": body.get('time_zone') if 'time_zone' in body.keys() else event.time_zone, "utc": body.get('start_time')} if 'start_time' in body.keys() else {"timezone": event.time_zone, "utc": event.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")},
                    "end":{"timezone": body.get('time_zone') if 'time_zone' in body.keys() else event.time_zone, "utc": body.get('end_time')} if 'end_time' in body.keys() else {"timezone": event.time_zone, "utc": event.end_time.strftime("%Y-%m-%dT%H:%M:%SZ")},
                    "name": {"html": body.get('event_name')} if 'event_name' in body.keys() else {"html": event.event_name},
                    "capacity" if 'total_participant' in body.keys() else 'capacity': body.get('total_participant') if 'total_participant' in body.keys() else body.get('total_participant')
               }
          })
          response = json_request("POST", url, headers=self.header(), data=payload)
          return response.status_code
     
     
     def clone_event(self, id):
          '''
          Clone event on eventbrite
          '''
          events = EventbriteEvents.fetch_by_id(id, self.organization_id)
          
          url = f"{self.base_url}/v3/events/{events.eventbrite_id}/copy/"
          response = json_request("POST", url, headers=self.header())
          resp_data = json_loads(response.text)
          if response.status_code == 200:
               body = {}
               body['organization_id'] = self.organization_id
               body['eventbrite_id'] = resp_data['id']
               body['event_name'] = events.event_name
               body['description'] = events.description
               body['url'] = resp_data['url']
               body['time_zone'] = events.time_zone
               body['start_time'] = events.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
               body['end_time'] = events.end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
               body['event_image'] = events.event_image
               body['event_sold_out_message'] = events.event_sold_out_message
               body['venue'] = events.venue
               body['address'] = events.address
               body['city'] = events.city
               body['state'] = events.state
               body['zip_country'] = events.zip_country
               body['enable_map'] = events.enable_map
               body['display_option'] = events.display_option 
               body['total_participant'] = events.total_participant 
               body['enable_one_time_donation'] = events.enable_one_time_donation 
               body['event_has_reg_cutoff_date'] = events.event_has_reg_cutoff_date 
               body['admin_notification'] = events.admin_notification
               body['reciept_type'] = events.reciept_type 
               body['reciept_title'] = events.reciept_title
               body['reciept_category'] = events.reciept_category 
               body['reciept_description'] = events.reciept_description 
               body['sender_name'] = events.sender_name 
               body['reply_email'] = events.reply_email 
               body['subject'] = events.subject 
               body['body'] = events.body 
               body['archived'] = events.archived 
               
               event_bool, event = EventbriteEvents.register(body)
               if event_bool:
                    return True, model_to_dict(event)
               return False, event
          return False, response.text