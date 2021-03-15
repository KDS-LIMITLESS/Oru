import iso3166
import phonenumbers
from phonenumbers import is_valid_number_for_region
import aiohttp
import asyncio


class Country:

    async def get_country_name(self, country_name):
        c_name = country_name.upper()
        try:
            country_name = iso3166.countries[c_name]
            self.country_name = country_name
            return self.country_name.name.upper()
        except KeyError:
            raise LookupError("Invalid country name")

    async def get_country_region(self):
        try:
            self.region = self.country_name.alpha2
            return self.region
        except NameError:
            raise LookupError
        (
            f"region code for {self.country_name} not found! Please select another country."
        )

    async def get_user_phonenumber(self, phonenumber: str):
        try:
            phone = phonenumbers.parse(phonenumber, self.region)
        except phonenumbers.phonenumberutil.NumberParseException:
            raise TypeError("Invalid Phone Number")
        if is_valid_number_for_region(phone, self.region):
            return phonenumbers.format_number(phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        raise Exception(f"{phonenumber} is not a valid number format for {self.country_name.name.capitalize()}")

    async def get_states(self, state_name: str):
        country_id = self.region
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://naijacrawl.com/api/v3/free-get-state-list?country_code={country_id}") as resp:
                # resp = requests.get(f"http://naijacrawl.com/api/api/v2/free-get-state-list?country_code={country_id}")
                # convert the Response object to dict with json.loads()
                resp_dict = await resp.json()
                # self.resp_dict = json.loads(resp)
                for self.state_id, self.state in resp_dict.items():
                    if state_name.capitalize() == self.state:
                        return self.state
                raise NameError(f"{state_name.capitalize()} is not a state in {self.country_name.name.capitalize()}!")

    async def get_city(self, city_name):
        state_id = self.state_id
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://naijacrawl.com/api/v3/free-get-city-list?state_id={state_id}") as resp:
                # response = await requests.get(f"http://naijacrawl.com/api/api/v2/free-get-city-list?state_id={state_id}").text.capitalize()
                # response_dict = json.loads(response)
                response_dict = await resp.json()
                for _, city in response_dict.items():
                    if city_name.lower() in city.lower():
                        return city
                raise NameError(f"{city_name.capitalize()} is not a city in {self.state}")
