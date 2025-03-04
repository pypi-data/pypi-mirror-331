import json, bson, requests, base64, math, os
import imghdr
import pandas as pd
from bs4 import BeautifulSoup
from firebase_admin import storage
from django.http import JsonResponse, Http404
from django.utils import timezone
from django.core.management.color import no_style
from django.db import connection
from django.conf import settings


# *********************************************************************************
# Borra todos los registros de una tabla y reinicia los ID
def reset_model(model):
    model.objects.all().delete()
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), [model])
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)
    return

# Verificar si la tabla existe
def db_table_exists(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');")
        return cursor.fetchone()[0]


def null_safe_float_to_int(value):
    if pd.isnull(value):
        return None
    else:
        return int(value)

def null_safe_string(value):
    
    if pd.isnull(value):
        return None
    else:
        return str(value)


def success_json(mensaje=None, resp=None, url=None):

    data = {'result': 'ok'}

    if resp:
        data['resp'] = resp

    if url:
        data['url'] = url
        data['redirected'] = True
    else:
        data['redirected'] = False
        
    if mensaje:
        data['mensaje'] = mensaje

    return JsonResponse(data)

def bad_json(mensaje=None, error=None, form=None, extradata=None):
    data = {'result': 'error'}
    if mensaje:
        data['mensaje'] = mensaje
    try:
        if error:
            if error >= 0:
                if error == 0:
                    data['mensaje'] = "Solicitud incorrecta"
                elif error == 1:
                    data['mensaje'] = "Error al guardar los datos"
                elif error == 2:
                    data['mensaje'] = "Error al eliminar los datos"
        if extradata:
            data.update(extradata)
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse(data)
    
def error_json(mensaje=None, error=None, forms=[], extradata=None):
    data = {'result': 'error'}
    if mensaje:
        data['mensaje'] = mensaje
    try:
        if error and error >= 0:
            if error == 0:
                data['mensaje'] = "Solicitud incorrecta"
            elif error == 1:
                data['mensaje'] = "Error al guardar los datos"
            elif error == 2:
                data['mensaje'] = "Error al eliminar los datos"
        if extradata:
            data.update(extradata)

        if forms:
            errors = {}
            for form in forms:
                errors.update({field: list(errors) for field, errors in form.errors.items()})
            data['forms'] = errors
            
        return JsonResponse(data, status=400)
    except Exception as ex:
        return JsonResponse(data, status=400)
    

def get_query_params(request):
    
    if request.method == 'GET':
        action = request.GET.get('action', '')
        data = request.GET.dict()
        if 'action' in data:
            del data['action']
        return action, data
    elif request.method == 'POST':
        action = ""
        try:
            data = json.loads(request.body)
            if 'action' in data:
                if 'action' in data:
                    action = data['action']
                else:
                    action == None
            if action == None or action == "":
                try:
                    action = request.GET.get('action', '')    
                except Exception as e:
                    action = ""
        except:
            data = request.POST.dict()
            pass
        
        if action == "" or action == None:
            action = request.POST.get('action', None)  
           
        return action, data

def get_hace_tiempo(created):
    
    ahora = timezone.now()
    diferencia = ahora - created
    segundos = round(diferencia.total_seconds())
    minutos = math.floor(segundos / 60)
    horas = math.floor(minutos / 60)
    dias = math.floor(horas / 24)
    meses = math.floor(dias / 30)

    if meses == 1:
        return "hace un mes"
    elif meses > 1:
        return f"hace {meses} meses"
    elif dias == 1:
        return f"hace {dias} día"
    elif dias > 0:
        return f"hace {dias} días"
    elif horas == 1:
        return f"hace {horas} hora"
    elif horas > 0:
        return f"hace {horas} horas"
    elif minutos == 1:
        return f"hace {minutos} minuto"
    elif minutos > 0:
        return f"hace {minutos} minutos"
    else:
        return f"hace {segundos} segundos"
    
def get_tiempo_string(tiempo):
    horas = tiempo // 3600
    tiempo = tiempo % 3600
    minutos = tiempo // 60
    tiempo = tiempo % 60
    segundos = tiempo
    
    if horas > 0 and minutos > 0 and segundos > 0:
        return f"{horas} horas {minutos} minutos {segundos} segundos"
    if horas > 0 and minutos > 0 and segundos == 0:
        return f"{horas} horas {minutos} minutos"
    if horas > 0 and minutos == 0 and segundos > 0:
        return f"{horas} horas {segundos} segundos"
    if horas > 0 and minutos == 0 and segundos == 0:
        return f"{horas} horas"
    if horas == 0 and minutos > 0 and segundos > 0:
        return f"{minutos} minutos {segundos} segundos"
    if horas == 0 and minutos > 0 and segundos == 0:
        return f"{minutos} minutos"
    else:
        return f"{segundos} segundos"
    
def get_seconds_to_string(seconds): # Convert seconds to 20:10
    
    if seconds >= 3600:
        hours = seconds // 3600
        seconds = seconds % 3600
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{hours}:{minutes}:{seconds}"
    else:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds}"
    
