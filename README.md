<div align="center">

![FaceGuard — reconocimiento facial local](assets/readme-banner.svg)

[![Python](https://img.shields.io/badge/Python-3.10%2B-00d9ff?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-YuNet_%2B_SFace-4cff91?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Local-31c7ff?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-9b7bff?style=for-the-badge)](LICENSE)

[![Tests](https://img.shields.io/github/actions/workflow/status/alejondr3/Reconocedor-de-caras/tests.yml?branch=main&style=flat-square&label=PIPELINE&logo=githubactions&logoColor=white)](https://github.com/alejondr3/Reconocedor-de-caras/actions)
![Last commit](https://img.shields.io/github/last-commit/alejondr3/Reconocedor-de-caras?style=flat-square&label=LAST%20PATCH&color=00d9a3)
![Repo size](https://img.shields.io/github/repo-size/alejondr3/Reconocedor-de-caras?style=flat-square&label=PAYLOAD&color=6f7dff)

### `> IDENTIFY // TRACK // RECORD // STAY LOCAL`

Reconocimiento facial en tiempo real para webcam, cámaras RTSP y archivos de
video. Procesa todo localmente, conserva los embeddings en SQLite y no depende
de servicios biométricos externos.

[Instalar](#-instalación-rápida) · [Usar cámara IP](#-cámara-de-seguridad-en-tiempo-real-y-grabación) · [Analizar videos](#-analizar-un-video-existente) · [Base SQLite](#-base-de-datos) · [Privacidad](#-privacidad-y-uso-responsable)

</div>

---

## ⚡ Capacidades

| Módulo | Función |
| --- | --- |
| `DETECT` | Detección facial YuNet para una o varias personas |
| `IDENTIFY` | Embeddings SFace y comparación local con SQLite |
| `LOW-QUALITY` | CLAHE, escalado, realce doble y memoria temporal |
| `LIVE` | Webcam y streams de cámaras de seguridad mediante RTSP |
| `VIDEO` | Análisis de MP4, AVI, MOV, MKV, M4V y WMV |
| `RECORD` | Exportación MP4 con nombres y rectángulos dibujados |
| `DATA` | Importación, respaldo y eliminación segura de SQLite |
| `PRIVACY` | Fotos, videos, modelos y bases excluidos de Git |

> [!NOTE]
> El sistema no entrena una red desde cero. Registra varias vistas de cada
> persona y las compara usando modelos preentrenados; esto es más práctico y
> preciso cuando no se dispone de miles de imágenes etiquetadas.

<div align="center">

![Secuencia de arranque de FaceGuard](assets/live-terminal.svg)

`LARP MODE: ENABLED` · `CLOUD EXFIL: 0` · `EDGE NODE: ARMED`

</div>

<details>
<summary><strong>▸ OPERATOR BRIEF // abrir panel táctico</strong></summary>

### Misión

Ingerir video desde una fuente local, detectar rostros, extraer vectores
biométricos y resolver identidades conocidas sin sacar el material del nodo.

### Threat model

- **Activo sensible:** fotografías, grabaciones, nombres y embeddings.
- **Superficie de ataque:** credenciales RTSP, archivos SQLite y acceso físico.
- **Postura:** procesamiento en el edge, mínimo privilegio y retención limitada.
- **Fail closed:** una similitud insuficiente termina como `Desconocido`, no como
  una identidad forzada.

### Reglas del operador

1. Nunca commitear el vault biométrico ni credenciales del uplink RTSP.
2. Crear un snapshot antes de importar o purgar la base.
3. Calibrar contra impostores, no solamente contra rostros conocidos.
4. Mantener supervisión humana en cualquier decisión relevante.

</details>

## ◈ Cámaras de baja calidad

- amplía cuadros pequeños con interpolación bicúbica;
- aplica CLAHE para compensar luz y contraste deficientes;
- descarta capturas de registro demasiado borrosas u oscuras;
- combina hasta las tres muestras más parecidas de cada persona;
- exige coincidencia durante varios cuadros antes de mostrar un nombre;
- permite bajar carga de CPU procesando embeddings cada varios cuadros.

Esto ayuda, pero ninguna técnica recupera detalle que la cámara nunca capturó.
Una cara de menos de ~55 píxeles, desenfoque fuerte, contraluz u oclusión puede
seguir sin ser reconocible.

## 🚀 Instalación rápida

> **Windows, sin consola:** descarga el ZIP, descomprímelo, ejecuta
> `instalar.bat` una sola vez y luego abre siempre con `iniciar.bat`.

## 🧩 Tutorial de instalación en Windows (sin consola)

### Requisitos

- Windows 10 u 11 de 64 bits.
- Python 3.10 o superior instalado desde
  [python.org](https://www.python.org/downloads/). Durante la instalación marca
  **Add Python to PATH**.
- Conexión a Internet únicamente durante la primera instalación.
- Una webcam, un video o una cámara IP con RTSP.

### Paso 1: descargar

1. En GitHub pulsa **Code** y después **Download ZIP**.
2. Descomprime el ZIP en una carpeta normal, por ejemplo el Escritorio.
3. No ejecutes el programa directamente dentro del ZIP.

### Paso 2: instalar

1. Abre la carpeta descomprimida.
2. Haz doble clic en `instalar.bat`.
3. Espera el mensaje **INSTALACIÓN COMPLETADA**. La descarga puede tardar varios
   minutos porque OpenCV y el modelo SFace son grandes.
4. Si Windows muestra una advertencia, verifica que el archivo pertenece a este
   repositorio antes de permitir su ejecución.

### Paso 3: abrir y registrar

1. Haz doble clic en `iniciar.bat`.
2. Escribe el nombre de la persona.
3. Deja `0` como cámara para usar la webcam principal.
4. Elige entre 20 y 40 fotografías y pulsa **Registrar persona**.
5. Mira al frente y gira lentamente la cabeza. Usa condiciones parecidas a las
   de la cámara final.
6. Repite el registro para cada participante autorizado.

### Paso 4: reconocer

Pulsa **Iniciar reconocimiento**. Un rectángulo verde muestra una persona
reconocida y uno rojo indica **Desconocido**. Pulsa **Detener cámara** antes de
cerrar o cambiar de fuente.

El botón **Crear respaldo** genera un ZIP con una copia consistente de
`faces.db` y todas las fotografías de `data/photos/`. El usuario elige dónde
guardarlo y no es necesario cerrar la aplicación.

El botón **Eliminar base de datos** pide dos confirmaciones, elimina todas las
identidades y embeddings y crea una base SQLite vacía. Las fotografías se
conservan en `data/photos/` para evitar borrarlas accidentalmente; se recomienda
crear un respaldo antes de usar esta opción.

El botón **Importar base SQLite** permite elegir otro archivo `.db`, `.sqlite` o
`.sqlite3` creado por este proyecto. La aplicación valida las tablas, combina
personas y embeddings y omite registros idénticos. Antes de modificar la base
activa crea automáticamente un respaldo en `data/backups/`. Las fotografías no
forman parte del archivo SQLite y deben copiarse por separado si se necesitan.

La ventana muestra la cámara en vivo, el avance de las fotografías y las
personas registradas. La primera instalación necesita conexión a Internet.

## 📡 Cámara de seguridad en tiempo real y grabación

La cámara debe ofrecer un stream **RTSP**. Muchas cámaras IP y DVR/NVR lo tienen,
pero algunas cámaras domésticas basadas únicamente en nube no lo permiten.

1. Conecta la computadora y la cámara a la misma red.
2. En la configuración de la cámara activa RTSP y crea un usuario exclusivo de
   solo lectura.
3. Busca la ruta RTSP en el manual del fabricante. Normalmente tiene esta forma:

   ```text
   rtsp://usuario:contraseña@192.168.1.50:554/ruta-del-stream
   ```

4. Prueba la URL en VLC con **Medio → Abrir ubicación de red**. Si VLC no puede
   verla, el reconocedor tampoco podrá hacerlo.
5. Abre `iniciar.bat`, pega la URL completa en **Cámara (0 o URL RTSP)** y activa
   **Grabar reconocimiento en video**.
6. Pulsa **Iniciar reconocimiento**. Al detener la cámara se cerrará el archivo
   correctamente.

Los videos con rectángulos y nombres quedan en:

```text
data/recordings/reconocimiento-AAAAmmdd-HHMMSS.mp4
```

Para cámaras de baja calidad usa el stream de mayor resolución durante el
registro. Si el equipo no logra procesarlo en tiempo real, prueba el substream
de la cámara. La cara debería medir al menos unos 55 píxeles. Evita contraluz,
ángulos extremos y movimiento rápido.

No escribas la URL RTSP en código, capturas o commits: normalmente contiene la
contraseña. Las grabaciones están excluidas de Git. Para operación continua se
recomienda limitar el espacio de disco y definir cuánto tiempo se conservarán.

## 🎞️ Analizar un video existente

La interfaz también reconoce personas en videos que ya estén guardados:

1. Abre `iniciar.bat` y pulsa **Elegir video**.
2. Selecciona un archivo MP4, AVI, MOV, MKV, M4V o WMV.
3. Activa **Grabar reconocimiento en video** si quieres conservar una copia con
   los nombres y rectángulos dibujados.
4. Pulsa **Iniciar reconocimiento**.
5. El análisis se detendrá automáticamente al llegar al final del archivo.

El video original nunca se modifica. Si se activó la grabación, el resultado se
guarda como un MP4 nuevo dentro de `data/recordings/`. Las personas deben estar
registradas previamente en la misma base SQLite.

## 🛠️ Instalación manual (usuarios técnicos)

Requiere Python 3.10 o superior:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
faceguard download-models
faceguard-gui
```

## ⌨️ Uso rápido por consola

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

## 🎯 Ajuste del umbral

El umbral predeterminado es `0.36` (similitud coseno). Si confunde personas,
súbelo, por ejemplo a `0.48`. Si rechaza demasiadas coincidencias verdaderas,
bájalo poco a poco, nunca sin evaluar falsos positivos:

```bash
faceguard recognize --threshold 0.48
```

Para un control de acceso, no uses reconocimiento facial como único factor:
combínalo con PIN, tarjeta o revisión humana. Calibra el umbral con imágenes de
las cámaras reales y con personas que no estén registradas.

### Calibración para cámaras de baja calidad

La interfaz activa por defecto **Modo cámara de baja calidad**. Este modo amplía
el cuadro a 1280 píxeles, mejora contraste, genera una segunda lectura con
realce de detalle y conserva temporalmente una identidad durante cuadros
borrosos. Consume más CPU.

Para obtener mejores resultados:

1. Registra nuevamente a cada persona usando la cámara de seguridad real o un
   video grabado por ella, no solamente una webcam de buena calidad.
2. Captura entre 40 y 60 fotos variando ángulo, distancia e iluminación.
3. Empieza con umbral `0.36`. Si rechaza caras conocidas, prueba `0.34`; si
   confunde personas diferentes, prueba `0.40` o `0.44`.
4. Mantén también personas no registradas en la prueba para medir falsos
   positivos. No bajes de `0.30`.
5. Acerca la cámara o usa mayor resolución si la cara ocupa menos de unos 55
   píxeles. El software no puede reconstruir detalles que nunca fueron captados.

## 🗄️ Base de datos

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

## 🧪 Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q
```

## 🛡️ Privacidad y uso responsable

Úsalo únicamente con consentimiento informado y una finalidad legítima. Avisa
cuando una cámara realiza identificación, limita quién accede a la base y
permite que una persona solicite la eliminación de sus datos. En una hackatón,
coloca un aviso visible y obtén permiso antes de fotografiar a cada participante.
No publiques el dataset ni lo reutilices para otra finalidad. Revisa las leyes
aplicables antes de desplegarlo en espacios públicos, trabajo, escuelas o para
tomar decisiones relevantes. Evalúa precisión y falsos positivos por separado
para las poblaciones y condiciones reales de uso.

## 🧬 Arquitectura del repositorio

```mermaid
flowchart LR
    A[Webcam / RTSP / Video] --> B[CLAHE + Upscale]
    B --> C[YuNet Detector]
    C --> D[SFace Embedding]
    D --> E[(SQLite Vector Vault)]
    E --> F{Cosine Threshold}
    F -->|match| G[Identidad conocida]
    F -->|reject| H[Desconocido]
    G --> I[Overlay + MP4]
    H --> I
```

```text
src/faceguard/     motor, base SQLite, calidad, CLI y voto temporal
tests/             pruebas unitarias sin cámara
models/            modelos descargados (ignorados por Git)
data/              base local (ignorada por Git)
```

<details>
<summary><strong>▸ DICCIONARIO LARPER // jerga del operador</strong></summary>

| Modismo | Traducción técnica |
| --- | --- |
| **Edge node** | La computadora que procesa el video localmente |
| **RTSP uplink** | Conexión de red con la cámara IP |
| **Biometric vault** | Archivo SQLite que contiene los embeddings |
| **Vector handshake** | Comparación por similitud coseno entre embeddings |
| **Unknown-class rejection** | Rechazar una cara cuando no supera el umbral |
| **Temporal lock** | Mantener una identidad durante varios cuadros coherentes |
| **Cold snapshot** | Respaldo de la base antes de una operación riesgosa |
| **Air-gapped capable** | Puede funcionar sin Internet después de descargar modelos |
| **Zero cloud telemetry** | El programa no envía rostros a un servicio biométrico cloud |
| **Purge protocol** | Eliminación confirmada de la base SQLite activa |

</details>

---

<div align="center">

`[ CAMERA ] → [ YUNET ] → [ SFACE ] → [ SQLITE ] → [ IDENTITY ]`

Construido para demostraciones responsables, procesamiento local y despliegues
donde la privacidad importa.

</div>


