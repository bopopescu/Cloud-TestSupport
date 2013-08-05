import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
import tornado.ioloop
import tornado.web
import tornado.database
import tornado.httpserver
import os
from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", Main),
            (r"/login", Login),
            (r"/logout", Logout),
            (r"/index", Index),
            (r"/home", Home),
            (r"/delete", DeleteRecord),
            (r"/success", Success),
            (r"/results", DBHandler),
            (r"/(style\.css)",tornado.web.StaticFileHandler, {"path": "./css/"}),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/login",
            static_path= os.path.join(os.path.dirname(__file__), "static"),
            debug="True",
        )
        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        self.db = tornado.database.Connection(
            host="cloudtest.c3ft09b20edu.us-east-1.rds.amazonaws.com", database="cloudtest",
            user="cloudtest", password="cloudtest")

class DatabaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

class DBHandler(DatabaseHandler):
    def get(self):
        rows = self.db.query("select * from studentmarkdetails")
        self.db.close()
        self.render('results.html',rows=rows)

class Index(DatabaseHandler):
    def get(self):
        rows = self.db.query("select * from studentmarkdetails")
        self.db.close()
        self.render('index.html',rows=rows)

class DeleteRecord(DatabaseHandler):
    def get(self):
        print 'get'

    def post(self):
        rollno=int(self.get_argument("Delete_RollNo"))
        db_query='DELETE FROM studentmarkdetails WHERE rollno=%s'%(rollno)
        lastrow=self.db.execute(db_query)
        self.redirect("/results")

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

class Main(BaseHandler):
    def get(self):
        if not self.current_user:
            self.redirect("/login")
            return
        name = tornado.escape.xhtml_escape(self.current_user)
        if name == 'priya':
            self.redirect("/index")
        else:
            self.clear_cookie("user")
            self.redirect(u"/login")

class Home(tornado.web.RequestHandler):
        def get(self):
            if self.current_user is not None:
                self.render('home.html')
            else:
                self.redirect("/login")

class Success(DatabaseHandler):
        def get(self):
            if self.current_user is not None:
                fullname=self.get_argument("fullname")
            else:
                self.render('login.html')

        def post(self):
            firstname = self.get_argument("firstname")
            lastname = self.get_argument("lastname")
            rollno=int(self.get_argument("rollno"))
            Marks1=int(self.get_argument("Marks1"))
            Marks2=int(self.get_argument("Marks2"))
            Marks3=int(self.get_argument("Marks3"))
            Marks4=int(self.get_argument("Marks4"))
            total=Marks1+Marks2+Marks3+Marks4
            avg=total/4
            if avg>60 and avg<80:
                grade="B"
            if avg>80 and avg<100:
                grade="A"
            if avg<50:
                grade="C"
            avg = str(avg)
            total=str(total)
            rollno=str(rollno)
            Marks1=str(Marks1)
            Marks2=str(Marks2)
            Marks3=str(Marks3)
            Marks4=str(Marks4)
            self.db.execute("INSERT INTO studentmarkdetails (firstname,lastname,rollno,physics,chemistry,biology,maths,total,average,grade) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",firstname,lastname,rollno,Marks1,Marks2,Marks3,Marks4,total,avg,grade)
            self.redirect("/index")
#            self.render('success.html',firstname=firstname,lastname=lastname,rollno=rollno,Marks1=str(Marks1),Marks2=str(Marks2),Marks3=str(Marks3),Marks4=str(Marks4),total=str(total),avg=str(avg),grade=grade)
            self.db.close()

class Login(BaseHandler):
        def get(self):
            if self.current_user is not None:
                self.render('home.html')
            else:
                self.render('login.html')

        def post(self):
            self.set_secure_cookie("user", self.get_argument("username"))
            self.redirect("/")

class Logout(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/login")

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
