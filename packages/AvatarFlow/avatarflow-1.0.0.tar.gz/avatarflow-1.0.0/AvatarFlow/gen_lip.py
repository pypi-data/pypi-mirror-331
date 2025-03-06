import requests
import json
import time
import urllib.parse
import random
import re
import os
from reg_lip import *
import subprocess
import os

def agregar_franja_negra(video_entrada, video_salida):
    """
    Agrega una franja negra de 70 píxeles en la parte superior del video.
    """
    if not os.path.exists(video_entrada):
        print(f"⚠️ El archivo no existe.")
        return

    comando = [
        "ffmpeg",
        "-y",
        "-i", video_entrada,
        "-vf", "pad=iw:ih+70:0:70:black",  # Agregar franja negra arriba
        "-c:a", "copy",
        video_salida
    ]

    try:
        proceso = subprocess.run(comando, check=True, stderr=subprocess.STDOUT)
        #print(f"✅ Franja negra agregada: {video_salida}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error al procesar el video:\n{e.output.decode()}")

def recortar_franja_negra(video_entrada, video_salida):
    """
    Recorta una franja negra de 70 píxeles en la parte superior del video.
    """
    if not os.path.exists(video_entrada):
        print(f"⚠️ El archivo no existe.")
        return

    comando = [
        "ffmpeg",
        "-y",
        "-i", video_entrada,
        "-vf", "crop=iw:ih-70:0:70",  # Recortar 70 píxeles desde arriba
        "-c:a", "copy",
        video_salida
    ]

    try:
        proceso = subprocess.run(comando, check=True, stderr=subprocess.STDOUT)
        #print(f"✅ Franja negra recortada: {video_salida}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error al procesar el video:\n{e.output.decode()}")



def generar_nombre_projecto():
    """Genera un nombre completo triplicando el nombre y apellido, junto con un número aleatorio de 3 dígitos."""
    nombres = ["Juan", "Pedro", "Maria", "Ana", "Luis", "Sofia", "Diego", "Laura", "Javier", "Isabel",
               "Pablo", "Marta", "David", "Elena", "Sergio", "Irene", "Daniel", "Alicia", "Carlos", "Sandra",
               "Antonio", "Lucia", "Miguel", "Sara", "Jose", "Cristina", "Alberto", "Blanca", "Alejandro", "Marta",
               "Francisco", "Esther", "Roberto", "Silvia", "Manuel", "Patricia", "Marcos", "Victoria", "Fernando", "Rosa",
               # Nombres comunes de EE.UU.
               "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Charles", "Thomas",
               "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
               "Kenneth", "Kevin", "Brian", "George", "Edward", "Ronald", "Timothy", "Jason", "Jeffrey", "Ryan",
               "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
               "Benjamin", "Samuel", "Frank", "Gregory", "Raymond", "Alexander", "Patrick", "Jack", "Dennis", "Jerry",
               "Tyler", "Aaron", "Henry", "Douglas", "Jose", "Peter", "Adam", "Zachary", "Nathan", "Walter",
               "Kyle", "Harold", "Carl", "Arthur", "Gerald", "Roger", "Keith", "Jeremy", "Terry", "Lawrence",
               "Sean", "Christian", "Ethan", "Austin", "Joe", "Jordan", "Albert", "Jesse", "Willie", "Billy",
               "Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Alonso", "Diaz",
                 "Martin", "Ruiz", "Hernandez", "Jimenez", "Torres", "Moreno", "Gomez", "Romero", "Alvarez", "Vazquez",
                 "Gil", "Lopez", "Ramirez", "Santos", "Castro", "Suarez", "Munoz", "Gomez", "Gonzalez", "Navarro",
                 "Dominguez", "Lopez", "Rodriguez", "Sanchez", "Perez", "Garcia", "Gonzalez", "Martinez", "Fernandez", "Lopez",
                 # Apellidos comunes de EE.UU.
                 "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                 "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
                 "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
                 "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
                 "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
                 "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
                 "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper",
                 "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ward", "Cox", "Diaz", "Richardson", "Wood"]


    nombre = random.choice(nombres)
    numero = random.randint(100, 999)

    nombre_completo = f"{nombre}{numero}"
    return nombre_completo

