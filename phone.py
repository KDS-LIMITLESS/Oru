import iso3166
import phonenumbers
from phonenumbers import is_valid_number_for_region




class Country:

    @classmethod
    def get_country_details(cls, country_name:str):
        c_name = country_name.upper()
        try:
            country_name = iso3166.countries[c_name]
            country_region = country_name.alpha2 
            return [country_name,country_region][0].name.upper()
        except KeyError:
            return f"{country_name} not found!"

        
        
        
