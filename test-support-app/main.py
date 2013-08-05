import os,sys,time
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from urllib import urlretrieve
import tornado.ioloop
import tornado.web
import tornado.httpserver
cwd = os.getcwd()
import logging
from ec2tests import run_instance

from tornado.options import define, options

define("port", default=8080, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", Main),
            (r"/login", Login),
            (r"/logout", Logout),
            (r"/dashboard", Dashboard),
            (r"/test", Runtests),
            (r"/results", Results),
            (r"/frame", FrameHandler),
        ]
        settings = dict(
            cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/login",
            static_path= os.path.join(os.path.dirname(__file__), "static"),
            debug="True",
        )
        tornado.web.Application.__init__(self, handlers, **settings)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class Main(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        else:
            self.render('home.html')

class Logout(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/login")

class Login(BaseHandler):
        def get(self):
            if self.current_user is not None:
                self.render('home.html')
            else:
                self.render('index.html')

        def post(self):
            self.redirect("/dashboard")

class FrameHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('TestReport.html')

class Dashboard(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        else:
            self.render('home.html')

    def post(self):
        self.set_secure_cookie("user", self.get_argument("username"))
        self.render('home.html')

class Results(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        else:
            self.render('Results.html')

    def post(self):
        self.render('Results.html')

class Runtests(tornado.web.RequestHandler):
    def get(self):
        self.write("Running Test cases")

    def post(self):
        testcase_file=self.get_argument("fileurl")
        browser = self.get_argument("browser")
        if browser == 'htmlunit':
            print 'Linux instance'
            env = 'Ubuntu12.04'
        else:
            print 'Windows instance'
            env = 'WinServer2k8'
        emailids = self.get_argument("emailid")
        logging.info('Launching Instance %s %s %s %s'%(testcase_file,browser,env,emailids))
        print testcase_file,browser,env,emailids
        print 'Launching instances.............'
        inst = run_instance(testcase_file,browser,env,'C:\stest-support\stest-results',emailids)
        print 'Id',inst
        logging.info('Launching Instance Id %s '%(inst))
        self.redirect("/results")

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
