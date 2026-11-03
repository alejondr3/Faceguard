<p align="center">
  <img src="assets/readme-banner.svg" width="100%" alt="FRG-05 — FaceGuard. Artefacto recuperado de reconocimiento facial local." />
  <img src="https://raw.githubusercontent.com/alejondr3/alejondr3/main/assets/visual-v3/signal.gif" width="100%" alt="LINK ESTABLISHED — AFTER HOURS / 001. Franja de señal animada." />
</p>

<p align="center"><samp>「 la cámara sigue mirando. la nube no. 」</samp></p>

<p align="center">
  <a href="#expediente">expediente</a> &nbsp; / &nbsp;
  <a href="#ritual-de-instalacion">ritual de instalación</a> &nbsp; / &nbsp;
  <a href="#fuentes-recuperadas">fuentes recuperadas</a> &nbsp; / &nbsp;
  <a href="#vault">vault</a> &nbsp; / &nbsp;
  <a href="#opsec">opsec</a>
</p>

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/alejondr3/Reconocedor-de-caras/tests.yml?branch=main&style=flat-square&label=BUILD&color=111111" alt="Estado del build" />
  <img src="https://img.shields.io/github/last-commit/alejondr3/Reconocedor-de-caras?style=flat-square&label=LAST%20SIGNAL&color=333333" alt="Último commit" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-111111?style=flat-square&logo=python&logoColor=white" alt="Python 3.10 o superior" />
  <img src="https://img.shields.io/badge/License-MIT-111111?style=flat-square" alt="Licencia MIT" />
</p>

<br />

<a id="expediente"></a>

### 01 / expediente recuperado

FaceGuard es un motor local de reconocimiento facial para webcam, cámaras IP y
videos. **YuNet** encuentra el rostro. **SFace** lo transforma en un vector.
**SQLite** conserva la memoria. Ningún servicio biométrico externo recibe las
imágenes.

| campo | registro |
| --- | --- |
| `artifact` | FRG-05 / Reconocedor de caras |
| `operator` | alejondr3 / night node 001 |
| `inputs` | webcam · RTSP · MP4 · AVI · MOV · MKV · WMV |
| `engine` | OpenCV YuNet + SFace |
| `memory` | SQLite vector vault |
| `output` | identidad · desconocido · grabación anotada |
| `cloud telemetry` | ninguna después de descargar los modelos |
| `status` | **STILL WATCHING** |

<p align="center"><img src="assets/live-terminal.svg" width="100%" alt="Registro nocturno animado del motor FaceGuard." /></p>

<details>
<summary><samp>[ RESTRICTED / abrir manifiesto de capacidades ]</samp></summary>

| protocolo | capacidad |
| --- | --- |
| `DETECT` | una o varias caras mediante YuNet |
| `IDENTIFY` | embeddings SFace comparados localmente |
| `LOW-QUALITY` | CLAHE, escalado, doble realce y memoria temporal |
| `LIVE-LINK` | webcam y cámaras de seguridad RTSP |
| `RECOVERED-FOOTAGE` | análisis de archivos de video existentes |
| `RECORD` | exportación MP4 con nombres y rectángulos |
| `VAULT` | importar, respaldar o purgar SQLite |
| `UNKNOWN-REJECT` | una similitud insuficiente queda como Desconocido |

</details>

<br />

<a id="ritual-de-instalacion"></a>

### 02 / ritual de instalación

#### Windows — sin invocar la terminal

