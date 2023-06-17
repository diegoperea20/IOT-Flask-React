from flask import Flask , request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

#Para usar fronted
from flask_cors import CORS
#------------------------------

#Para autentificar
from flask_bcrypt import check_password_hash, generate_password_hash
import jwt
import datetime
#------------------------------

app = Flask(__name__)

#Para usar fronted
CORS(app)
#---------

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:mypassword@localhost:3306/flaskmysql'
#app.config['SQLALCHEMY_DATABASE_URI'] =  'postgresql://postgres:mypassword@localhost:5432/flaskpostgresql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db=SQLAlchemy(app)


ma= Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    user= db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))

    def __init__(self, email, user, password):
        self.email = email
        self.user = user
        self.password = password
        
#Allnodes
class Allnode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user= db.Column(db.String(200))
    code = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(200))

    def __init__(self, user, code, name):
        self.user = user
        self.code = code
        self.name = name

# Define la función para crear el esquema dinámicamente
def create_table_schema(code):
    class TableSchema(ma.Schema):
        class Meta:
            fields = ('id', 'temperature', 'humidity')

    table_schema = TableSchema()
    tables_schema = TableSchema(many=True)

    globals()[f'table_{code}_schema'] = table_schema
    globals()[f'tables_{code}_schema'] = tables_schema


#----------------------------
with app.app_context():
    db.create_all()


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'email', 'user', 'password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

#Allnode
class AllnodeSchema(ma.Schema):
    class Meta:
        fields = ('id','user', 'code', 'name')


allnode_schema = AllnodeSchema()
allnodes_schema = AllnodeSchema(many=True)



@app.route('/loginup', methods=['POST'])
def create_user():
    email=request.json['email']
    user=request.json['user']
    password = generate_password_hash(request.json['password'])
    existing_user = User.query.filter_by(user=user).first()
    if existing_user:
        return jsonify({'error': 'User already exists'}), 409
    new_user = User(email, user, password)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

@app.route('/loginup', methods=['GET'])
def get_users():
    all_users=User.query.all()
    result=users_schema.dump(all_users)
    return jsonify(result)                    

@app.route('/loginup/<id>', methods=['GET'])
def get_user(id):
    user=User.query.get(id)
    return user_schema.jsonify(user) 

@app.route('/loginup/<id>', methods=['PUT'])
def update_user(id):
    user_to_update = User.query.get(id)  # Renombrar la variable aquí
    
    email = request.json['email']
    new_user = request.json['user']
    password = generate_password_hash(request.json['password'])

    user_to_update.email = email
    user_to_update.user = new_user  # Renombrar la variable aquí
    user_to_update.password = password
    
    db.session.commit()
    return user_schema.jsonify(user_to_update)



@app.route('/loginup/<id>', methods=['DELETE'])
def delete_user(id):
    user=User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    return user_schema.jsonify(user)


#Login IN (Iniciar sesion)
@app.route('/', methods=['POST'])
def login():
    data = request.get_json()
    username = data['user']
    password = data['password']

    user = User.query.filter_by(user=username).first()
    if user and check_password_hash(user.password, password):
        # Las credenciales son válidas, puedes generar un token de autenticación aquí
        token = generate_token(user)  # Ejemplo: función para generar el token

        return jsonify({'token': token ,"user_id": user.id}), 200

    # Las credenciales son incorrectas
    return jsonify({'error': 'Credenciales inválidas'}), 401


def generate_token(user):
    # Definir las opciones y configuraciones del token
    token_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Token expira en 1 hora
    }
    secret_key = 'tuclavesecretadeltoken'  # Cambia esto a tu clave secreta real

    # Generar el token JWT utilizando PyJWT
    token = jwt.encode(token_payload, secret_key, algorithm='HS256')
    return token


#Allnode

@app.route('/allnode', methods=['POST'])
def create_allnode():
    user=request.json['user']
    code=request.json['code']
    name=request.json['name']
    code_same=Allnode.query.filter_by(code=code).first()
    if code_same:
        return jsonify({'error': 'code already exists'}), 409
    
    new_allnode = Allnode(user, code, name)
    db.session.add(new_allnode)
    db.session.commit()
    return allnode_schema.jsonify(new_allnode)


@app.route('/allnode/<user>', methods=['GET'])
def get_allnode_user(user):
    task=Allnode.query.filter_by(user=user).all()
    return allnodes_schema.jsonify(task) 


@app.route('/allnode/<id>', methods=['PUT'])
def put_allnode_user(id):
    allnode_to_update = Allnode.query.get(id)  # Renombrar la variable aquí
    name = request.json['name']
    allnode_to_update.name=name
    db.session.commit()
    return allnode_schema.jsonify(allnode_to_update)

@app.route('/allnode/<id>', methods=['DELETE'])
def delete_node_allnode(id):
    allnode=Allnode.query.get(id)
    db.session.delete(allnode)
    db.session.commit()
    return allnode_schema.jsonify(allnode)

