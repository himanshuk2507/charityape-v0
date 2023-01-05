from flask import Blueprint, request, session
from src.integrations.eventbrite.models import EventBriteKey, EventbriteEvents
from flask_jwt_extended import get_jwt
from src.app_config import db
from src.library.utility_classes.paginator import Paginator
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.request_response import Response
from src.integrations.eventbrite.eventbrite import EventBrite
from src.library.base_helpers.model_to_dict import model_to_dict
from src.campaigns.models import Campaign


eventbrite = Blueprint('eventbrite', __name__)



'''
@route POST /eventbrite-settings
@desc Set Outh Key for this Admin's Eventbrite account
@access Admin
'''
@eventbrite.route('eventbrite-settings', methods=['POST'])
@admin_required()
def set_eventbrite_route():
     try:
          admin_id = get_jwt().get('id')
          organization_id = get_jwt().get('org')
          # print(organization_id)
          body = request.json

          event: EventBriteKey = EventBriteKey.query.filter_by(
               organization_id = organization_id,
               admin_id = admin_id
          ).one_or_none()
          
          if not event:
               body['admin_id'] = admin_id
               body['organization_id'] = organization_id

               result_bool, result_data = EventBriteKey.register(body)
               
               if not result_bool:
                    return Response(False, result_data).respond()
          else:
               result_bool, result_data = event.update(body)
               
               if not result_bool:
                    return Response(False, result_data).respond()
          
          return Response(True, 'Settings updated successfully!').respond()
     except Exception as e:
          print(e)
          return Response(False, str(e), 500).respond()
     
     


'''
@route GET /eventbrite-settings
@desc Confirm whether this Admin's EventBriteKey is configured
@access Admin
'''
@eventbrite.route('eventbrite-settings', methods=['GET'])
@admin_required()
def confirm_eventbrite_configuration_route():
    try:
        admin_id = get_jwt().get('id')
        organization_id = get_jwt().get('org')

        event = EventBriteKey.query.filter_by(
            admin_id = admin_id,
            organization_id = organization_id
        ).one_or_none()

        if not event:
            return Response(False, 'EventBriteKey is not configured for this account').respond()

        return Response(True, 'EventBriteKey has been configured for this account').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
   



'''
@route POST /eventbrite
@desc Create Event on Eventbrite
@access Admin
'''
@eventbrite.route('', methods=['POST'])
@admin_required()
def create_eventbrite_route():
     try:
          admin_id = get_jwt().get('id')
          organization_id = get_jwt().get('org')
          # print(organization_id)
          body = request.json

          result_bool, result_data = EventBrite(organization_id=organization_id, admin_id=admin_id).create_event(body)
               
          if not result_bool:
               return Response(False, result_data).respond()
          
          return Response(True, result_data).respond()
     except Exception as e:
          print(e)
          return Response(False, str(e), 500).respond()
     

'''
@route GET /eventbrite
@desc List Events on Eventbrite
@access Admin
'''
@eventbrite.route('', methods=['GET'])
@admin_required()
def fetch_all_eventbrite_route():
    try:
        data = Paginator(
            model=EventbriteEvents,
            query=EventbriteEvents.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
   
   


'''
@route PATCH /eventbrite/<uuid>
@desc Update Event by ID
@access Admin
'''
@eventbrite.route("<uuid:id>", methods=["PATCH"])
@admin_required()
def update_eventbrite(id):
     try:
          body = request.json 
          fields = EventbriteEvents.fetch_by_id(id, organization_id=get_jwt().get('org'))

          # validations
          if not fields:
               return Response(False, 'This event does not exist').respond()
          unallowed_fields = ['id', 'organization_id', 'url']

          for field in body.keys():
               if field not in unallowed_fields:
                    setattr(fields, field, body.get(field))
          
          
          update = EventBrite(organization_id=get_jwt().get('org'), admin_id= get_jwt().get('id')).update_event(body=body, eventbrite_id=fields.eventbrite_id)
          if update == 200:
               db.session.add(fields)
               db.session.commit()
               return Response(True, model_to_dict(fields)).respond()
          return Response(False, "Something went wrong", 500).respond()
     except Exception as e:
          print(e)
          return Response(False, str(e), 500).respond()



'''
@route POST /eventbrite/clone/<uuid:id>
@desc Clone Event
@access Admin
'''
@eventbrite.route("/clone/<uuid:id>", methods=["GET"])
@admin_required()
def clone_eventbrite(id):
     try:
          clone_bool, clone_data = EventBrite(organization_id=get_jwt().get('org'), admin_id= get_jwt().get('id')).clone_event(id=id)
          if clone_bool:
               return Response(True, clone_data).respond()
          return Response(False, clone_data, 500).respond()
     except Exception as e:
          print(e)
          return Response(False, str(e), 500).respond()
     



'''
@route GET /eventbrite/info/<uuid>
@desc Get event by ID
@access Admin
'''
@eventbrite.route("/info/<uuid:id>", methods=["GET"])
@admin_required()
def eventbrite_info_by_id(id):
    event: EventbriteEvents = EventbriteEvents.fetch_by_id(id, organization_id=get_jwt().get('org'))
    if not event:
        return Response(False, "This event does not exist").respond()

    campaign = Campaign.fetch_by_id(event.campaign_id) if event.campaign_id is not None else None
    event = model_to_dict(event)
    event['campaign'] = model_to_dict(campaign)
     
    return Response(True, event).respond()



'''
@route DELETE /eventbrite
@desc Delete event by ID
@access Admin
'''
@eventbrite.route("", methods=["DELETE"])
@admin_required()
def delete_eventbrite():
     try:
          body = request.json
          if not body or body.get('ids') is None:
               return Response(False, '`ids` is a required field').respond()

          event_ids = body.get('ids', [])
          if len(event_ids) == 0:
               return Response(False, 'No Events to perform DELETE operation on').respond()
        
          EventbriteEvents.delete_many_by_id(event_ids, get_jwt().get('org'))
          return Response(True, 'Event(s) deleted successfully').respond()
     except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()