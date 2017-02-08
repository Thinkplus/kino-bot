# -*- coding: utf-8 -*-

import forecastio
from airkoreaPy import AirKorea
from geopy.geocoders import GoogleV3

import slack
import utils

class Weather(object):

    def __init__(self, text=None):
        self.input = text
        self.config = utils.Config()
        self.slackbot = slack.SlackerAdapter()
        self.template = slack.MsgTemplate()

    def forecast(self, timely='current'):
        geolocator = GoogleV3()
        location = geolocator.geocode(utils.Profile().get_location())

        api_key = self.config.open_api['dark_sky']['TOKEN']
        lat = location.latitude
        lon = location.longitude
        dark_sky = forecastio.load_forecast(api_key, lat, lon)

        if timely == 'current':
            currently = dark_sky.currently()
            self.__forecast(currently, timely, location.address)
        elif timely == 'daily':
            hourly = dark_sky.hourly()
            self.__forecast(hourly, timely, location.address)
        elif timely == 'weekly':
            daily = dark_sky.daily()
            self.__forecast(daily, timely, location.address)

    def __forecast(self, forecast, timely, address):
        icon = forecast.icon
        summary = forecast.summary

        if timely == 'current':
            temperature = forecast.temperature
            fallback = summary + " " + str(temperature) + "도"
        else:
            temperature = None
            fallback = summary

        attachments = self.template.make_weather_template(address, icon, summary, temperature=temperature, fallback=fallback)
        self.slackbot.send_message(attachments=attachments)

    def air_quality(self):
        api_key = self.config.open_api['airkorea']['TOKEN']
        airkorea = AirKorea(api_key)

        station_name = utils.Profile().get_location(station=True)
        response = airkorea.forecast(station_name)
        attachments = self.template.make_air_quality_template(response)
        self.slackbot.send_message(attachments=attachments)
