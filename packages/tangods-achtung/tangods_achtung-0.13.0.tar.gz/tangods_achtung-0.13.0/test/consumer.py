"""
This is a very small web service that can be run and used to test
the HTTPConsumers property of Achtung. The server will print out any
reports it receives.

   $ pip install bottle
   $ python test/receiver.py

Then configure your achtung device with a HTTPReceiver http://localhost:8007
"""

from bottle import run, request, route


@route('/', method='GET')
def handle_get():
    # This is just used to check if the service is alive
    print("get")


@route('/', method='POST')
def handle_post():
    print("post", request.body.read())


run(host='localhost', port=8007, debug=True)