1. Instala [Python 3.10 o superior](https://www.python.org/downloads/) y marca **Add Python to PATH**.
2. En GitHub pulsa **Code → Download ZIP**.
3. Descomprime el archivo. No ejecutes el proyecto dentro del ZIP.
4. Haz doble clic en `instalar.bat`.
5. Espera hasta ver **INSTALACIÓN COMPLETADA**.
6. Abre el sistema con `iniciar.bat`.

> La primera instalación necesita Internet para descargar OpenCV y los modelos
> ONNX. Después, el nodo puede operar sin conexión.

#### Primer registro

1. Escribe el nombre del participante autorizado.
2. Deja `0` como fuente para usar la webcam principal.
3. Mantén activo **Modo cámara de baja calidad**.
4. Selecciona entre 30 y 60 fotografías.
5. Pulsa **Registrar persona** y gira lentamente la cabeza.
6. Repite bajo la iluminación y distancia de la cámara definitiva.

```text
03:07  iniciando "solo voy a registrar una cara"
03:19  la cara ahora tiene 128 dimensiones
03:46  SQLite conoce mi perfil izquierdo
04:12  MATCH
04:13  no sé por qué la webcam me juzga
04:14  git commit
--:--  la sesión nunca se cerró
```

<br />

<a id="fuentes-recuperadas"></a>

### 03 / fuentes recuperadas

#### Cámara de seguridad / RTSP

La cámara debe ofrecer un stream RTSP. Actívalo desde la configuración del
fabricante y crea un usuario de solo lectura.

```text
rtsp://usuario:contraseña@192.168.1.50:554/ruta-del-stream
```

1. Conecta la computadora y la cámara a la misma red.
2. Prueba la URL en VLC con **Medio → Abrir ubicación de red**.
3. Pega la URL en **Cámara (0 o URL RTSP)**.
4. Activa **Grabar reconocimiento en video** si necesitas evidencia procesada.
5. Pulsa **Iniciar reconocimiento**.
6. Detén la cámara antes de cerrar para finalizar correctamente el MP4.

Las grabaciones aparecen en `data/recordings/`. No publiques una URL RTSP:
normalmente contiene credenciales reales.

#### Video existente

1. Pulsa **Elegir video**.
2. Selecciona MP4, AVI, MOV, MKV, M4V o WMV.
3. Activa la grabación si quieres una copia con las identidades dibujadas.
4. Pulsa **Iniciar reconocimiento**.

El original no cambia. El análisis termina automáticamente al llegar al último
cuadro.

<br />

### 04 / protocolo para imágenes que casi desaparecieron

El modo de baja calidad amplía el cuadro, aplica CLAHE, genera una segunda
lectura con realce de detalle y conserva temporalmente una identidad durante
cuadros borrosos. Ayuda con compresión, poca luz y cámaras antiguas; no puede
reconstruir información que nunca fue capturada.

1. Registra a cada persona usando la cámara final o un video producido por ella.
2. Captura 40–60 vistas con ángulos, luz y distancia diferentes.
3. Empieza con umbral `0.36`; prueba `0.34` si rechaza conocidos.
4. Si confunde personas, sube a `0.40` o `0.44`.
5. No bajes de `0.30` y prueba también con personas no registradas.
6. La cara debería medir al menos unos 55 píxeles.

> **UNKNOWN IS A VALID ANSWER.** Forzar siempre una identidad aumenta los falsos positivos.

<br />

<a id="vault"></a>

### 05 / biometric vault

La memoria activa vive en `data/faces.db`. Guarda nombres, embeddings y calidad;
las fotografías permanecen separadas en `data/photos/`. Todo está ignorado por Git.

| operación | efecto |
| --- | --- |
| **Importar base SQLite** | valida y combina personas y vectores compatibles |
| **Crear respaldo** | genera un ZIP con SQLite y fotografías |
| **Eliminar base de datos** | pide doble confirmación y crea una base vacía |
| **Actualizar lista** | vuelve a leer los expedientes registrados |

Antes de importar se crea un cold snapshot automático en `data/backups/`. Los
registros idénticos se omiten. Las fotografías no viajan dentro de SQLite.

<details>
<summary><samp>[ CLI ACCESS / comandos para operadores ]</samp></summary>

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .
faceguard download-models
faceguard enroll --name "Ana" --samples 40
faceguard recognize --camera 0 --threshold 0.36
faceguard list
faceguard delete --name "Ana"
```

Para una cámara IP:

```powershell
faceguard recognize --camera "rtsp://usuario:clave@192.168.1.50/stream"
```

</details>

<br />

<a id="opsec"></a>

### 06 / opsec notes

**Activos sensibles:** fotografías, videos, nombres, credenciales RTSP y
embeddings. Un embedding sigue siendo información biométrica aunque no sea una
foto directamente legible.

- Obtén consentimiento informado antes del registro.
- Señaliza cualquier cámara que realice identificación.
- Usa mínimo privilegio para cuentas RTSP.
- Cifra el disco y limita quién puede acceder a `data/`.
- Define cuánto tiempo conservar fotografías y grabaciones.
- Mantén revisión humana para decisiones relevantes.
- No uses reconocimiento facial como único factor de control de acceso.
- Evalúa falsos positivos con las personas y cámaras reales.

<details>
<summary><samp>[ LORE INDEX / diccionario de campo ]</samp></summary>

| término | significado civil |
| --- | --- |
| **edge node** | computadora que procesa el video localmente |
| **RTSP uplink** | enlace de red con una cámara IP |
| **biometric vault** | SQLite que conserva los embeddings |
| **vector handshake** | comparación por similitud coseno |
| **unknown rejection** | rechazar una cara que no supera el umbral |
| **temporal lock** | sostener una identidad durante cuadros coherentes |
| **cold snapshot** | respaldo antes de una operación riesgosa |
| **purge protocol** | eliminación confirmada de la base activa |
| **recovered footage** | video analizado después de grabarse |
| **air-gapped** | operación sin Internet tras descargar los modelos |

</details>

<br />

### 07 / mapa del artefacto

```mermaid
flowchart LR
    A[Webcam / RTSP / Video] --> B[CLAHE + Upscale]
    B --> C[YuNet Detector]
    C --> D[SFace / 128D]
    D --> E[(SQLite Vault)]
    E --> F{Cosine Threshold}
    F -->|match| G[Known Identity]
    F -->|reject| H[UNKNOWN]
    G --> I[Overlay + MP4]
    H --> I
```

```text
src/faceguard/     motor, interfaz, calidad, SQLite y CLI
tests/             pruebas unitarias sin cámara
assets/            artefactos visuales del expediente
models/            modelos ONNX ignorados por Git
data/              vault, fotos y grabaciones ignoradas por Git
```

#### Pruebas

```powershell
pip install -r requirements-dev.txt
pytest -q
```

<br />

<p align="center">
  <a href="https://github.com/alejondr3"><img src="https://raw.githubusercontent.com/alejondr3/alejondr3/main/assets/animated-v4/footer.gif" width="100%" alt="Fin de transmisión. La sesión nunca se cerró. STILL COMPILING." /></a>
</p>

<p align="center"><samp>FRG-05 // no cloud saw the face // end of recovered file</samp></p>

