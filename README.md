# Spotify-Flask-Plotly Baseline Template

## Introduction 

This repo serves as a baseline template for anyone wishing to develop a Flask App that uses the [spotipy](https://spotipy.readthedocs.io/en/2.19.0/) library and needs to use OAuth2 to authenticate. I struggled quite a bit doing that and so I'm sharing this template in the hopes that it'll be easier for anyone to do this. 

I've also taken reference from [here](https://towardsdatascience.com/web-visualization-with-plotly-and-flask-3660abf9c946?gi=26b80bee705c) which shows how to very easily include Plotly charts within Flask (without incurring all the trouble of having to integrate Dash and Flask). 

## Usage

Simply fork the repo and you can start modifying `app.py` to suit your needs. The template is designed to be run on Heroku. To ensure that it runs properly, you must set the following environmental variables within Heroku:

- SPOTIPY_SECRET_ID
- SPOTIPY_SECRET_KEY
- SPOTIPY_REDIRECT_URI

These can be gotten from your Spotify Developer dashboard. Ensure that the REDIRECT_URL is https:<your-heroku-app>/ and that it is the same in both your Spotify Developer dashboard and Heroku. 

Please do credit if you use this baseline. Thank you and all the best!
