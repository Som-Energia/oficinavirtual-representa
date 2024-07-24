import httpx
from yamlns import ns
import os
from pydantic import (
    BaseModel,
    AwareDatetime,
    EmailStr,
    UUID4,
)

debug = True

class NewUser(BaseModel):
    username: str
    name: str
    is_active: bool
    last_login: AwareDatetime
    groups: list[UUID4]
    email: EmailStr
    attributes: dict
    path: str
    type: str

class UserProvision:

    def _api(self, url, payload=None, params=None, method=None):
        BASE_URL=os.environ.get("AUTHENTIK_API_URL")
        TOKEN=os.environ.get("AUTHENTIK_TOKEN")
        full_url = f"{BASE_URL}/api/v3/{url}"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f"Bearer {TOKEN}"
        }
        method = method if method is not None else "POST" if payload else "GET"
        #debug and print(f"{method} {full_url}\n{payload and ns(payload).dump()}")

        response = httpx.request(method, full_url, params=params, headers=headers, data=payload)

        response.raise_for_status()

        print('RESPONSE:',response.text)
        return response.json() if response.text else None


    def version(self):
        return self._api("admin/version/")


    def get_by_username(self, username):
        user_id = self.get_id_by_username(username)
        try:
            return self._api(f"core/users/{user_id}/", payload={}, method="GET")
        except httpx.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def create(self, user: NewUser):
        try:
            return self._api(f"core/users/", payload=user.model_dump_json(), method="POST")
        except httpx.HTTPError as e:
            print(e.response.status_code, e.response.text)
            raise

    def remove(self, user_id):
        try:
            return self._api(f"core/users/{user_id}/", payload={}, method="DELETE")
        except httpx.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def get_id_by_username(self, username):
        try:
            result = self._api(f"core/users/", params={'username':username}, method="GET")
        except httpx.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
        if not result.get('results'): return None
        return result['results'][0]['pk']


# This implementation uses the official authentik python client
# But importing the library slows down feedback loop for tests a lot!!!.
# Commented out just in case future releases solve this problem.
"""
from authentik_client.api_client import ApiClient
from authentik_client.api.core_api import CoreApi
from authentik_client.configuration import Configuration
from authentik_client.rest import ApiException
from pprint import pprint
class UserProvision_Lib:
    def __init__(self):
        BASE_URL=os.environ.get("AUTHENTIK_API_URL")
        TOKEN=os.environ.get("AUTHENTIK_TOKEN")

        self.configuration = Configuration(
            host = f"{BASE_URL}/api/v3",
            access_token = TOKEN
        )

    def retrieve(self, user_id):
        with ApiClient(self.configuration) as api_client:
            api_instance = CoreApi(api_client)

            try:
                return api_instance.core_users_retrieve(id=user_id).model_dump()
                print("The response of AdminApi->admin_apps_list:\n")
                pprint(api_response)
            except ApiException as e:
                print("Exception when calling AdminApi->admin_apps_list: %s\n" % e)
"""
