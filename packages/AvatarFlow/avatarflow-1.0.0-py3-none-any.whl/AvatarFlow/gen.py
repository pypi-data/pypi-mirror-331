#@title Generate avatar
import requests
import json
import os
import time


def obtener_tareas(token, page_size=10, page=1):
    contador_segundos=0
    url = f"https://app.jogg.ai/edge-service/aigc/task/page?type=2&page_size={page_size}&page={page}"

    headers = {
        "Authorization": token,
        "X-APP-ID": "52002",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-ES,es;q=0.9",
        "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
        "sec-ch-ua-mobile": "?0",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.jogg.ai/aigc-avatar/create",
        "Accept-Encoding": "gzip, deflate"
    }

    while True:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            #print("En Proceso...")
            contador_segundos += 10
            minutos = contador_segundos // 60
            segundos = contador_segundos % 60
            print(f"\r⏱️ Processing... Time elapsed: {minutos} minutes and {segundos} seconds", end='', flush=True)
            #print(data)

            tasks = data.get("data", [])
            if tasks:
                task = tasks[0]
                progress_desc = task.get("progress_desc", "").lower()
                err_msg = task.get("err_msg", "").strip()

                # Si hay un mensaje de error, salir del bucle y mostrarlo
                if err_msg:
                    print(f"\n❌ Error detectado: {err_msg}")
                    return None  # O lanzar una excepción con raise Exception(err_msg)

                # Si la tarea ha sido completada con éxito, devolver la URL
                if progress_desc == "success":
                    output_url = task.get("output_url", [])
                    if output_url and output_url[0]:  # Verifica que no esté vacío
                        return output_url[0]

        else:
            print(f"\n❌ Error en la solicitud. Código de estado: {response.status_code}")
            return None  # Detener ejecución si la solicitud falla

        time.sleep(10)  # Espera 10 segundos antes de la próxima solicitud


def descargar_video(url):
    if not url:
        print("No hay URL de video para descargar.")
        return
    
    # Crear carpeta si no existe
    output_dir = "/content/avatar"
    os.makedirs(output_dir, exist_ok=True)

    # Obtener el nombre del archivo desde la URL
    nombre_archivo = url.split("/")[-1]
    ruta_completa = os.path.join(output_dir, nombre_archivo)

    print(f"\nDescargando video desde...")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(ruta_completa, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        os.environ["VIDEO_AVATAR"] = ruta_completa
        print(f"✅ Video guardado")
    else:
        print(f"\n❌ Error al descargar el video. Código: {response.status_code}")




def enviar_peticion(photo_path, model, from_value, emotion, token):
    # URL del endpoint
    url = "https://app.jogg.ai/edge-service/aigc/motion"

    # Datos para la petición POST
    data = {
        "aspect_ratio": 1,
        "gesture": False,
        "photo_path": photo_path,
        "model": model,
        "from": from_value,
        "emotion": emotion
    }

    # Cabeceras HTTP, el token es ahora editable
    headers = {
        "Authorization": token,
        "X-APP-ID": "52002",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://app.jogg.ai",
        "Referer": "https://app.jogg.ai/aigc-avatar/create",
        "Accept-Language": "es-ES,es;q=0.9",
    }

    # Enviar la solicitud POST
    response = requests.post(url, headers=headers, json=data)

    # Verificar la respuesta
    if response.status_code == 200:
        # Procesar la respuesta
        response_json = response.json()
        if response_json.get("msg") == "success":
            print("La solicitud fue exitosa.")
            return True
        else:
            print("Error en la respuesta:", response_json)
            return False
    else:
        print(f"Error en la solicitud. Código de estado: {response.status_code}")
        return False


def agents(model, emotion):
    # Ejemplo de uso
    photo_path = os.environ.get("FULL_PATH")
    model
    from_value = 3
    emotion
    token = os.environ.get("JWT_TOKEN")

    # Llamada a la función
    valido = enviar_peticion(photo_path, model, from_value, emotion, token)
    if valido:
      print("La solicitud fue exitosa.")
      # Ejemplo de uso
      token = os.environ.get("JWT_TOKEN")
      output_url = obtener_tareas(token)

      if output_url:
          descargar_video(output_url)
      else:
          print("No se encontró ninguna URL de video.")
    else:
      print("Error en la solicitud")