#delete account 
@app.route('/allnodeaccount/<user>', methods=['DELETE'])
def delete_node_allnode_account(user):
    allnodes = Allnode.query.filter_by(user=user).all()

    for allnode in allnodes:
        db.session.delete(allnode)

    db.session.commit()

    return 'deleted successfully'



@app.route('/allnode/<id>/<user>', methods=['GET'])
def get_allnode_row(id,user):
    task=Allnode.query.filter_by(id=id ,user=user).all()
    return allnodes_schema.jsonify(task) 

#Table Code
@app.route('/tablecode', methods=['POST'])
def create_tablecode():
    try:
        code = request.json.get('code')
        if not code:
            return 'Code not provided', 400

        table_name = f'table_{code}'
        user_table = type(table_name, (db.Model,), {
            'id': db.Column(db.Integer, primary_key=True),
            'temperature': db.Column(db.String(200)),
            'humidity': db.Column(db.String(100))
        })

        create_table_schema(code)  # Llama a la función para crear el esquema dinámicamente

        db.create_all()
        return 'Code table created successfully', 201

    except Exception as e:
        return str(e), 500


from sqlalchemy import inspect

@app.route('/tablecode/<code>', methods=['POST'])
def post_tablecode(code):
    try:
        # Obtener los datos de temperatura y humedad de la solicitud JSON
        temperature = request.json.get('temperature')
        humidity = request.json.get('humidity')

        # Verificar si la tabla existe en la base de datos
        table_name = f'table_{code}'
        inspector = inspect(db.engine)
        if table_name not in inspector.get_table_names():
            return 'Table not found', 404

        # Crear una instancia de la clase de la tabla dinámica
        TableClass = type(table_name, (db.Model,), {})
        table_entry = TableClass(temperature=temperature, humidity=humidity)

        # Agregar la nueva entrada a la base de datos
        db.session.add(table_entry)
        db.session.commit()

        return 'Data added successfully', 201

    except Exception as e:
        return str(e), 500  # Devuelve el mensaje de error en caso de que ocurra una excepción

#-----------------------------------------------------------------------------------------
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

@app.route('/tablecode/<code>', methods=['DELETE'])
def delete_tablecode(code):
    try:
        # Verificar si la tabla existe en la base de datos
        table_name = f'table_{code}'
        inspector = inspect(db.engine)
        if not inspector.has_table(table_name):
            return 'Table not found', 404

        # Crear una conexión y una sesión
        engine = create_engine(db.engine.url)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Ejecutar una consulta SQL para eliminar la tabla
        query = text(f'DROP TABLE {table_name}')
        session.execute(query)
        session.commit()

        return 'Table deleted successfully', 200

    except Exception as e:
        return str(e), 500  # Devuelve el mensaje de error en caso de que ocurra una excepción




#-----------------------------------------------------------------------------------------

from sqlalchemy import inspect
from sqlalchemy import Table

@app.route('/tablecode/<code>', methods=['GET'])
def get_tablecode(code):
    try:
        table_name = f'table_{code}'  # Genera el nombre de la tabla a buscar
        inspector = inspect(db.engine)
        if not inspector.has_table(table_name):  # Verifica si la tabla existe en la base de datos
            return 'Table not found', 404

        # Reflect the tables from the database
        db.reflect()

        # Obtén la tabla dinámica a partir del nombre
        table = db.Model.metadata.tables[table_name]

        # Realiza la consulta a la tabla
        table_data = db.session.query(table).all()

        # Procesa los datos obtenidos y devuélvelos como respuesta
        data = []
        for row in table_data:
            data.append({
                'id': row.id,
                'temperature': row.temperature,
                'humidity': row.humidity
            })

        return jsonify(data), 200

    except Exception as e:
        return str(e), 500  # Devuelve el mensaje de error en caso de que ocurra una excepción



#delete tables in delete account
@app.route('/tablecodeall/<user>', methods=['DELETE'])
def delete_user_tablecodes(user):
    try:
        # Obtener todos los códigos asociados al usuario
        table_codes = []
        allnode_records = Allnode.query.filter_by(user=user).all()
        for record in allnode_records:
            table_codes.append(record.code)

        # Verificar y eliminar las tablas correspondientes
        engine = create_engine(db.engine.url)
        inspector = inspect(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        for code in table_codes:
            table_name = f'table_{code}'
            if inspector.has_table(table_name):
                query = text(f'DROP TABLE {table_name}')
                session.execute(query)

        session.commit()

        return 'Tables deleted successfully', 200

    except Exception as e:
        return str(e), 500  # Devuelve el mensaje de error en caso de que ocurra una excepción
   
    
   

if __name__ == '__main__':
    app.run(debug=True)

#Comands for use docker container mysql
#docker run --name mymysql -e MYSQL_ROOT_PASSWORD=mypassword -p 3306:3306 -d mysql:latest
#docker exec -it mymysql bash
#mysql -u root -p
#create database flaskmysql;



