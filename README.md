# Scrape-A-Long

## Running tests as a local module

1. clone the repository

    ::sh
    git clone git@github.com:manuelep/scrapealong.git

1. install requirements

    ::sh
    cd path/to/scrapealong
    pip install -r requirements.txt

1. module setup

        ::sh
        touch scrapealong/settings_private.py

    create the `settings_private.py` file as showed before and fill it with the
    subsequent content adapted to your needs:

        ::python
        # -*- coding: utf-8 -*-

        QUEUE_LENGTH = 2

        TRIPADVISOR_HOTES_LOCATIONS = [
            # Try something like:
            # 'Hotels-g187849-Milan_Lombardy-Hotels.html',
        ]

        TRIPADVISOR_RESTAURANTS_LOCATIONS = [
            # Try something like:
            # 'Restaurants-g187849-Milan_Lombardy.html',
        ]

1. run the tests

    python3 -m scrapealong.utest

## Using the module inside a py4web application

Just include this library as a sub-module in your py4web applications.

## Configure

Just add a *settings_private.py* file in each path:

  * `tripadvisor -> hotels`
  * `tripadvisor -> restaurant`
  * `tripadvisor -> turism`

with the values of location *uri* you want to be monitored (follow the example in
parallel *settings.py* files).