def check_is_superuser(request):
    if request.user.is_superuser:
        return
    else:
        raise Http404("Página no encontrada")

def get_url_params(request, exclude=['pagina']):
    url_parameters = request.GET.copy()
    
    for param in exclude:
        if param in url_parameters:
            del url_parameters[param]
    
    return url_parameters.urlencode() 


def upload_image_to_firebase_storage(image, bucket_name=settings.FIREBASE_BUCKET_NAME, folder=settings.TINYMCE_IMAGES_FOLDER):
    print("Estamos cargando la imagen Firebase desde Imagen")
    try:
        from firebase_admin import storage
        bucket = storage.bucket(bucket_name)
        tipo_archivo = imghdr.what(None, image.read())
        blob = bucket.blob(folder + "/" + str(bson.ObjectId()) + "." + tipo_archivo)
        image.seek(0)   # Pone el cursor al inicio del archivo
        content_type = image.content_type if hasattr(image, 'content_type') else "image/" + tipo_archivo

        blob.upload_from_file(image, content_type=content_type)
        blob.make_public()
        return blob.public_url
    except Exception as ex:
        print(ex)
        return None

    
def upload_url_image_to_firebase_storage(url, bucket_name=settings.FIREBASE_BUCKET_NAME, folder=settings.FIREBASE_IMAGES_FOLDER):
    print("Estamos cargando la imagen Firebase desde URL")
    try:
        from firebase_admin import storage
        bucket = storage.bucket(bucket_name)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.content
            tipo_archivo = imghdr.what(None, content)
            blob = bucket.blob(folder + "/" + str(bson.ObjectId()) + "." + tipo_archivo)
            blob.upload_from_string(response.content, content_type=response.headers['content-type'])
            blob.make_public()
            return blob.public_url
        else:
            print(f"Error al obtener la imagen: {response.status_code}")
            return None
    except Exception as ex:
        print(ex)
        return None
    


