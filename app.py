from flask import Flask , render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from datetime import datetime

#Encuesta: Guarda los datos de las encuestas que se esten manipulando.

class Poll:

    _code=-1 #Identificador de la encuesta creada.
    _title="Encuesta sin Título" #Título de la encuesta creada.
    _description="--?--" #Descripción de la encuesta creada.
    _state="Por realizar" #Estado de la encuesta 'Por realizar','Abierta','Cerrada'.
    _id_encuestador=0 #Id del encuestador que crea la encuesta. (no implemenado)
    _question=0 #Número de encuestas.
    
    def __init__ (self): #Constructor de la clase Poll
        self._state =-1
        self._state = "Por Realizar"
    
    def setCode(self,code):#seter del atributo code
        self._code=code

    def setQuestion(self,question): #seter del atributo question
        self._question=question

    def setTitle(self,title): #seter del atributo title
        self._title = title
    
    def setDescription(self,description):#seter del atributo description
        self._description = description
    
    def setState(self,state):#seter del atributo state
        self._state = state
    
    def getQuestion(self): #geter del atributo question
        return self._question

    def getTitle(self): #geter del atributo title
        return self._title
    
    def getCode(self): #geter del atributo code
        return self._code
    
    def getDescription(self):#geter del atributo description
        return self._description
   
    def getState(self):#geter del atributo state
        return self._state    

"""
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
"""    






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
#polls=SystemPoll()

#Variables Globales
lastPoll=Poll()# hace referencia a la ultima encuesta creada



#-------------------------------

@app.route("/")
def home():#----> pagina home
    return render_template('index.html')

#-------------------------------
#-------------------------------

#Operaciones con Encuestas

#-------------------------------
#-------------------------------

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

#-------------------------------

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
        lastPoll.setCode(row[0])
        
    
    return redirect(url_for('nueva_encuesta_code', code = lastPoll.getCode()))

#-------------------------------

@app.route("/crear_pregunta", methods=['POST'])
def crear_pregunta():

    code=lastPoll.getCode()
    lastPoll.setQuestion(lastPoll.getQuestion()+1)
    enunciado=request.form['enunciado']
    
    #print(enunciado)
    
    #query="INSERT INTO Preguntas (id_encuesta,enunciado) VALUES ("+str(code)+","+enunciado+")"
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Preguntas (id_encuesta,enunciado) VALUES (%s,%s)",(code,enunciado))
    mysql.connection.commit()

    query="UPDATE Encuestas SET preguntas="+str(lastPoll.getQuestion())+" WHERE id_encuesta ="+str(code)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
   
    return redirect(url_for('nueva_encuesta_code', code = lastPoll.getCode()))

#-------------------------------

@app.route("/nueva_encuesta/<code>")
def nueva_encuesta_code(code):
    """
    cur = mysql.connection.cursor()
    cur.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.id_encuesta=%s",[code])
    pollv = cur.fetchall()
    

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO Preguntas (id_encuesta,enunciado) VALUES (%s,'nueva pregunta')",(code))
    mysql.connection.commit()



    cur = mysql.connection.cursor()
    cur.execute("SELECT P.id_encuesta,P.enunciado FROM Preguntas as P WHERE P.id_encuesta=%s",[code])
    questions = cur.fetchall()
    """
    
    return render_template("nueva_encuesta.html"
    ,code=code)

    #,pollv=pollv
    #,questions=questions

#-------------------------------
@app.route("/cancelar_nueva_encuesta")
def cancelar_nueva_encuesta():
    query='DELETE FROM Encuestas WHERE id_encuesta ='+str(lastPoll.getCode())
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()

    return redirect(url_for('encuestas'))

