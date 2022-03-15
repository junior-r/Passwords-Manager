import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime


connection = sqlite3.connect('Users.sqlite3')
cursor = connection.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username STRING UNIQUE, 
        correoE STRING UNIQUE,
        password STRING
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Passwords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username STRING,
    password STRING,
    website STRING,
    date DATETIME
    )
''')


def home():
    print('1, Crear Cuenta | 2, Iniciar Sesión')
    accion = input('¿Qué desea hacer?: ')
    if accion == '1':
        return sing_up()
    elif accion == '2':
        return login()
    else:
        print('Opción Inválida. Intenta de Nuevo!')
        home()


def sing_up():
    print('-------- Crear Cuenta --------\n')
    username = input('Ingrese su nombre de usuario: ')
    gmail = input('Ingrese su correo electrónico: ')
    master_password = input('Ingrese su contraseña maestra: ')
    print('')
    return validate_sing_up(username, gmail, master_password)


def validate_sing_up(username, gmail, master_password):
    if len(username) >= 3 and len(username) <= 30:
        if gmail.count('@') == 1:
            if master_password != '' and len(master_password) >= 8:
                return create_account(username, gmail, master_password)
            else:
                print('Contraseña Inválida. Intente de nuevo')
                return sing_up()
        else:
            print('Dirección de correo electrónico Inválida. Intente de nuevo')
            return sing_up()
    else:
        print('Nombre de Usuario Inválido. Intente de nuevo')
        return sing_up()


def create_account(username, gmail, master_password):
    master_password = generate_password_hash(master_password)
    user_data = [
        (username, gmail, master_password)
    ]
    sql = 'INSERT INTO Users VALUES(NULL, ?, ?, ?)'
    try:
        cursor.executemany(sql, user_data)
        print('Cuenta creada exitosamente!')
        return login()
    except sqlite3.IntegrityError:
        print('Esta cuenta ya existe. Prueba Iniciar Sesión')
    except Exception as ex:
        print('No se pudo crear la cuenta!')
        print(f'Error: {ex}')


def login():
    print('-------- Iniciar Sesión --------\n')
    gmail = input('Ingrese su correo electrónico: ')
    master_password = input('Ingrese su contraseña maestra: ')
    return validate_login(gmail, master_password)


def validate_login(gmail, master_password):
    sql = f'SELECT * FROM Users WHERE correoE = "{gmail}"'
    cursor.execute(sql)
    user = cursor.fetchall()
    for data in user:
        current_user = data[1]
        if check_password_hash(data[3], master_password):
            print('')
            print(f'-------- Bienvenido @{current_user} --------\n')
            return boveda(data)
        else:
            print('Correo electrónico o Contraseña maestra Invalido!')


def boveda(data):
    current_user = data[1]
    print('-------- Bóveda --------\n')
    print(f'¿Qué deseas hacer @{current_user}? \n')
    print('1 - Agegar Contraseña.', '2 - Ver Contraseñas.', '3 - Actualizar Contraseña.', '4 - Borrar Contraseña.',
          '5 - Salir.\n', sep='\n')
    option = input('¿Qué desea hacer?: ')
    if option == '1':
        return create_password(data)
    elif option == '2':
        return read_passwords(data)
    elif option == '3':
        return update_password(data)
    elif option == '4':
        return delete_password(data)
    elif option == '5':
        print('Hasta la próxima!!')
    else:
        print('Opción Inválida.')


def create_password(data):
    current_user = data[1]
    print('-------- Creando Contraseña --------\n')
    password = input('Ingresa la contraseña del sitio web: ')
    website = input('Ingresa la url del sitio web: ')
    date_now = datetime.datetime.now()
    current_date = datetime.datetime.strftime(date_now, '%d/%m/%Y %H:%M:%S %p')
    sql = f'INSERT INTO Passwords VALUES(NULL, "{current_user}", "{password}", "{website}", "{current_date}")'
    try:
        cursor.execute(sql)
        print('Contraseña creada exitosamente!\n')
        return read_passwords(data)
    except Exception as ex:
        print('No se pudo registrar la contraseña.')
        print(f'Error: {ex}')


def read_passwords(data):
    current_user = data[1]
    print('-------- Lista de Contraseñas --------\n')
    sql = f'SELECT * FROM Passwords WHERE Passwords.username = "{current_user}"'
    cursor.execute(sql)
    result = cursor.fetchall()
    for i in result:
        print(f'Url: {i[3]}', f'Nombre de Usuario: {i[1]}',
              f'Contraseña del Sitio: {i[2]}', f'Fecha de Creación: {i[4]}\n', sep='\n')
    input('Presione enter para continuar: ')
    return boveda(data)


def update_password(data):
    current_user = data[1]
    print('-------- Actualizando Contraseña --------\n')
    sql_read = f'SELECT * FROM Passwords WHERE Passwords.username = "{current_user}"'
    cursor.execute(sql_read)
    result = cursor.fetchall()
    for i in result:
        print(f'Id Contaseña -> {i[0]} |', f'Contraseña -> {i[2]} |', f'Sitio web -> {i[3]}')
    id_password = int(input('Ingresa el Id de la contraseña a actualizar: '))
    new_password = input('Ingresa la nueva contraseña: ')
    sql_upd = f'UPDATE Passwords SET password = "{new_password}" WHERE id = "{id_password}"'
    try:
        cursor.execute(sql_upd)
        print('Contraseña actualizada con exito!')
        return read_passwords(data)
    except Exception as ex:
        print('No se pudo actualizar la contraseña')
        print(f'Error: {ex}')


def delete_password(data):
    current_user = data[1]
    print('-------- Borrar Contraseña --------\n')
    sql_read = f'SELECT * FROM Passwords WHERE Passwords.username = "{current_user}"'
    cursor.execute(sql_read)
    result = cursor.fetchall()
    for i in result:
        print(f'Id Contaseña -> {i[0]} |', f'Contraseña -> {i[2]} |', f'Sitio web -> {i[3]}')
    id_password = int(input('Ingresa el Id de la contraseña a borrar: '))
    warning = input('Está a punto de borrar una contraseña. ¿Desea continuar? (S/N): ')
    if warning.upper() == 'S' or warning.upper() == 'SI':
        sql_del = f'DELETE FROM Passwords WHERE id = {id_password}'
        try:
            cursor.execute(sql_del)
            print('Contraseña borrada con éxito!')
        except Exception as ex:
            print('Ocurrió un error al borrar la contraseña')
            print(f'Error: {ex}')
    elif warning.upper() == 'N' or warning.upper() == 'NO':
        print('No se borró la contraseña')
    else:
        print('Opción inválida')
    return read_passwords(data)


home()


connection.commit()
connection.close()