def replace_images(html, bucket_name=settings.FIREBASE_BUCKET_NAME, folder=settings.TINYMCE_IMAGES_FOLDER):
    # bucket = storage.bucket("pre-online.appspot.com")
    bucket = storage.bucket(bucket_name)

    soup = BeautifulSoup(html, 'html.parser')
    for img in soup.find_all('img'):
        imagen = img['src']

        if not imagen.startswith('data:image'):
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                       'Referer': 'https://quizizz.com/admin/quiz/636186fc7c0111001dd1c409/adjectives?fromSearch=true&source=',
                       'Sec-Ch-Ua-Mobile': '?0',
                       'Sec-Ch-Ua': '" Not A;Brand";v="99", "Chromium";v="121", "Google Chrome";v="121"',
                       'Sec-Ch-Ua-Platform': '"Windows"',
                       'Connection': 'keep-alive',
                       'Accept-Encoding': 'gzip, deflate, br',
                       'Accept': '*/*',
                       }
            response = requests.get(imagen, headers=headers)
            # https://quizizz.com/media/resource/gs/quizizz-media/quizzes/e3b75077-e64f-4dd6-b94d-aa8ac6cb8055?w=200&h=200
            # https://quizizz.com/_media/quizzes/e3b75077-e64f-4dd6-b94d-aa8ac6cb8055_200_200
            if response.status_code == 200:
                content = response.content
                tipo_archivo = imghdr.what(None, content)
                blob = bucket.blob(folder + "/" + str(bson.ObjectId()) + "." + tipo_archivo)
                blob.upload_from_string(response.content, content_type=response.headers['content-type'])
                blob.make_public()
                img['src'] = blob.public_url

                if "alt" in img.attrs:
                    img["alt"] = "Banco de preguntas"
                else:
                    img["alt"] = "Banco de preguntas"

        else :
            # Upload image to firebase storage
            imagen = imagen.replace('data:image/png;base64,', '')
            imagen = imagen.replace('data:image/jpeg;base64,', '')
            imagen = imagen.replace('data:image/jpg;base64,', '')
            imagen = imagen.replace('data:image/gif;base64,', '')
            imagen = imagen.replace('data:image/svg+xml;base64,', '')
            imagen = imagen.replace('data:image/webp;base64,', '')
            imagen = imagen.replace('data:image/bmp;base64,', '')
            imagen = imagen.replace('data:image/tiff;base64,', '')
            imagen = imagen.replace('data:image/vnd.microsoft.icon;base64,', '')
            imagen = imagen.replace('data:image/x-icon;base64,', '')
            imagen = imagen.replace('data:image/vnd.wap.wbmp;base64,', '')
            imagen = imagen.replace('data:image/x-xbitmap;base64,', '')
            imagen = imagen.replace('data:image/x-xbm;base64,', '')
            imagen = imagen.replace('data:image/x-win-bitmap;base64,', '')
            imagen = imagen.replace('data:image/x-windows-bmp;base64,', '')
            imagen = imagen.replace('data:image/x-ms-bmp;base64,', '')
            imagen = imagen.replace('data:image/bmp;base64,', '')
            imagen = imagen.replace('data:image/x-bmp;base64,', '')
            imagen = imagen.replace('data:image/x-bitmap;base64,', '')
            imagen = imagen.replace('data:image/x-xbitmap;base64,', '')
            imagen = imagen.replace('data:image/x-win-bitmap;base64,', '')

            imagen = imagen.encode('utf-8')
            imagen = base64.b64decode(imagen)

            blob = bucket.blob(folder + "/" + str(bson.ObjectId()))
            blob.upload_from_string(imagen, content_type="image/png")
            blob.make_public()
            img['src'] = blob.public_url

            if "alt" in img.attrs:
                img["alt"] = "Banco de preguntas"
            else:
                img["alt"] = "Banco de preguntas"

    return str(soup)


def eliminar_imagenes(sender, instance, imagen_fields, delete=False):
    if not delete:
        try:
            if instance.pk:
                antigua_instancia = sender.objects.get(pk=instance.pk)
                i = 0
                for field in imagen_fields:
                    antigua_imagen = getattr(antigua_instancia, field)
                    nueva_imagen = getattr(instance, field)
                    if antigua_imagen and nueva_imagen != antigua_imagen:
                        if os.path.isfile(antigua_imagen.path):
                            os.remove(antigua_imagen.path)
                    i += 1
                    if i > 50: # Evita un bucle infinito
                        break
        except Exception as ex:
            print(ex)
    else:
        try:
            i = 0
            for field in imagen_fields:
                imagen = getattr(instance, field)
                if imagen:
                    if os.path.isfile(imagen.path):
                        os.remove(imagen.path)
                i += 1
                if i > 50: # Evita un bucle infinito
                    break
        except Exception as ex:
            print(ex)