@app.route("/crear_encuesta", methods=['POST'])
def crear_encuesta():
    
    if request.method =='POST':
        
        code=lastPoll.getCode()
        title=request.form['title']
        des=request.form['description']
        print("Ingresar en base de datos"+ str(code) + str(title)+" y "+str(des)+".")
        
        query="UPDATE Encuestas SET nombre='"+str(title)+"',descripcion='"+str(des)+"' WHERE id_encuesta ="+str(code)
        print(query)
        
        cur = mysql.connection.cursor()
        cur.execute(query)
        mysql.connection.commit()
        """
        newpoll=Poll()
        newpoll.setCode(code)
        newpoll.setTitle(title)
        newpoll.setDescription(des)
        polls.addPoll(newpoll)"""
        
    return redirect(url_for('encuestas'))

#-------------------------------
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
        newpoll.setTitle(title)
        newpoll.setDescription(des)
        polls.addPoll(newpoll)

    return redirect(url_for('encuestas'))

"""
#-------------------------------

@app.route("/editar_encuesta/<num>") #, methods=['POST']
def editar_encuesta(num):
    cur1 = mysql.connection.cursor()
    cur1.execute("SELECT E.id_encuesta,E.nombre,E.descripcion, E.estado,E.preguntas FROM Encuestas as E WHERE E.id_encuesta=%s",[num])

    pollv = cur1.fetchall()
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT P.enunciado FROM Preguntas as P WHERE P.id_encuesta=%s",[num])
    questionv=cur2.fetchall()
    return render_template("editar_encuesta.html"
    ,pollv=pollv
    ,questionv=questionv)

#-------------------------------

@app.route('/eliminar_encuesta/<num>')
def eliminar_encuesta(num):
    
    query='DELETE FROM Preguntas WHERE id_encuesta ='+str(num)
    cur = mysql.connection.cursor()
    cur.execute(query)

    query='DELETE FROM Encuestas WHERE id_encuesta ='+str(num)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()

    return redirect(url_for('encuestas'))

#-------------------------------

@app.route('/enviar_encuesta/<num>')
def enviar_encuesta(num):
   
    query="UPDATE Encuestas SET estado='Abierta' WHERE id_encuesta ="+str(num)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    
    return redirect(url_for('encuestas'))

#-------------------------------

@app.route('/cerrar_encuesta/<num>')
def cerrar_encuesta(num):
   
    query="UPDATE Encuestas SET estado='Cerrada' WHERE id_encuesta ="+str(num)
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    
    return redirect(url_for('encuestas'))

#-------------------------------
#-------------------------------

# Operaciones con Encuestados

#-------------------------------
#-------------------------------

@app.route('/encuestados')
def encuestados():
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Encuestados')
    data = cur.fetchall()
    
    return render_template("encuestados.html", encuestados = data)#'encuestados'

#-------------------------------

@app.route('/encuestados/<name>')
def estadoEncuestados(name):
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Encuestados')
    data = cur.fetchall()
    return render_template("encuestados.html", encuestados = data)#'encuestados'

#-------------------------------

@app.route('/nuevo_enc', methods=['POST'])
def nuevo_enc():
    
    if request.method == 'POST':

        correo = request.form['correo']
        nombre = request.form['nombre']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO Encuestados (correo,nombre) VALUES (%s,%s)',(correo,nombre))
        mysql.connection.commit()

    return redirect(url_for('encuestados'))

#-------------------------------
    
@app.route('/editar_encuestado/<email>')
def get_encuestado(email):

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Encuestados WHERE correo = %s', [email])
    data = cur.fetchall()
    return render_template('e-encuestado.html', encuestado = data[0])

#-------------------------------

@app.route('/eliminar_encuestado/<email>')
def elim_encuestado(email):

    cur = mysql.connection.cursor()
    
    cur.execute('DELETE FROM Encuestados WHERE correo = %s',[email])
    mysql.connection.commit()
    
    return redirect(url_for('encuestados'))

#-------------------------------
#-------------------------------

#Login

#-------------------------------
#-------------------------------

@app.route("/login")
def login():
    return render_template("login.html")

#-------------------------------

@app.route("/sigin")
def sigin():
    return render_template("sigin.html")

#-------------------------------
#-------------------------------


#Operaciónes con encuestas


#-------------------------------
