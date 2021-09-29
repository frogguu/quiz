#!/usr/local/bin/python3.9
from wsgiref.handlers import CGIHandler
import cgitb
print("Content-Type: text/html\n\r\n")
cgitb.enable(display=1, format="html")
from app import app
CGIHandler().run(app)
