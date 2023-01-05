from operator import and_
from typing import List
from flask import Blueprint, request
from src.app_config import db
from flask_jwt_extended import get_jwt
from src.campaigns.models import Campaign
from src.library.decorators.authentication_decorators import admin_required
from src.library.utility_classes.custom_validator import Validator
from src.library.utility_classes.paginator import Paginator
from src.library.utility_classes.request_response import Response
from src.library.base_helpers.model_to_dict import model_to_dict
from .models import EventsInformation
from sqlalchemy.orm.session import make_transient

eventviews = Blueprint("eventviews", __name__)



'''
@route POST /event/create
@desc Create event
@access Admin
'''
@eventviews.route('/create', methods=["POST"])
@admin_required()
def create_event():
    body = request.json 
    body['organization_id'] = get_jwt().get('org')

    try:
        result_bool, result_data = EventsInformation.register(body)
        print(result_bool)
        if result_bool:
            return Response(True, model_to_dict(result_data)).respond()
        return Response(False, result_data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
     

'''
@route GET /event
@desc List events
@access Admin
'''
@eventviews.route('', methods=["GET"])
@admin_required()
def list_events():
    try:
        data = Paginator(
            model=EventsInformation,
            query=EventsInformation.query,
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result

        for event in data['rows']:
            campaign = Campaign.fetch_by_id(event.get('campaign_id')) if event.get('campaign_id') is not None else None
            event['campaign'] = model_to_dict(campaign)

        return Response(True, data).respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()
    
    
'''
@route PATCH /event/<uuid>
@desc Update Event by ID
@access Admin
'''
@eventviews.route("<uuid:id>", methods=["PATCH"])
@admin_required()
def update_event(id):
        try:
            body = request.json 
            fields = EventsInformation.fetch_by_id(id, organization_id=get_jwt().get('org'))

            # validations
            if not fields:
                return Response(False, 'This event does not exist').respond()
            unallowed_fields = ['id', 'organization_id']

            for field in body.keys():
                if field not in unallowed_fields:
                    setattr(fields, field, body.get(field))

            db.session.add(fields)
            db.session.commit()

            return Response(True, model_to_dict(fields)).respond()
        except Exception as e:
            print(e)
            return Response(False, str(e), 500).respond()
        

'''
@route GET /event/info/<uuid>
@desc Get event by ID
@access Admin
'''
@eventviews.route("/info/<uuid:id>", methods=["GET"])
@admin_required()
def event_info_by_id(id):
    event: EventsInformation = EventsInformation.fetch_by_id(id, organization_id=get_jwt().get('org'))
    if not event:
        return Response(False, "This event does not exist").respond()

    campaign = Campaign.fetch_by_id(event.campaign_id) if event.campaign_id is not None else None
    event = model_to_dict(event)
    event['campaign'] = model_to_dict(campaign)
     
    return Response(True, event).respond()


'''
@route DELETE /event/<uuid>
@desc Delete event by ID
@access Admin
'''
@eventviews.route("", methods=["DELETE"])
@admin_required()
def delete_event():
    try:
        body = request.json
        if not body or body.get('ids') is None:
            return Response(False, '`ids` is a required field').respond()

        event_ids = body.get('ids', [])
        if len(event_ids) == 0:
            return Response(False, 'No Events to perform DELETE operation on').respond()
        
        EventsInformation.delete_many_by_id(event_ids, get_jwt().get('org'))
        return Response(True, 'Event(s) deleted successfully').respond()
    except Exception as e:
        print(e)
        return Response(False, str(e), 500).respond()


'''
@route POST /event/clone
@desc Clone Event
@access Admin
'''
@eventviews.route("/clone", methods=["POST"])
@admin_required()
def clone_event():
     try:
          body = request.json
          events = body.get('events', [])

          if len(events) == 0:
               return Response(False, 'No package to perform CLONE operation on').respond()

          events = db.session.query(EventsInformation)\
               .filter(
                    and_(
                         EventsInformation.id.in_(events),
                         EventsInformation.organization_id == get_jwt().get('org')
                    )
               )\
               .all()
          for event in events:
               make_transient(event)
               event.id = None
               event.name += " (cloned)"
               db.session.add(event)
               db.session.commit()

          data = Paginator(
               model=EventsInformation,
               query_string=Paginator.get_query_string(request.url),
               organization_id=get_jwt().get('org')
          ).result

          return Response(True, data).respond()
     except Exception as e:
          print(e)
          return Response(False, str(e), 500).respond()