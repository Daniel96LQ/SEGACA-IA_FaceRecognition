# Importa las bibliotecas necesarias
# Biblioteca para el reconocimiento facial
import face_recognition
# OpenCV (Open Source Computer Vision) - para procesamiento de imágenes y videos
import cv2
# NumPy - para operaciones matemáticas y manipulación de matrices
import numpy as np
# MySQL Connector - para conectar y trabajar con bases de datos MySQL
import mysql.connector
# Biblioteca para manipulación de fechas y horas
from datetime import datetime
# Biblioteca para operaciones con el sistema operativo (por ejemplo, manipulación de archivos y directorios)
import os
# Passlib - para el hashing de contraseñas utilizando el algoritmo bcrypt
from passlib.hash import bcrypt

# Conecta a la base de datos MySQL
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ss"
)
db_cursor = db_connection.cursor()
#Codigo de Persona
codper = 0
# Materia
materia = ''
# Obtener dia, mes y año
day = (datetime.now().weekday() + 1) % 7
month = datetime.now().strftime('%m')
year = datetime.now().strftime('%Y')
# OBTENER PERIODOS Y HORAS DE PERIODOS
hour = datetime.now().strftime('%H:%M:%S')
per = 0
inicio = ''
final = ''
# Directorio de imágenes
dir_photos = "Photos"
# Lista de encodings de rostros y nombres de rostros conocidos
known_face_encodings = []
known_face_names = []

def login():
    global codper, materia, per, inicio, final
    # Intentos máximos permitidos
    intentos_maximos = 3
    intentos = 0

    while intentos < intentos_maximos:
        # Ingresa el correo de usuario y contraseña desde el usuario
        email = input("Ingrese su correo: ")
        contrasena = input("Ingrese su contraseña: ")

        # Consulta la contraseña hasheada desde la base de datos
        select_query = "SELECT codper, password FROM usuario WHERE email = %s"
        db_cursor.execute(select_query, (email,))
        result = db_cursor.fetchone()

        if result:
            contrasena_hash = result[1]
            
            # Verifica la contraseña introducida con la contraseña hasheada almacenada
            if bcrypt.verify(contrasena, contrasena_hash):
                print("Inicio de sesión exitoso.")
                # Capturamos el valor del codigo de persona
                codper = result[0]
                
                if '08:00:00' < hour < '09:20:00':
                    per = 1
                    inicio = '08:00'
                    final = '09:20'
                elif '09:20:00' < hour < '10:40:00':
                    per = 2
                    inicio = '09:20'
                    final = '10:40'
                elif '11:00:00' < hour < '13:20:00':
                    per = 3
                    inicio = '11:00'
                    final = '12:20'
                elif '14:00:00' < hour < '15:20:00':
                    per = 4
                    inicio = '14:00'
                    final = '15:20'
                elif '15:20:00' < hour < '16:50:00':
                    per = 5
                    inicio = '15:20'
                    final = '16:40'
                elif '17:00:00' < hour < '18:20:00':
                    per = 6
                    inicio = '17:00'
                    final = '18:20'
                elif '18:20:00' < hour or hour < '08:00:00':
                    per = 1
                    inicio = '08:00'
                    final = '09:20'
                    
                # print("PER: ", per)
                # print("CODPER: ", codper)
                # print("DIA: ", day)
                
                # Consulta la materia que se esta impartiendo en el periodo actual
                select_query = "SELECT descmat FROM profesor as P, course_detail_doc as CDD, materia as M WHERE P.codper = %s AND P.codprof = CDD.codprof AND CDD.day = %s AND CDD.periodo = %s AND P.codmat = M.codmat"
                db_cursor.execute(select_query, (codper, day, per))
                result = db_cursor.fetchone()
                # almacenamos el nombre de la materia
                materia = result[0]
                
                print("Materia: ", materia)
                
                return True
            else:
                print("Credenciales incorrectas. Intentos restantes:", intentos_maximos - intentos - 1)
                intentos += 1
        else:
            print("Credenciales incorrectas. Intentos restantes:", intentos_maximos - intentos - 1)
            intentos += 1
            
    print("Número máximo de intentos alcanzado. Saliendo del programa.")
    return False

# Si el login es exitoso, ejecuta el reconocedor facial
if login():
    # Recorre todos los archivos en el directorio de imágenes
    for filename in os.listdir(dir_photos):
        # Obtiene la ruta completa del archivo
        file_path = os.path.join(dir_photos, filename)
        
        # Verifica si el archivo es una imagen
        if os.path.isfile(file_path) and file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            # Carga la imagen y obtiene el encoding del rostro
            image = face_recognition.load_image_file(file_path)
            face_encoding = face_recognition.face_encodings(image)[0]
            
            # Agrega el encoding y el nombre del archivo a las listas
            known_face_encodings.append(face_encoding)
            known_face_names.append(filename.split(".")[0])
        
    # Inicializa variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    # Inicia la captura de video desde la camara
    video_capture = cv2.VideoCapture(1)

    while True:
        # Captura frames de la webcam
        ret, frame = video_capture.read()

        # Procesa solo cada segundo frame para mejorar la velocidad
        if process_this_frame:
            # Redimensiona el frame para acelerar el procesamiento
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convierte el frame a formato RGB ya que OpenCV usa BGR
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Encuentra las ubicaciones de los rostros en el frame
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # Compara los encodings con las caras conocidas
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Desconocido"

                # Si hay coincidencia, elige la cara conocida más cercana
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                    # Obtiene la fecha y hora actual
                    now = datetime.now()
                    current_date = now.date()
                    current_time = now.time()
                    
                    print('Materia: ', materia)
                    print('Inicio: ', inicio)
                    print('Final: ', final)
                    
                    # Verifica si ya se registró esta cara hoy
                    check_query = "SELECT * FROM estudiante as E, asistencia as A WHERE E.codest = %s AND E.codest = A.codest AND A.inicial = %s AND A.final = %s AND A.fecha = %s AND A.materia = %s"
                    db_cursor.execute(check_query, (name, inicio, final, current_date, materia))
                    result = db_cursor.fetchone()

                    # Si no se ha registrado hoy, inserta el registro en la base de datos
                    if not result:
                        insert_query = "INSERT INTO asistencia (materia, detalle, inicial, final, fecha, color, textcolor, codest) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                        db_cursor.execute(insert_query, (materia, 'ASISTIO - RECONOCIMIENTO FACIAL', inicio, final, current_date, '#06652E', '#FFFFFF', name))
                        db_connection.commit()
                    else:
                        print(f"{name} ya ha sido registrado hoy")

                face_names.append(name)

        process_this_frame = not process_this_frame

        # Muestra los resultados en el frame
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Reescala las coordenadas a la escala original
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Dibuja un rectángulo alrededor del rostro
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Dibuja un cuadro de texto con el nombre
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Muestra el frame con los resultados de detección
        cv2.imshow('Video', frame)

        # Presiona 'q' para salir del bucle
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera la conexión de la webcam
    video_capture.release()
    cv2.destroyAllWindows()
