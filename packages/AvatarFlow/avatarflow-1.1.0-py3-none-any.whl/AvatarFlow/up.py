#@title upload file
import requests
import os

def subir_imagen(archivo_path, url):
    # Los encabezados necesarios
    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Windows",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "sec-ch-ua": "Not(A:Brand;v=99, Google Chrome;v=133, Chromium;v=133)",
        "Content-Type": "image/png",  # Especificamos que estamos enviando una imagen PNG
        "sec-ch-ua-mobile": "?0",
        "Origin": "https://app.jogg.ai",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.jogg.ai/",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }

    # Abrimos el archivo de la imagen en modo binario
    with open(archivo_path, 'rb') as file:
        file_data = file.read()

        # Realizamos la solicitud PUT para subir la imagen
        response = requests.put(url, headers=headers, data=file_data)

    # Verificamos el código de estado de la respuesta
    if response.status_code == 200:
        try:
            # Intentamos obtener la respuesta como JSON
            respuesta_json = response.json()
            msg = respuesta_json.get("msg", "")
            if msg == "success":
                return "Imagen subida exitosamente"
            else:
                return f"Error: {msg}"
        except requests.exceptions.JSONDecodeError:
            # Si no es posible procesar la respuesta como JSON, mostramos el contenido de la respuesta
            return f"Error: No se pudo procesar la respuesta JSON. Respuesta recibida: {response.text}"
    else:
        # Si el código de estado no es 200, mostramos el código de estado y el contenido de la respuesta
        return f"Error al subir la imagen. Código de estado: {response.status_code}, Respuesta: {response.text}"


# Función para subir el archivo a la URL de la API
def subir_archivo(authorization_token, filename):
    url = "https://app.jogg.ai/edge-service/common/upload/oss_sign"

    headers = {
        "Host": "app.jogg.ai",
        "Connection": "keep-alive",
        "sec-ch-ua-platform": "Windows",
        "Authorization": authorization_token,
        "sec-ch-ua": "Not(A:Brand;v=99, Google Chrome;v=133, Chromium;v=133)",
        "sec-ch-ua-mobile": "?0",
        "X-APP-ID": "52002",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://app.jogg.ai",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.jogg.ai/avatar",
        "Accept-Language": "es-ES,es;q=0.9",
        "Accept-Encoding": "gzip, deflate"
    }

    # Datos a enviar en la solicitud POST
    data = {
        "filetype": "image/png",
        "filename": filename,
        "use_to": "media",
        "source": 1
    }

    response = requests.post(url, json=data, headers=headers)

    try:
        respuesta_json = response.json()
        msg = respuesta_json.get("msg", "")
        sign_url = respuesta_json.get("data", {}).get("sign_url", None)
        key = respuesta_json.get("data", {}).get("full_path", None)

        # Validar si el msg es "success"
        if msg == "success":
            return sign_url, key
        else:
            return None, None  # Si no es success, retornar None

    except requests.exceptions.JSONDecodeError:
        return None, None  # Si hay un error en la respuesta, retornar None

        #os.environ["JWT_TOKEN"] = token_obtenido
        #os.environ["EMAIL"] = correo
        #os.environ["PASS"] = password



def ups(archivo_path):
    filename = os.path.basename(archivo_path) 
    # Solicitar datos al usuario
    authorization_token = os.environ.get("JWT_TOKEN")
    #print(filename)
    # Subir el archivo y obtener la URL firmada y la clave
    sign_url, key = subir_archivo(authorization_token, filename)

    if sign_url and key:
        print(f"Subida exitosa.")
        #print(f"Clave: {key}")
        os.environ["FULL_PATH"] = key

        # Ruta del archivo y URL firmada
        url = sign_url
        # Llamada a la función para subir la imagen
        resultado = subir_imagen(archivo_path, url)
        #print(resultado)
    else:
        print("Error: No se pudo obtener la URL firmada o la clave.")
