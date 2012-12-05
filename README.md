![alt text](https://raw.github.com/stoneG/whiskey/master/whiskey.png "Surgeon General's Warning Goes Here")
Whiskey
=======
is a WSGI compliant server.

Starting the server
-------------------
```python
import whiskey as Whiskey

whiskey = Whiskey.distill('127.0.0.1', 8080, application)
whiskey.drink_forever()
# Where 'application' is a WSGI application
```

Supports these environ variables
--------------------------------
* Everything in os.environ
* Everything explicitly stated in
  [PEP333](http://www.python.org/dev/peps/pep-0333/).
