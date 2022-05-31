
from tkinter.filedialog import Open
from xml.dom.minidom import ReadOnlySequentialNamedNodeMap
from flask import Flask , render_template, request, redirect, url_for
from flask_mysqldb import MySQL
#(id_encuesta, nombre, descripcion, estado, fecha_inicio, fecha_fin , id_encuestador)



class Poll:

    _code=-1
    _title="Encuesta sin Título"
    _description="--?--"
    _state="Por realizar"
    _id_encuestador=0
    def __init__ (self,code):
        self._code = code
        self._state = "Por Realizar"
    
    def addTitle(self,title):
        self._title = title
    
    def addDescription(self,description):
        self._description = description
    
    def setState(self,state):
        self._state = state
    
    def getTitle(self):
        return self._title
    
    def getCode(self):
        return self._code
    
    def getDescription(self):
        return self._description
   
    def getState(self):
        return self._state    

class SystemPoll:
    
    def __init__ (self):
        self.pollsReady  = []
        self.pollsOpen   = []
        self.pollsClosed = []
    def addPoll(self,poll):

        if poll.getState() == "Por realizar":
            self.pollsReady.append(poll)
        elif poll.getState() == "Abierta":
            self.pollsOpen.append(poll)
        elif poll.getState() == "Cerrada":
            self.pollsClosed.append(poll)
        else:
            print("error estado no valido")
        
    def removePoll(self,code):
        
        for i in self.pollsReady:
            if i.getCode()== code:
               self.pollsReady.remove(i)

        for i in self.pollsOpen:
            if i.getCode()== code:
               self.pollsOpen.remove(i)

        for i in self.pollsClosed:
            if i.getCode()== code:
               self.pollsClosed.remove(i) 
    
    def getPoll(self,code):
        
        for i in self.pollsReady:
            if i.getCode()== code:
               return i

        for i in self.pollsOpen:
            if i.getCode()== code:
               return i

        for i in self.pollsClosed:
            if i.getCode()== code:
               return i
       
    
    def getAll(self):

        return self.polls
    
    def getState(self,state):

        if state == "Por realizar":
            return self.pollsReady
        elif state == "Abierta":
            return self.pollsOpen
        elif state == "Cerrada":
            return self.pollsClosed
        else:
            print("error estado no valido")

    def getCount(self):
        return len(self.pollsClosed) + len(self.pollsOpen) + len(self.pollsReady)
    






app = Flask(__name__)#-------> Main de la aplicación


#mysql connection
app.config['MYSQL_HOST']='103.195.100.230'
app.config['MYSQL_USER']='jookeezc_alejandro'
app.config['MYSQL_PASSWORD']='is2_gonzal0'
app.config['MYSQL_DB']='jookeezc_encuesta'
mysql = MySQL(app)

#settings
app.secret_key = "mysecretkey"




# Se inicializa el almacen de encuestas
polls=SystemPoll()

poll1=Poll(1)#-------> Encuesta de prueba
poll1.addTitle("Segunda Encuesta presidencial 2026")
poll1.addDescription("resultados de vocaciones año 2026")
poll1.setState("Por realizar")
polls.addPoll(poll1)




poll2=Poll(2)#-------> Encuesta de prueba
poll2.addTitle("Primera Encuesta presidencial 2026")
poll2.addDescription("resultados de vocaciones año 2026")
poll2.setState("Abierta")
polls.addPoll(poll2)





poll3=Poll(3)#-------> Encuesta de prueba
poll3.addTitle("Encuesta presidencial 2021")
poll3.addDescription("resultados de vocaciones año 2026")
poll3.setState("Cerrada")
polls.addPoll(poll3)





#-------> Aca deberia estar la query de la base de datos
#SELECT E.id_encuesta,E.nombre,E.descripcion FROM Encuestas as E
#ncursor = mysql.connection.cursor()
#ncursor.execute('SELECT * FROM Encuestados WHERE correo = %s', [email])
#data = cur.fetchall()



@app.route("/")
def home():#----> pagina home
    return render_template('index.html')


@app.route("/encuestas")
def encuestas():#----> pagina

    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado FROM Encuestas as E WHERE E.estado='Por realizar'")
    Ready = cur1.fetchall()
    
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado FROM Encuestas as E WHERE E.estado='Abierta'")
    Open = cur2.fetchall()

    cur3 = mysql.connection.cursor()
    cur3.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado FROM Encuestas as E WHERE E.estado='Cerrada'" )
    Closed = cur3.fetchall()
    
    
    
    
    return render_template("encuestas.html",
        pollsReady=Ready,
        pollsOpen=Open,
        pollsClosed=Closed)

@app.route("/nueva_encuesta")
def nueva_encuesta():
    return render_template("nueva_encuesta.html")

@app.route("/crear_encuesta", methods=['POST'])
def crear_encuesta():
    
    if request.method =='POST':

        title=request.form['title']
        des=request.form['description']
        print("Ingresar en base de datos "+title+" y "+ des+".")
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Encuestas (nombre, descripcion) VALUES (%s,%s)",(title,des))
        mysql.connection.commit()
        
        newpoll=Poll(polls.getCount()+1)
        newpoll.addTitle(title)
        newpoll.addDescription(des)
        polls.addPoll(newpoll)

    return redirect(url_for('encuestas'))

@app.route("/editar_encuesta", methods=['POST'])
def editar_encuesta():
    
    if request.method =='POST':
        code=request.form['code']
        #title=request.form['title']
        #des=request.form['description']
        newpoll=polls.getPollcode(code)
        print(newpoll)
    return render_template("editar_encuesta.html")

@app.route('/encuestados')
def encuestados():
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Encuestados')
    data = cur.fetchall()
    return render_template("encuestados.html", encuestados = data)#'encuestados'

@app.route('/nuevo_enc', methods=['POST'])
def nuevo_enc():
    
    if request.method == 'POST':

        correo = request.form['correo']
        nombre = request.form['nombre']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO Encuestados (correo,nombre) VALUES (%s,%s)',(correo,nombre))
        mysql.connection.commit()

    return redirect(url_for('encuestados'))

    
@app.route('/editar_encuestado/<email>')
def get_encuestado(email):

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Encuestados WHERE correo = %s', [email])
    data = cur.fetchall()
    return render_template('e-encuestado.html', encuestado = data[0])

@app.route('/eliminar_encuestado/<email>')
def elim_encuestado(email):

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Encuestados WHERE correo = %s',[email])
    mysql.connection.commit()
    return redirect(url_for('encuestados'))

@app.route("/login")
def login():
      
    return render_template("login.html")

@app.route("/logear", methods = ['GET','POST'])
def logear():
    if request.method =='POST':
        email = request.form['correo']
        password = request.form['contraseña']
        #print(email)
        #print(password)
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM Encuestadores WHERE correo = %s', (email,))
        user = cur.fetchone()
        cur.close()
        #print(user[2])
        if user is not None:
            if password == user[2]:
                return "bienvenido jajitas"
            else: 
                return "correo y/o contraseña no valido"
        else:
            return "Correo no registrado"        
        #cur.close()       
        #if len(user)>0:
        #return "Bienvenido :)"
        #else:
        #    return "Error, Correo y/o contraseña no valida"


    return redirect(url_for('login'))    

@app.route("/sigin")
def sigin():
  
    return render_template("sigin.html")
          

    

@app.route('/eliminar_encuesta/<num>')
def eliminar_encuesta(num):

    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Encuestas WHERE id_encuesta = %s',[num])
    mysql.connection.commit()
    return redirect(url_for('encuestas'))