def extraer_datos(response_text):
    """
    Extrae 'id', 'organizationId' y 'userId' de la respuesta JSONL de la API.

    Parámetros:
    - response_text (str): Texto de respuesta en formato JSONL.

    Retorna:
    - tuple: (id, organizationId, userId) si existen, sino (None, None, None).
    """
    try:
        for line in response_text.splitlines():  # Procesar línea por línea
            data = json.loads(line)
            json_data = data.get("json", [])

            if isinstance(json_data, list) and len(json_data) > 2:
                nested_list = json_data[2]
                if isinstance(nested_list, list) and nested_list:
                    first_entry = nested_list[0]
                    if isinstance(first_entry, list) and first_entry:
                        obj = first_entry[0]
                        if isinstance(obj, dict) and "id" in obj:
                            return obj.get("id"), obj.get("organizationId"), obj.get("userId")
    except json.JSONDecodeError:
        pass  # Ignorar errores de JSON

    return None, None, None  # Si no se encuentran los valores


def create_sync_so_project(org_id, authorization_token, project_name):
    """
    Crea un proyecto en Sync.so y extrae los IDs del resultado.

    Parámetros:
    - org_id (str): ID de la organización.
    - authorization_token (str): Token de autenticación.
    - project_name (str): Nombre del proyecto.

    Retorna:
    - tuple: (project_id, organization_id, user_id) si se crea correctamente.
    """
    url = "https://api.sync.so/trpc/projects.create?batch=1"
    headers = {
        "Host": "api.sync.so",
        "Connection": "keep-alive",
        "x-org-id": org_id,
        "Authorization": f"Bearer {authorization_token}",
        "sec-ch-ua-platform": "Windows",
        "sec-ch-ua": "Not(A:Brand);v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "trpc-accept": "application/jsonl",
        "content-type": "application/json",
        "x-sync-source": "web",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }

    # Datos a enviar
    data = {"0": {"json": {"name": project_name, "description": "", "visibility": "USER", "mode": "DEVELOPER"}}}

    # Enviar la solicitud
    response = requests.post(url, headers=headers, json=data)

    #response.raise_for_status()  # Lanzar error si la solicitud falla

    # Extraer los datos de la respuesta
    project_id, organization_id, user_id = extraer_datos(response.text)

    return project_id, organization_id, user_id


def generar_lipsync(x_org_id, authorization, x_project_id, version, video_url, audio_url):
    """Envía una solicitud a la API de Sync.so para generar un lipsync."""

    # Definimos las URLs y las configuraciones para las versiones
    if version == "1.7.1":
        model = "lipsync-1.7.1"  # Nombre del modelo específico para la versión 1.7.1
        url = "https://sync.so/api/generate"  # URL diferente para la versión 1.7.1
        headers = {
        "Host": "sync.so",
        "Connection": "keep-alive",
        "x-org-id": x_org_id,
        "Authorization": f"Bearer {authorization}",
        "x-project-id": x_project_id,
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "baggage": "sentry-environment=production,sentry-release=NCOlpcAefmQsxNofnxTvc,sentry-public_key=ae5c877441c3c02186a92764c98c688f,sentry-trace_id=f050b10660294abdb510011951d21918,sentry-replay_id=705605fcdc3d4b318d6a8c446256e51e,sentry-sample_rate=1,sentry-sampled=true",
        "sentry-trace": "f050b10660294abdb510011951d21918-ad283984cd7f599f-1",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/projects/Dq5BxMS8aZhj1YuEQRuJQ7/playground",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Content-Length": "1174"
        }
        data = {
            "model": model,
            "input": [
                {
                    "type": "video",
                    "url": video_url
                },
                {
                    "type": "audio",
                    "url": audio_url
                }
            ],
            "options": {
                "pads": [0, 5, 0, 0],
                "output_format": "mp4",
                "sync_mode": "bounce",
                "active_speaker": False
            }
        }

    elif version in ("1.8.0", "1.9.0"): # Simplificado con 'in'
        if version == "1.8.0":
            model = f"lipsync-1.8.0"
        else:
            model = f"lipsync-1.9.0-beta"


        url = "https://sync.so/api/generate"
        headers = {
        "Host": "sync.so",
        "Connection": "keep-alive",
        "x-org-id": x_org_id,
        "Authorization": f"Bearer {authorization}",
        "x-project-id": x_project_id,
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "baggage": "sentry-environment=production,sentry-release=NCOlpcAefmQsxNofnxTvc,sentry-public_key=ae5c877441c3c02186a92764c98c688f,sentry-trace_id=f050b10660294abdb510011951d21918,sentry-replay_id=705605fcdc3d4b318d6a8c446256e51e,sentry-sample_rate=1,sentry-sampled=true",
        "sentry-trace": "f050b10660294abdb510011951d21918-ad283984cd7f599f-1",
        "sec-ch-ua-platform": '"Windows"',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/projects/Dq5BxMS8aZhj1YuEQRuJQ7/playground",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Content-Length": "1174"
        }
        data = {
            "model": model,
            "input": [
                { "url": video_url, "type": "video" }, # Corrección: url primero
                { "url": audio_url, "type": "audio" }  # Corrección: url primero
            ],
            "options": {
                "pads": [0, 5, 0, 0],
                "output_format": "mp4",
                "sync_mode": "bounce",
                "active_speaker": False
            }
        }

    else:
        return "Versión no válida"

    # Realizamos la solicitud a la API
    response = requests.post(url, headers=headers, data=json.dumps(data))

    id_gen = extract_id(response.text)
    return id_gen


