# coding: utf-8
import tornado.web, tornado.ioloop
import motor


class NewMessageHandler(tornado.web.RequestHandler):

    def get(self):
        self.write("""
            <form method='post'>
                <input type='text' name='msg'/>
                <input type='submit'/>
            </form>
        """)

    @tornado.web.asynchronous
    def post(self):
        msg = self.get_argument('msg')

        self.settings['db'].messages.insert(
            {'msg': msg},
            callback=self._on_message
        )

    def _on_message(self, result, error):
        if error:
            raise tornado.web.HTTPError(500, error)
        else:
            self.redirect('/')


class MessageHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        self.write('<a href="/compose">Compose a message</a><br />')
        self.write('<ul>')
        db = self.settings['db']
        db.messages.find().sort([('_id', -1)]).each(self._got_message)

    def _got_message(self, message, error):
        if error:
            raise tornado.web.HTTPError(500, error)
        elif message:
            self.write('<li>{0}</li>'.format(message['msg']))
        else:
            self.write('</ul>')
            self.finish()

db = motor.MotorClient().test

application = tornado.web.Application(
    [
        (r'/compose', NewMessageHandler),
        (r'/', MessageHandler)
    ],
    db=db
)

print 'Listening on http://localhost:8888'
application.listen(8888)
tornado.ioloop.IOLoop.instance().start()