def eliminar_parrafos_vacios(html):
    soup = BeautifulSoup(html, 'html.parser')
    # while soup.p and not soup.p.text.strip():
    #     soup.p.extract()

    # while soup.p and (not soup.p.text.strip() and not soup.p.find_all(lambda tag: tag.name == 'img')):
    #     soup.p.extract()
    while soup.p and (not soup.p.text.strip() and not soup.p.find('img')):
        soup.p.extract()
    # while soup.p and not soup.find_all('p')[-1].text.strip():
    #     soup.find_all('p')[-1].extract()
    while soup.p and (not soup.find_all('p')[-1].text.strip() and not soup.find_all('p')[-1].find('img')):
        soup.find_all('p')[-1].extract()
    # Obtener el HTML resultante
    cleaned_html = str(soup)
    # Eliminar \n y \r al principio y al final
    cleaned_html = cleaned_html.lstrip('\n\r').rstrip('\n\r')

    if cleaned_html == "":
        cleaned_html = None
    return cleaned_html

def replace_quizziz_html(html):
    html = str(html)
    # html = html.replace('text-content-base', '')
    html = html.replace('font-medium', '')
    html = html.replace('font-semibold', 'fw-semibold')
    html = html.replace('font-bold', 'fw-bold')
    html = html.replace('font-light', 'fw-light')
    html = html.replace('font-regular', 'fw-regular')
    html = html.replace('font-italic', 'fs-italic')
    html = html.replace('font-normal', 'fs-normal')
    html = html.replace('font-small', 'fs-small')
    html = html.replace('font-medium', 'fs-medium')
    html = html.replace('font-large', 'fs-large')
    html = html.replace('font-xlarge', 'fs-xlarge')
    html = html.replace('color="dark.primary"', '')

    html = html.replace('<p class="fw-semibold"></p>', '')
    html = html.replace('<p></p>', '')
    html = html.replace('<!-- --><!-- --><!-- -->', '')
    html = html.replace('<!-- -->', '')

    soup = BeautifulSoup(html, 'html.parser')

    for tag in soup.find_all('p'):
    # Verificamos si tienen un atributo que comience con 'data-v-'
        for attr in list(tag.attrs):
            if attr.startswith('data-v-'):
                del tag[attr]

    for tag in soup.find_all('span'):
    # Verificamos si tienen un atributo que comience con 'data-v-'
        for attr in list(tag.attrs):
            if attr.startswith('data-v-'):
                del tag[attr]

    for tag in soup.find_all('div'):
    # Verificamos si tienen un atributo que comience con 'data-v-'
        for attr in list(tag.attrs):
            if attr.startswith('data-v-'):
                del tag[attr]

    # Encontrar un div con clase flex items-center w-full h-full image-preview cursor-zoom-in y eliminarlo
    # for tag in soup.find_all('div', {'class': 'flex items-center w-full h-full image-preview cursor-zoom-in'}):
    #     tag.extract()

    # Buscar todas las etiquetas <p>
    for p_tag in soup.find_all('p', class_=lambda x: x and 'text-content-base' in x):
        # Crear una nueva etiqueta <div> con los mismos atributos que el <p>
        div_tag = soup.new_tag('div')
        div_tag.attrs = p_tag.attrs  # Copiar los atributos del <p> al <div>
        
        # Clonar todos los elementos hijos, incluidos los <p> internos
        while p_tag.contents:
            div_tag.append(p_tag.contents[0])

        # Reemplazar el <p> con el <div>
        p_tag.replace_with(div_tag)

    html = str(soup)
    html = html.replace('text-content-base ', '')
    return html

def get_redirect_url(request, object=None):
    """
    Genera la URL de redirección según los parámetros del formulario.

    :param request: Objeto HttpRequest
    :param form: Instancia del formulario
    :return: String con la URL de redirección
    """
    try:
        if '_addanother' in request.POST:
            return f'{request.path}?action=add'
        elif '_continue' in request.POST:
            if object and hasattr(object, 'instance'):
                return f'{request.path}?action=edit&id={object.instance.pk}'
            else:
                return f'{request.path}?action=edit&id={object.pk}'
        return request.path
    except Exception as ex:
        print(ex)
        return request.path


