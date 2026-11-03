# Reconocedor de caras

Aplicación local de reconocimiento facial en tiempo real. Usa **YuNet** para
detectar caras, **SFace** para convertirlas en embeddings y **SQLite** para
guardar las muestras. No entrena una red desde cero: registra varias vistas de
cada persona y las compara con un modelo preentrenado, que es la opción práctica
cuando no se dispone de miles de imágenes etiquetadas.

## Qué hace frente a cámaras de baja calidad

- amplía cuadros pequeños con interpolación bicúbica;
- aplica CLAHE para compensar luz y contraste deficientes;
- descarta capturas de registro demasiado borrosas u oscuras;
- combina hasta las tres muestras más parecidas de cada persona;
- exige coincidencia durante varios cuadros antes de mostrar un nombre;
- permite bajar carga de CPU procesando embeddings cada varios cuadros.

Esto ayuda, pero ninguna técnica recupera detalle que la cámara nunca capturó.
Una cara de menos de ~55 píxeles, desenfoque fuerte, contraluz u oclusión puede
seguir sin ser reconocible.

## Instalación

Requiere Python 3.10 o superior.

```bash
python -m venv .venv
```

En Windows:

```powershell
.venv\Scripts\Activate.ps1
pip install -e .
faceguard download-models
```

En Linux/macOS:

```bash
source .venv/bin/activate
pip install -e .
faceguard download-models
```

Los dos modelos ONNX se descargan del repositorio oficial de OpenCV Zoo. No se
incluyen en Git por su tamaño.

## Interfaz gráfica para Windows

No es necesario usar una consola. Después de descargar o descomprimir el
repositorio:

1. Haz doble clic en `instalar.bat` y espera a que termine.
2. Haz doble clic en `iniciar.bat` cada vez que quieras abrir el programa.
3. Escribe el nombre, selecciona la cámara y pulsa **Registrar persona**.
4. Pulsa **Iniciar reconocimiento** para comenzar la demostración.

El botón **Crear respaldo** genera un ZIP con una copia consistente de
`faces.db` y todas las fotografías de `data/photos/`. El usuario elige dónde
guardarlo y no es necesario cerrar la aplicación.

La ventana muestra la cámara en vivo, el avance de las fotografías y las
personas registradas. La primera instalación necesita conexión a Internet.

## Uso rápido

Registra una persona con 20 vistas tomadas desde la cámara predeterminada:

```bash
faceguard enroll --name "Ana"
```

Cada muestra aceptada también se guarda como fotografía recortada en
`data/photos/Ana/`. Así queda un dataset visible para la demostración y para
evaluaciones posteriores. La carpeta está excluida de Git porque contiene datos
biométricos reales.

Es importante variar suavemente la posición: frente, izquierda, derecha, un
poco arriba y abajo; repetir con la misma iluminación y distancia de la cámara
que se utilizarán en producción. Para una cámara mala conviene registrar 30–40
muestras válidas:

```bash
faceguard enroll --name "Ana" --samples 35 --min-quality 0.25
```

También se pueden usar fotos existentes:

```bash
faceguard enroll --name "Ana" --images "fotos/ana/*.jpg"
```

Para elegir otra ubicación para el dataset o registrar únicamente embeddings:

```bash
faceguard enroll --name "Ana" --photos-dir D:/dataset/rostros
faceguard enroll --name "Ana" --no-save-photos
```

Inicia el reconocimiento (pulsa `Q` o `Esc` para salir):

```bash
faceguard recognize
```

Una cámara USB diferente:

```bash
faceguard recognize --camera 1
```

Un stream RTSP:

```bash
faceguard recognize --camera "rtsp://usuario:clave@192.168.1.50/stream"
```

No guardes credenciales RTSP en scripts o commits. Usa variables de entorno o
un gestor de secretos en el despliegue real.

## Ajuste del umbral

El umbral predeterminado es `0.40` (similitud coseno). Si confunde personas,
súbelo, por ejemplo a `0.48`. Si rechaza demasiadas coincidencias verdaderas,
bájalo poco a poco, nunca sin evaluar falsos positivos:

```bash
faceguard recognize --threshold 0.48
```

Para un control de acceso, no uses reconocimiento facial como único factor:
combínalo con PIN, tarjeta o revisión humana. Calibra el umbral con imágenes de
las cámaras reales y con personas que no estén registradas.

## Base de datos

Por defecto se crea `data/faces.db`, que contiene nombres, embeddings biométricos
y puntajes de calidad. Las fotografías quedan separadas en `data/photos/`.
Ambas ubicaciones están ignoradas por Git. Comandos de administración:

```bash
faceguard list
faceguard delete --name "Ana"
```

Para elegir otra base:

```bash
faceguard recognize --database D:/datos/faces.db
```

Protege y cifra el disco donde se almacene: los embeddings son datos biométricos
sensibles. Define retención, copias de seguridad y eliminación de datos.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Privacidad y uso responsable

Úsalo únicamente con consentimiento informado y una finalidad legítima. Avisa
cuando una cámara realiza identificación, limita quién accede a la base y
permite que una persona solicite la eliminación de sus datos. En una hackatón,
coloca un aviso visible y obtén permiso antes de fotografiar a cada participante.
No publiques el dataset ni lo reutilices para otra finalidad. Revisa las leyes
aplicables antes de desplegarlo en espacios públicos, trabajo, escuelas o para
tomar decisiones relevantes. Evalúa precisión y falsos positivos por separado
para las poblaciones y condiciones reales de uso.

## Estructura

```text
src/faceguard/     motor, base SQLite, calidad, CLI y voto temporal
tests/             pruebas unitarias sin cámara
models/            modelos descargados (ignorados por Git)
data/              base local (ignorada por Git)
```