def extract_output_media_url(text):
    """Extrae outputMediaUrl usando expresiones regulares."""
    match = re.search(r'"outputMediaUrl":"([^"]+)"', text)  # Busca el patrón
    if match:
        return match.group(1)  # Retorna la URL encontrada
    return None  # Retorna None si no hay coincidencia

def download_video(url, save_path):
    """Descarga el video desde la URL y lo guarda en la ruta especificada."""
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Crea la carpeta si no existe

        with open(save_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)

        print(f"📥 Video descargado...")
    else:
        print(f"⚠️ Error al descargar el video...")

def obtener_datos(token: str, id_solicitud: str):
    contador_segundos=0
    """Consulta la API cada 10 segundos hasta encontrar outputMediaUrl y descarga el video."""
    url = f"https://api.sync.so/trpc/generations.getAll?batch=1&input=%7B%220%22%3A%7B%22json%22%3A%7B%22fromPlayground%22%3Atrue%2C%22ids%22%3A%5B%22{id_solicitud}%22%5D%7D%7D%7D"

    headers = {
        "Authorization": f"Bearer {token}",
        "x-org-id": "88769fc3-397f-47a1-92c6-00ebaa75b4ea",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "content-type": "application/json"
    }

    while True:
        response = requests.get(url, headers=headers)
        #print(response.text)

        if response.status_code == 200:
            output_url = extract_output_media_url(response.text)
            if output_url:
                print(f"✅ Video listo...")

                # Ruta donde se guardará el video
                save_path = "/tmp/output.mp4"
                download_video(output_url, save_path)

                # Definir la ruta de la carpeta
                ruta = "/content/video/"
                # Verificar si la carpeta existe
                if not os.path.exists(ruta):
                    # Si no existe, crearla
                    os.makedirs(ruta)
                    print(f"La carpeta ha sido creada.")
                else:
                    print(f"La carpeta ya existe.")
                # Recortar la franja negra
                recortar_franja_negra("/tmp/output.mp4", "/content/video/output.mp4")

                return save_path  # Salir del bucle

            #print("⏳ Procesando... esperando 10 segundos...")

            contador_segundos += 10
            minutos = contador_segundos // 60
            segundos = contador_segundos % 60
            print(f"\r⏱️ Processing... Time elapsed: {minutos} minutes and {segundos} seconds", end='', flush=True)


        else:
            print(f"⚠️ Error en la solicitud: {response.status_code}")

        time.sleep(10)  # Esperar 10 segundos antes de reintentar






