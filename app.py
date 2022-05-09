from flask import Flask , render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime
#(id_encuesta, nombre, descripcion, estado, fecha_inicio, fecha_fin , id_encuestador)



class Poll:

    _code=-1
    _title="Encuesta sin Título"
    _description="--?--"
    _state="Por realizar"
    _id_encuestador=0
    _question=0
    def __init__ (self):
        self._state =-1
        self._state = "Por Realizar"
    def addCode(self,code):
        self._code=code

    def addQuestion(self,question):
        self._question=question

    def addTitle(self,title):
        self._title = title
    
    def addDescription(self,description):
        self._description = description
    
    def setState(self,state):
        self._state = state
    def getQuestion(self):
        return self._question

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
lastPoll=Poll()







@app.route("/")
def home():#----> pagina home
    return render_template('index.html')


@app.route("/encuestas")
def encuestas():#----> pagina

    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.estado='Por realizar'")
    
    Ready = cur1.fetchall()

    #print(Ready)
    
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado, E.fecha_inicio,E.fecha_fin,E.preguntas FROM Encuestas as E WHERE E.estado='Abierta'")
    Open = cur2.fetchall()

    cur3 = mysql.connection.cursor()
    cur3.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado, E.fecha_inicio,E.fecha_fin,E.preguntas FROM Encuestas as E WHERE E.estado='Cerrada'" )
    Closed = cur3.fetchall()
    
    
    
    
    return render_template("encuestas.html",
        pollsReady=Ready,
        pollsOpen=Open,
        pollsClosed=Closed)

@app.route("/nueva_encuesta")
def nueva_encuesta():

    cur = mysql.connection.cursor()
    title="nueva encuesta"
    des="sin descripción"
    cur.execute("INSERT INTO Encuestas (nombre, descripcion,estado, preguntas) VALUES (%s,%s,'Por realizar',0)",(title,des))
    mysql.connection.commit()
    cur.execute("SELECT LAST_INSERT_ID()")
    code = cur.fetchall()
    
    for row in code:
        lastPoll.addCode(row[0])
    
    return redirect(url_for('nueva_encuesta_code', code = lastPoll.getCode()))

@app.route("/crear_pregunta", methods=['POST'])
def crear_pregunta():
    code=lastPoll.getCode()
    lastPoll.addQuestion(lastPoll.getQuestion()+1)
    enunciado=request.form['enunciado']
    
    print(enunciado)
    
    #query="INSERT INTO Preguntas (id_encuesta,enunciado) VALUES ("+str(code)+","+enunciado+")"
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Preguntas (id_encuesta,enunciado) VALUES (%s,%s)",(code,enunciado))
    mysql.connection.commit()

    query="UPDATE Encuestas SET preguntas="+str(lastPoll.getQuestion())+" WHERE id_encuesta ="+str(code)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
   
    return redirect(url_for('nueva_encuesta_code', code = lastPoll.getCode()))

@app.route("/nueva_encuesta/<code>")
def nueva_encuesta_code(code):

    return render_template("nueva_encuesta.html")


@app.route("/crear_encuesta", methods=['POST'])
def crear_encuesta():
    
    if request.method =='POST':
        code=lastPoll.getCode()
        title=request.form['title']
        des=request.form['description']
        print("Ingresar en base de datos"+ str(code) + str(title)+" y "+str(des)+".")
        
        """
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Encuestas (nombre, descripcion,estado) VALUES (%s,%s,'Por realizar')",(title,des))
        mysql.connection.commit()
        """
        
        query="UPDATE Encuestas SET nombre='"+str(title)+"',descripcion='"+str(des)+"' WHERE id_encuesta ="+str(code)
        print(query)
        
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        
        newpoll=Poll()
        newpoll.addCode(code)
        newpoll.addTitle(title)
        newpoll.addDescription(des)
        polls.addPoll(newpoll)
        
    return redirect(url_for('encuestas'))





"""
@app.route("/crear_encuesta", methods=['POST'])
def crear_encuesta():
    
    if request.method =='POST':

        title=request.form['title']
        des=request.form['description']
        print("Ingresar en base de datos "+title+" y "+ des+".")
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Encuestas (nombre, descripcion,estado) VALUES (%s,%s,'Por realizar')",(title,des))
        mysql.connection.commit()
        
        newpoll=Poll(polls.getCount()+1)
        newpoll.addTitle(title)
        newpoll.addDescription(des)
        polls.addPoll(newpoll)

    return redirect(url_for('encuestas'))


"""
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


@app.route('/encuestados/<name>')
def estadoEncuestados(name):
    
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
@app.route("/sigin")
def sigin():
    return render_template("sigin.html")

@app.route('/eliminar_encuesta/<num>')
def eliminar_encuesta(num):
   
    query='DELETE FROM Encuestas WHERE id_encuesta ='+str(num)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    return redirect(url_for('encuestas'))

@app.route('/enviar_encuesta/<num>')
def enviar_encuesta(num):
   
    query="UPDATE Encuestas SET estado='Abierta' WHERE id_encuesta ="+str(num)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    return redirect(url_for('encuestas'))
@app.route('/cerrar_encuesta/<num>')
def cerrar_encuesta(num):
   
    query="UPDATE Encuestas SET estado='Cerrada' WHERE id_encuesta ="+str(num)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    return redirect(url_for('encuestas'))

