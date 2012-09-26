import json
import requests


class WunderError(Exception):
    pass

class AmbiguousLocationError(Exception):
    pass

class Forecast(object):
    def __init__(self, description, data):
        self.description = description
        for key in data.keys():
            setattr(self, key, data[key])


class Client(object):

    def __init__(self, api_key):
        self.api_key = api_key
        self._api_endpoint = "http://api.wunderground.com/api/{0}".format(api_key)

    def forecast(self, location):
        r = requests.get("{0}/q/forecast/{1}.json".format(self._api_endpoint, location))
        data = json.loads(r.content)

        # If the response contains a "results" key then the location was ambiguous, see
        # http://www.wunderground.com/weather/api/d/docs?d=data/index
        if data["response"].has_key("results"):
            raise AmbiguousLocationError("Location {0} is ambiguous".format(location))

        text = data["forecast"]["txt_forecast"]
        simple = data["forecast"]["simpleforecast"]
        reverse_txt_days = dict([[day["period"], day] for day in text["forecastday"]])
        reverse_simple_days = dict([[day["period"], day] for day in simple["forecastday"]])
        result = {}
        for period, day in reverse_simple_days.items():
            result[period] = Forecast(reverse_txt_days[period]["fcttext_metric"], day)
        return result