def extract_id(data_input):
    if isinstance(data_input, dict):
        return data_input.get("id")
    elif isinstance(data_input, str):
        try:
            data_dict = json.loads(data_input)
            return data_dict.get("id")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON string: {e}", doc=data_input, pos=0)  # Mejorado el manejo de errores
    else:
        raise TypeError("Input must be a dictionary or a JSON string")

def extraer_datos_subida(response_text):
    """
    Extrae 'uploadUrl', 'uploadToken' y 'uploadKey' de la respuesta JSONL,
    separando y procesando solo las partes relevantes.

    Parámetros:
    - response_text (str): Respuesta JSON en formato JSONL.

    Retorna:
    - tuple: (uploadUrl, uploadToken, uploadKey) si existen, sino (None, None, None).
    """
    try:
        # Dividir el JSON en líneas
        for line in response_text.splitlines():
            #print("Línea JSON:", line)  # Imprimir cada línea para ver la estructura

            # Buscar los campos 'uploadUrl', 'uploadToken' y 'uploadKey'
            upload_url_match = re.search(r'"uploadUrl":"(https?://[^"]+)"', line)
            upload_token_match = re.search(r'"uploadToken":"([^"]+)"', line)
            upload_key_match = re.search(r'"uploadKey":"([^"]+)"', line)

            # Si se encuentran los valores correspondientes, extraerlos
            upload_url = upload_url_match.group(1) if upload_url_match else None
            upload_token = upload_token_match.group(1) if upload_token_match else None
            upload_key = upload_key_match.group(1) if upload_key_match else None

            # Imprimir los resultados intermedios
            #print("uploadUrl:", upload_url)
            #print("uploadToken:", upload_token)
            #print("uploadKey:", upload_key)

            # Si todos los valores existen, devolverlos
            if upload_url and upload_token and upload_key:
                return upload_url, upload_token, upload_key

    except Exception as e:
        print("Error inesperado:", e)

    return None, None, None  # Si no se encuentran los valores necesarios


def get_upload_url(org_id, authorization_token, file_name, content_type, is_public=False):
    """Obtiene la URL de subida para un archivo."""
    url = "https://api.sync.so/trpc/fileStorage.getUploadUrl?batch=1"
    headers = {
        "Host": "api.sync.so",
        "Connection": "keep-alive",
        "x-org-id": org_id,
        "Authorization": f"Bearer {authorization_token}",
        "sec-ch-ua-platform": "Windows",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "trpc-accept": "application/jsonl",
        "content-type": "application/json",
        "x-sync-source": "web",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }
    data = {
        "0": {
            "json": {
                "fileName": file_name,
                "contentType": content_type,
                "isPublic": is_public,
            }
        }
    }

    try:
        response = requests.get(url, headers=headers, params={"input": json.dumps(data)})  # Usar params para GET
        response.raise_for_status()
        #print(response.text)
        # Extraer los datos utilizando la función auxiliar
        upload_url, upload_token, upload_key = extraer_datos_subida(response.text)
        return upload_url, upload_token, upload_key


    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud (get_upload_url): {e}")
        return None, None, None


def extraer_datos_signed_url(response_text):
    """
    Extrae la signed URL de la respuesta utilizando expresiones regulares.
    Busca cualquier URL que empiece con 'https://' en el texto de la respuesta.
    """
    try:
        # Usamos una expresión regular para encontrar cualquier URL que comience con 'https://'
        urls = re.findall(r'https://[^\s"]+', response_text)

        # Si encontramos alguna URL, la retornamos
        if urls:
            return urls[0]  # Devolvemos la primera URL que encuentre

    except Exception as e:
        print(f"Error: {e}")

    return None




