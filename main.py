#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
from google.cloud import storage
import random
import string
from google.appengine.ext import ndb

class Photo(ndb.Model):
    created_time = ndb.DateTimeProperty(auto_now_add=True)
    photo_url = ndb.StringProperty()


def generate_random_string(n=10):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


class MainHandler(webapp2.RequestHandler):
    def post(self):
        # get the file
        file = self.request.POST['photo']

        # save it to gcs
        client = storage.Client()
        bucket = client.get_bucket('kl-public-photo-album.appspot.com')
        blob = bucket.blob(generate_random_string(100))
        blob.upload_from_string(file.file.read())

        # get a public url
        acl = blob.acl
        acl.all().grant_read()
        acl.save()

        # save that to datastore
        public_url = blob.public_url
        photo = Photo()
        photo.photo_url = public_url
        photo.put()

        # redirect to homepage
        self.redirect('/')

    def get(self):
        # query all the photos in datastore
        photos = Photo.query().fetch()

        # render them on this page.... \o/

        content = """

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="icon" href="../../favicon.ico">

    <title>KL Public Photo Album</title>

    <!-- Bootstrap core CSS -->
    <link href="http://getbootstrap.com/dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <link href="../../assets/css/ie10-viewport-bug-workaround.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="http://getbootstrap.com/examples/jumbotron-narrow/jumbotron-narrow.css" rel="stylesheet">

    <!-- Just for debugging purposes. Don't actually copy these 2 lines! -->
    <!--[if lt IE 9]><script src="../../assets/js/ie8-responsive-file-warning.js"></script><![endif]-->
    <script src="../../assets/js/ie-emulation-modes-warning.js"></script>

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>

  <body>

    <div class="container">
      <div class="header clearfix">
        <nav>
          <ul class="nav nav-pills pull-right">
            <li role="presentation" class="active"><a href="#">Home</a></li>
          </ul>
        </nav>
        <h3 class="text-muted">KL Public Photo Album</h3>
      </div>

      <div class="jumbotron">
        <h1>KL Public Photo Album</h1>
        <p class="lead">Upload all your photos!</p>
        <form method="POST" enctype="multipart/form-data">
        	<input class="form-control" type="file" name="photo" /><br />
        	<button type="submit" class="btn btn-primary">Upload!</button>
        </form>
      </div>

      <div class="row marketing">
        <div class="col-lg-12">"""

        for photo in photos:
            content += '<img src="' + photo.photo_url + '" style="width:100%;" />'
    
        content += """</div>
      </div>

      <footer class="footer">
        <p>&copy; 2017 KL Public Photo Album</p>
      </footer>

    </div> <!-- /container -->


    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="../../assets/js/ie10-viewport-bug-workaround.js"></script>
  </body>
</html>
"""
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)








