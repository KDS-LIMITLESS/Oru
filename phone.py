import iso3166
import phonenumbers
from phonenumbers import is_valid_number_for_region, phonenumberutil
import requests
import json


class Country:


    def get_country_name(self, country_name):
        c_name = country_name.upper()
        try:
            country_name = iso3166.countries[c_name]
            self.country_name = country_name
            return self.country_name.name.upper()
        except KeyError:
            return f"{country_name} not found!"

    def get_country_region(self):
        try:
            #country_name = iso3166.countries[c]
            self.region = self.country_name.alpha2
            return self.region
        except KeyError:
            return f"Region for {self.country_name} Not found"
        except phonenumbers.phonenumberutil.NumberParseException:
            return "Region not found!"
        
    def get_user_phonenumber(self, phonenumber:str):
        try:
            #country_region = cls.get_country_region(country)
            phone = phonenumbers.parse(phonenumber,self.region)
        except phonenumbers.phonenumberutil.NumberParseException:
            return f"Please check the country name for mispelt words"    
        if is_valid_number_for_region(phone,self.region):
            return phonenumbers.format_number(phone,phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return f"Invalid Number"

    def get_states(self):
        country_id = self.region  #get_country_region(country)
        resp = requests.get(f"http://naijacrawl.com/api/api/v2/free-get-state-list?country_code={country_id}").text.capitalize()
        # convert the Response object to dict with json.loads()
        self.resp_dict = json.loads(resp)
        return self.resp_dict

    def get_city(self, state):
        for state_id, state_name in self.resp_dict.items():
            if state.lower() == state_name:
                response = requests.get(f"http://naijacrawl.com/api/api/v2/free-get-city-list?state_id={state_id}").text.capitalize()
                response_dict = json.loads(response)
                return response_dict
        
        return f"{state} is not a state in {self.country_name.name} "
            


