import iso3166
import phonenumbers
from phonenumbers import is_valid_number_for_region, phonenumberutil
from typing import List




class Country:


    @classmethod
    def get_country_details(cls, country_name):
        c_name = country_name.upper()
        try:
            country_name = iso3166.countries[c_name]
            return country_name.name.upper()
        except KeyError:
            return f"{country_name} not found!"

    @classmethod
    def get_country_region(cls, country):
        c = country.upper()
        try:
            country_name = iso3166.countries[c]
            region = country_name.alpha2
            return region
        except KeyError:
            return f"Region for {country} Not found"
        except phonenumbers.phonenumberutil.NumberParseException:
            return "Region not found!"
        

    @classmethod
    def get_user_phonenumber(cls, phonenumber:str, country):
        try:
            country_region = cls.get_country_region(country)
            phone = phonenumbers.parse(phonenumber,country_region)
        except phonenumbers.phonenumberutil.NumberParseException:
            return f"Please check the country name for mispelt words"    
        if is_valid_number_for_region(phone,country_region):
            return phonenumbers.format_number(phone,phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        return f"Invalid Number"