def get_signed_url(org_id, authorization_token, upload_token, upload_key):
    """Obtiene la URL firmada para un archivo subido."""
    url = f"https://api.sync.so/trpc/fileStorage.getSignedUrl"
    headers = {
        "Host": "api.sync.so",
        "Connection": "keep-alive",
        "x-org-id": org_id,
        "Authorization": f"Bearer {authorization_token}",
        "sec-ch-ua-platform": "Windows",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "trpc-accept": "application/jsonl",
        "content-type": "application/json",
        "x-sync-source": "web",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }

    input_param = {
        "0": {
            "json": {
                "uploadToken": upload_token,
                "uploadKey": upload_key
            }
        }
    }

    # Crear los parámetros de la URL (en formato query)
    params = {
        "batch": "1",
        "input": str(input_param).replace("'", '"')  # Convertir el dict a JSON compatible
    }


    try:
        response = requests.get(url, headers=headers, params=params) #Usar params para GET
        response.raise_for_status()
        #print(response.text)
        signed_url = extraer_datos_signed_url(response.text)
        return signed_url

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud (get_signed_url): {e}")
        return None



def upload_file(upload_url, file_path, content_type):
    """Sube un archivo a la URL proporcionada."""
    try:
        with open(file_path, 'rb') as f:
            headers = {"Content-Type": content_type}
            response = requests.put(upload_url, headers=headers, data=f)
            response.raise_for_status()
            return True  # Subida exitosa

    except FileNotFoundError:
        print(f"Error: Archivo no encontrado...")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud (upload_file): {e}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")  # Captura otras excepciones
        return False



