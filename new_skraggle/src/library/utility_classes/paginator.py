from typing import Any, List
from urllib.parse import parse_qs, urlparse

from sqlalchemy import desc
from src.library.base_helpers.model_to_dict import model_to_dict


class Paginator:
    def __init__(self, model, query=None, query_string: str = None, organization_id: str = None):
        '''
        Creates paginated queries and returns their results as a list of dictionaries.

        Example:
        ```
        users_with_no_middle_name = Paginator(
            model=ContactUsers,
            query=ContactUsers.query.filter_by(middle_name = None),
            query_string=Paginator.get_query_string(request.url),
            organization_id=get_jwt().get('org')
        ).result
        print(users_with_no_middle_name) # -> [{ "first_name": "Icheka", "last_name": "Ozuru", "middle_name": None }]
        ```
        '''

        parsed_query_string = self.parse_query_string(query_string)
        archived = parsed_query_string.get('archived')
        if archived == 'true':
            archived = True
        elif archived == 'false':
            archived = False
        else:
            archived = None

        self.result: List[dict[str, Any]] = Paginator.paginate(
            model=model,
            query=query or model.query,
            organization_id=organization_id,
            cursor=parsed_query_string.get('cursor'),
            direction=parsed_query_string.get('direction'),
            limit=parsed_query_string.get('limit'),
            archived=archived
        )

    @classmethod
    def get_query_string(cls, url: str = None):
        if not url:
            raise Exception(
                'Paginator::get_query_string() requires a `url` argument')
        return urlparse(url).query

    @classmethod
    def paginate(
        cls, model=None, query=None, cursor=-1, direction: str = 'after', archived: bool = None,
        limit: int = 10, organization_id: str = None
    ):
        '''
        Performs a seek-based pagination operation on the given `query`. 
        Returns a dict[str, List | boolean] that has `rows` -> List[dict[str, Any]], `has_next` -> boolean and `has_previous` -> boolean as keys

        Examples:
        `(i) Paginate without prior filtering`
        ```
        data = Paginator.paginate(query=MyModel.query, cursor='25', direction='after', limit=25, organization_id='ABC')
        print(data) # -> { 'rows': [], 'has_next': False, 'has_previous': True }
        ```
        `(ii) Paginate with prior filtering`
        ```
        # This will search for rows where `name` matches "%{search_string}%"
        search_string = 'nathan'
        filter_query = MyModel.query.filter(
            MyModel.name.ilike(f"%{search_string}%")
        )
        data = Paginator.paginate(query=filter_query, cursor='25', direction='after', limit=25, organization_id='ABC')
        print(data) # -> { 'rows': [], 'has_next': False, 'has_previous': True }
        ```
        '''
        cursor = cursor or -1

        if not model:
            raise Exception("Paginator.paginate() requires a `model` argument")

        query = query or model.query
        query = query.order_by(desc(model.sn)).filter(
            model.row_deleted == False)
        if archived == True or archived == False:
            query = query.filter_by(archived=archived)

        if not direction or not limit:
            return dict(
                rows=[model_to_dict(row) for row in query.filter().all()],
                has_next=False,
                has_previous=False
            )

        sn = int(cursor)

        result = {}
        rows = None

        if sn == -1:
            count = (
                model
                .query
                .count()
            )
            sn = count + 1

        if direction == 'after':
            rows = (
                query
                .filter(model.sn < sn)
                .filter_by(organization_id=organization_id if organization_id else organization_id != None)
                .limit(limit)
            )

            result['rows'] = [model_to_dict(row) for row in rows]

            if len(result['rows']) == 0:
                result['has_next'] = False
            else:
                result['has_next'] = query.filter(
                    model.sn < rows[-1].sn).first() != None
            result['has_previous'] = query.filter(
                model.sn > sn).first() != None
        else:
            rows = (
                query
                .filter(model.sn > sn)
                .filter_by(organization_id=organization_id if organization_id else organization_id != None)
                .limit(limit)
            )
            result['rows'] = [model_to_dict(row) for row in rows]

            if len(result['rows']) == 0:
                result['has_previous'] = False
            else:
                result['has_previous'] = query.filter(
                    model.sn > rows[0].sn).first() != None
            result['has_next'] = query.filter(model.sn < sn).first() != None

        return result

    @classmethod
    def parse_query_string(cls, query_string: str):
        '''
        Parses the query portion of a URL and extracts information that defines a page.
        Here, "page" refers to the result set of a DB WHERE query with `cursor`, `direction` and `limit` specified.

        Example:
        ```
        query_url = "name=Icheka&status=active&cursor=5&direction=before&limit=5"
        print(Paginator.parse_query_string(query_url)) # -> { "cursor": "5", "direction": "after", "limit": "5" }
        ```
        '''
        data = dict(
            cursor=None,
            direction=None,
            limit=None,
            archived=None
        )
        if not query_string or len(query_string) == 0:
            return data

        parsed_qs = parse_qs(query_string)

        def get(key: str = None):
            if key is None:
                return None
            query_key = parsed_qs.get(key)
            if not query_key:
                return None
            return None if len(query_key) == 0 else query_key[0]

        for key in data.keys():
            data[key] = get(key)

        return data
