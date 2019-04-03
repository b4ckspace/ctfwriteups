Gallery
=======

Task description
----------------

> http://gallery.q.2019.volgactf.ru

Solution
--------

Visiting the [Gallery](http://gallery.q.2019.volgactf.ru/) results in a login
form. There is no registration. There are links for four galleries: 2018, 2017,
2016 and 2015, linked to `/2018`, `/2017` and so on. They require login, but
still load the `js/main.js` which does an XHR request to some API at
`/api/images?year=2018`. This API returns a “403 Forbidden” page if you are
not logged in. However, there are two ways to bypass this: The server runs
nginx which is misconfigured. It protects `/api`, however, it does not protect
`//api`, so requesting `//api/images?year=2018` results in an unprotected API.
In addition, there is a NodeJS server (with the Express framework) running on
port 4000, which is proxied by the beforementioned nginx. So alternatively,
you can access the unprotected API at `http://gallery.q.2019.volgactf.ru:4000/api`.
The images API endpoint returns a list of files as JSON list: `["2.jpg",
"3.jpg", "5.jpg","6.jpg","4.jpg","1.jpg"]`. In the following, we refer to
`/api` as the unprotected endpoint, for whatever way is used to bypass the
protection.

Looking at the `js/main.js`, we see that there is another endpoint, namely
`/api/image?year=${year}&img=${img}`. This endpoint serves the image files.
So you can view nice pictures from VolgaCTF events using for example
`/api/images?year=2018&img=1.jpg`. However, the pictures include no relevant
information (unless you want to do some lockpicking :-)).

Digging further, we find a path traversal vulnerability in both of these
endpoints. The `images` endpoint can be used to show the content of arbitrary
directories. The `image` endpoint turns out to be useless for an attack, we
will elaborate on that later.

So using the `images` endpoint like `/api/images?year=2018` will result in
the directory `/var/www/apps/volga_gallery/storage/app/{year}/img/` to be
listed. We can chop off the `/img/` part by using a null byte, i.e., visiting
`/api/images?year=../%00` will result in `/var/www/apps/volga_gallery/storage`
to be listed. Using `year=../../../../%00` we will find a file named `flag`.

At first sight, we might use the `image` endpoint to retrieve this file, by
requesting `/api/image?year=../../../../%00&img=flag`. So, this endpoint will
constructs the path in the following way:
`/var/www/apps/volga\_gallery/storage/app/{year}/img/{img}`
However, this path is passed to the PHP function `file_exists`, which bails
if you pass it a null byte (“file_exists() expects parameter 1 to be a valid
path, string given”). This exception is rendered nicely by a Laravel exception
page, so you see more information (like the full path mentioned before).
Unfortunately, there is no additional relevant information.

Moreover, any slashes (including forward and backward slashes) are removed
from the `img` parameter, so `api/image?year=../../../../&img=../flag` (which
would remove the `/img/` part added) does not work. Also other path traversal
tricks (double encoding, UTF-16 encoding, truncation ...) do not work.

Looking again, we find another file of interest when requesting
`/api/images?year=../../../volga_adminpanel/sessions%00`:
`euzb7bMKx-5F29b2xNobGTDoWXmVFlEM.json` which probably contains a valid
session we could steal. Again, there is no way to read this file directly.

Looking for the cookie name the Express framework (NodeJS) resulted in
`connect.sid`. So we set a cookie `connect.sid` with the value of
`euzb7bMKx-5F29b2xNobGTDoWXmVFlEM`. Turns out not to work :-(

Reading the source code of `express-session` (the session framework of
Express) shows that they actually sign the cookies with a secret key. A few
more directory traversal requests we stumbled upon the configuration file
named config.js via `/api/images?year=../../../volga_auth/js%00`. We can
download this file directly via HTTP at `/js/config.js`. Furthermore, there
are two additional files of interest: `/js/index.js` and `js/auth.js`.

The configuration file looks like:

    const config = {
      apiPrefix: '/api',
      server: {
        port: 4000
      },
      proxy: {
        target: 'http://localhost:5000',
        autoRewrite: true
      },
      session: {
        name: 'SESSION',
        saveUninitialized: false,
        secret: ';GmU1FSlVETF/vzEaBHP',
        rolling: true,
        resave: false
      },
      whitelistPaths: [
        '/api/login', '/api/logout'
      ]
    }

So we have the secret, yay! And the cookie is renamed from the default
`connect.sid` to `SESSION`. So we thought “Nur noch ein kleiner Schnitt durchs
Kuchenblech” (German-speaking people: Search “Kuchenblechmafia” on YouTube,
others: It rougly translates to “basically solved, just a trivial step left”).

The easiest way to generate a signed cookie is now just to change the config
file the following way and run the server to receive the cookie:

    session: {
      genid: function() { return "euzb7bMKx-5F29b2xNobGTDoWXmVFlEM" },
      name: 'SESSION',
      saveUninitialized: true,
    // ...

So we got the cookie value (`s%3ACLPlzjlR_Lpfk1S0xWpl5w333HuVYLM9.qygCVWau45L5jPSQyfO%2BfPLC22loSdoYs9knaOxf%2BKc`),
applied it to our browser and visit `/api/flag` (you can find that endpoint in
the `js/index.js` from before) and receive our flag. Did not work. WTF?
Checking everything again. Still does not work. Joy turns into frustration.
VolgaCTF Qualifier 2019 ended without us having that task solved. Good bye 300
points :-(

Turns out the path used for session is not the one were we found the session
file. Thanks to quality JS software (session-file-store), there is another
traversal vulnerability under the assumption that you can sign the session
cookie.

Editing `js/config.js` again:

    session: {
      genid: function() {
        return "../../../../../../../../../../../../../../var/www/apps/volga_adminpanel/sessions/euzb7bMKx-5F29b2xNobGTDoWXmVFlEM"
      },
      name: 'SESSION',
      saveUninitialized: true,
    // ...

Again, run the server, get the cookie, pass it on to `/api/flag`. Works. We
received the flag: `VolgaCTF{31c2ac53d4101a01264775328797d424}`. Thanks to
the organizers for keeping the service running for some time after the
competition! Finally seeing the flag made us happy again :-)

