# Importa las bibliotecas necesarias
import face_recognition
import cv2
import numpy as np
import mysql.connector
from datetime import datetime

# Conecta a la base de datos MySQL
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="faces"
)
db_cursor = db_connection.cursor()

# Crea la tabla 'registro' si no existe
create_table_query = """
CREATE TABLE IF NOT EXISTS registro (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    hora TIME NOT NULL
);
"""
db_cursor.execute(create_table_query)

# Carga y codifica las imágenes de las caras conocidas
obama_image = face_recognition.load_image_file("obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

biden_image = face_recognition.load_image_file("biden.jpg")
biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

antonio_image = face_recognition.load_image_file("Antonio_Estrella.jpg")
antonio_face_encoding = face_recognition.face_encodings(antonio_image)[0]

scarlett_image = face_recognition.load_image_file("Scarlett.jpg")
scarlett_face_encoding = face_recognition.face_encodings(scarlett_image)[0]

# Crea arrays de los encodings y nombres de caras conocidas
known_face_encodings = [
    obama_face_encoding,
    biden_face_encoding,
    antonio_face_encoding,
    scarlett_face_encoding
]
known_face_names = [
    "Barack Obama",
    "Joe Biden",
    "Antonio Estrella",
    "Scarlett Johansson"
]

# Inicializa variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

# Inicia la captura de video desde la webcam
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
            name = "Unknown"

            # Si hay coincidencia, elige la cara conocida más cercana
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

                # Obtiene la fecha y hora actual
                now = datetime.now()
                current_date = now.date()
                current_time = now.time()

                # Verifica si ya se registró esta cara hoy
                check_query = "SELECT * FROM registro WHERE nombre = %s AND fecha = %s"
                db_cursor.execute(check_query, (name, current_date))
                result = db_cursor.fetchone()

                # Si no se ha registrado hoy, inserta el registro en la base de datos
                if not result:
                    insert_query = "INSERT INTO registro (fecha, nombre, hora) VALUES (%s, %s, %s)"
                    db_cursor.execute(insert_query, (current_date, name, current_time))
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
