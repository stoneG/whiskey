Whiskey
=======
is a WSGI compliant server.

Starting the server
-------------------
```python
import whiskey as Whiskey

whiskey = Whiskey.distill('127.0.0.1', 8080, application, Handler=Bartender)
# Where 'application' is a WSGI application
```

####TODO
* Response to client. The current iteration just prints the response body to
  the console for now.