def create_generation(org_id, authorization_token, project_id, video_url, audio_url):
    """Crea una nueva generación utilizando las URLs de los archivos."""
    url = "https://sync.so/api/generate"
    headers = {
        "Host": "sync.so",
        "Connection": "keep-alive",
        "x-org-id": org_id,
        "Authorization": f"Bearer {authorization_token}",
        "x-project-id": project_id,
        "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?0",
        "baggage": "sentry-environment=production,sentry-release=NCOlpcAefmQsxNofnxTvc,sentry-public_key=ae5c877441c3c02186a92764c98c688f,sentry-trace_id=f050b10660294abdb510011951d21918,sentry-replay_id=705605fcdc3d4b318d6a8c446256e51e,sentry-sample_rate=1,sentry-sampled=true",
        "sentry-trace": "f050b10660294abdb510011951d21918-ad283984cd7f599f-1",
        "sec-ch-ua-platform": "Windows",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://sync.so",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://sync.so/projects/Dq5BxMS8aZhj1YuEQRuJQ7/playground",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate",

    }
    data = {
        "model": "lipsync-1.7.1",
        "input": [
            {"type": "video", "url": video_url},
            {"type": "audio", "url": audio_url}
        ],
        "options": {"pads": [0, 5, 0, 0], "output_format": "mp4", "sync_mode": "bounce", "active_speaker": False}
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        id_gen = extract_id(response.text)
        #print(response.json)
        return id_gen

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud (create_generation): {e}")
        return None



# --- Función principal ---

def run_lipsync(org_id, authorization_token, project_id, video_file_path, audio_file_path, mod_version):

    # 1. Obtener URL de subida para el video
    print("Obteniendo URL de subida para el video...")
    video_upload_url, video_upload_token, video_upload_key = get_upload_url(
        org_id, authorization_token, "video-input.mp4", "video/mp4"
    )

    #print(video_upload_url)
    #print(video_upload_token)
    #print(video_upload_key)


    if not video_upload_url:
        return

    time.sleep(2)  # Pausa

    # 2. Subir el video
    print("Subiendo video...")
    if not upload_file(video_upload_url, video_file_path, "video/mp4"):
        return


    time.sleep(5)  # Pausa

    # 3. Obtener URL firmada para el video
    print("Obteniendo URL firmada para el video...")
    signed_video_url = get_signed_url(org_id, authorization_token, video_upload_token, video_upload_key)

    #print("signed_video_url", signed_video_url)


    if not signed_video_url:
      return
    parsed_url = urllib.parse.urlparse(signed_video_url)
    video_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path + "?" + urllib.parse.urlencode(urllib.parse.parse_qs(parsed_url.query))
    #print("signed_video_url2",video_url)

    time.sleep(2)  # Pausa

    # 4. Obtener URL de subida para el audio
    print("Obteniendo URL de subida para el audio...")
    audio_upload_url, audio_upload_token, audio_upload_key = get_upload_url(
        org_id, authorization_token, "audio-input.mp3", "audio/wav"  # Usar audio/wav
    )
    if not audio_upload_url:
        return

    #print("audio_upload_url", audio_upload_url)
    #print("audio_upload_token", audio_upload_token)
    #print("audio_upload_key", audio_upload_key)

    time.sleep(2)  # Pausa


    # 5. Subir el audio
    print("Subiendo audio...")
    if not upload_file(audio_upload_url, audio_file_path, "audio/wav"):  # Usar audio/wav
        return

    time.sleep(5)  # Pausa

    # 6. Obtener URL firmada para el audio
    print("Obteniendo URL firmada para el audio...")
    signed_audio_url = get_signed_url(org_id, authorization_token, audio_upload_token, audio_upload_key)
    #print("signed_audio_url",signed_audio_url)

    if not signed_audio_url:
      return
    parsed_url = urllib.parse.urlparse(signed_audio_url)
    audio_url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path + "?" + urllib.parse.urlencode(urllib.parse.parse_qs(parsed_url.query))
    #print("signed_audio_url2",audio_url)

    time.sleep(2)  # Pausa

    # 7. Crear la generación
    print("Creando generación...")
    generation_id = generar_lipsync(org_id, authorization_token, project_id, mod_version, signed_video_url, signed_audio_url)
    #generation_id = generar_180(org_id, authorization_token, project_id, signed_video_url, signed_audio_url)
    #generation_id = create_generation(org_id, authorization_token, project_id, signed_video_url, signed_audio_url)
    if generation_id:
        #print("generation_id:", generation_id)

        # 🔹 Edita estos valores con tu propio TOKEN e ID
        TOKEN = os.environ.get("ACCESS_TOKEN")
        ID_SOLICITUD = generation_id
        # Ejecutar la función
        video_path = obtener_datos(TOKEN, ID_SOLICITUD)
        print(f"\n🎉 Video guardado...")

    else:
        print("Error al crear la generación.")
        register_lip()
        time.sleep(1)
        str_reg = os.environ.get("REG")
        if str_reg=="REGISTRO":
            video_file_path = os.environ.get("VIDEO_PATH")
            audio_file_path = os.environ.get("AUDIO_PATH")
            mod_version = os.environ.get("MOD_VERSION")
            get_avatar(video_file_path, audio_file_path, mod_version)
            os.environ["REG"] = "NO"
    return generation_id


# --- Ejemplo de uso ---
# Reemplaza estos valores con los tuyos

# ✅ **Ejemplo de uso**

def get_avatar(video_file_path, audio_file_path, mod_version):
    agregar_franja_negra("/tmp/video.mp4", "/tmp/video_f.mp4")

    os.environ["VIDEO_PATH"] = video_file_path
    os.environ["AUDIO_PATH"] = audio_file_path
    os.environ["MOD_VERSION"] = mod_version
    

    access_token = os.environ.get("ACCESS_TOKEN")
    refresh_token = os.environ.get("REFRESH_TOKEN")
    refersh_token_id = os.environ.get("REFRESH_TOKEN_ID")
    users_id = os.environ.get("USER_ID")
    #print(access_token)
    #print(refresh_token)
    #print(refersh_token_id)
    #print(users_id)

    project_name = generar_nombre_projecto()
    # Crear el proyecto y obtener los IDs
    project_id, organization_id, user_ids = create_sync_so_project(users_id, access_token, project_name)

    # Mostrar los resultados
    if project_id:
        print("✅ Proyecto creado con éxito:")
        #print("project_id:", project_id)
        #print("organization_id:", organization_id)
        #print("user_id:", user_ids)

        org_id = users_id
        authorization_token = access_token

        generation_id = run_lipsync(org_id, authorization_token, project_id, video_file_path, audio_file_path, mod_version)

    else:
        print("❌ No se pudo crear el proyecto.")
        register_lip()
        time.sleep(1)
        str_reg = os.environ.get("REG")
        if str_reg=="REGISTRO":
            get_avatar(video_file_path, audio_file_path, mod_version)
            os.environ["REG"] = "NO"



