#!/usr/bin/env python3
"""Genera los SVG animados del perfil de GitHub de EvoShell.

Uso:  python scripts/generar_assets.py

Lee los datos de este archivo, los logos de scripts/iconos.json y las imágenes
fuente de assets/ (foto.png y certificados/), y escribe los SVG en assets/.
Las animaciones usan SMIL y CSS dentro del SVG, que GitHub reproduce cuando
muestra el archivo como imagen.

Los trazos de ECG son señal real: MIT-BIH Arrhythmia Database, registro 100,
derivación MLII (Moody GB, Mark RG. IEEE Eng Med Biol 2001;20(3):45-50),
publicada en PhysioNet bajo licencia ODC-BY 1.0. Ver scripts/ecg_mitbih_100.json.
"""
from __future__ import annotations

import base64
import io
import json
import random
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ASSETS = RAIZ / "assets"
ICONOS: dict[str, str] = json.loads((RAIZ / "scripts" / "iconos.json").read_text(encoding="utf-8"))
ECG = json.loads((RAIZ / "scripts" / "ecg_mitbih_100.json").read_text(encoding="utf-8"))

# ── Sistema visual ──────────────────────────────────────────────────────────
FONDO_A = "#060914"
FONDO_B = "#0E1430"
PANEL = "#0B1230"
CIAN = "#22D3EE"
VIOLETA = "#8B5CF6"
ROSA = "#F43F5E"
VERDE = "#34D399"
AMBAR = "#FBBF24"
TEXTO = "#E6EDF7"
TENUE = "#94A3B8"
LINEA = "#1E2945"
SANS = "'Segoe UI Variable Display','Segoe UI','Inter',system-ui,-apple-system,Helvetica,Arial,sans-serif"
MONO = "'Cascadia Code','JetBrains Mono','Fira Code',Consolas,'SF Mono',Menlo,monospace"

# ── Datos del perfil ────────────────────────────────────────────────────────
CORREO = "evos.sys@gmail.com"
LINKEDIN = "linkedin.com/in/darwin-burbano-10a158346"

FRASES_PORTADA = [
    "Backend y full stack en producción",
    "IA que prevé latidos de ECG",
    "Seguridad de aplicaciones web",
]

ETIQUETAS_PORTADA = [
    ("NestJS · PostgreSQL · AWS", CIAN),
    ("CNN-GRU · previsión de ECG", ROSA),
    ("OWASP · Google Cybersecurity", VERDE),
]

SECCIONES = {
    "sobre-mi": ("Sobre mí", "quién soy y qué construyo", "usuario"),
    "experiencia": ("Experiencia", "software empresarial en producción", "maletin"),
    "proyectos": ("Proyectos", "de la base de datos al modelo de IA", "cubo"),
    "stack": ("Stack tecnológico", "herramientas que uso a diario", "capas"),
    "certificaciones": ("Certificaciones", "credenciales verificables", "medalla"),
    "actividad": ("Actividad", "contribuciones en GitHub", "pulso"),
}

EXPERIENCIA = {
    "cargo": "Desarrollador full stack",
    "lugar": "Área de sistemas · distribuidora comercial · Nariño, Colombia",
    "resumen": "Diseño, construyo y opero el ERP web que reemplazó sistemas heredados y hojas de cálculo.",
    "stack": "TypeScript · NestJS 12 · React 19 · PostgreSQL 18 · Valkey 8 · AWS",
    "modulos": [
        ("Gestión comercial", "barras", CIAN, ["cuotas e impactos", "devoluciones", "alcance por rol"]),
        ("Proveedores", "documento", AMBAR, ["informes y planos", "ventas e inventario", "comprobantes en PDF"]),
        ("Terceros", "personas", VIOLETA, ["clientes y proveedores", "acreedores y personal", "catálogos contables"]),
        ("Bodega y distribución", "camion", VERDE, ["planilla y bitácora", "fletes y correrías", "pago a transportadores"]),
        ("Plataforma", "escudo", ROSA, ["usuarios y roles", "auditoría y monitoreo", "infraestructura AWS"]),
    ],
}

CIFRAS_ERP = [
    (13, "13", "módulos de negocio", "en una sola plataforma"),
    (1800, "1.800+", "pruebas automatizadas", "unitarias, integración y e2e"),
    (100, "100+", "migraciones SQL", "revisadas una por una"),
    (13, "13", "decisiones de arquitectura", "documentadas como ADR"),
]

# (nombre, icono o None, color sobre fondo oscuro, monograma si no hay icono)
STACK = [
    ("Backend", [
        ("TypeScript", "typescript", "#3178C6", None),
        ("Node.js", "nodedotjs", "#5FA04E", None),
        ("NestJS", "nestjs", "#E0234E", None),
        ("Fastify", "fastify", "#F8FAFC", None),
        ("Python", "python", "#4B8BBE", None),
        ("FastAPI", "fastapi", "#05A898", None),
        ("Zod", "zod", "#5B8DEF", None),
    ]),
    ("Frontend", [
        ("React", "react", "#61DAFB", None),
        ("Vite", "vite", "#8B92FF", None),
        ("TanStack", "reactquery", "#FF4154", None),
        ("Tailwind", "tailwindcss", "#06B6D4", None),
        ("shadcn/ui", "shadcnui", "#F8FAFC", None),
        ("JavaScript", "javascript", "#F7DF1E", None),
    ]),
    ("Datos e IA", [
        ("PostgreSQL", "postgresql", "#6E9BFF", None),
        ("Drizzle", "drizzle", "#C5F74F", None),
        ("Valkey", "redis", "#FF5A4E", None),
        ("TensorFlow", "tensorflow", "#FF6F00", None),
        ("scikit-learn", "scikitlearn", "#F7931E", None),
        ("Pandas", "pandas", "#F8FAFC", None),
        ("NumPy", "numpy", "#4DABCF", None),
        ("Matplotlib", None, "#5BA3D0", "MPL"),
        ("Jupyter", "jupyter", "#F37626", None),
    ]),
    ("Nube y DevOps", [
        ("AWS", None, "#FF9900", "AWS"),
        ("Docker", "docker", "#2496ED", None),
        ("nginx", "nginx", "#22C55E", None),
        ("Actions", "githubactions", "#2088FF", None),
        ("Turborepo", "turborepo", "#FF1E56", None),
        ("pnpm", "pnpm", "#F69220", None),
        ("Linux", "linux", "#FCC624", None),
        ("Bash", "gnubash", "#4EAA25", None),
        ("Git", "git", "#F05032", None),
    ]),
    ("Calidad y seguridad", [
        ("Vitest", "vitest", "#84CC16", None),
        ("Playwright", None, "#2EAD33", "PW"),
        ("OWASP", "owasp", "#F8FAFC", None),
        ("Kali Linux", "kalilinux", "#8FB4D0", None),
        ("Wireshark", "wireshark", "#4FB3E8", None),
        ("Metasploit", "metasploit", "#4FA8E0", None),
        ("Nmap", None, "#7FB2E5", "NM"),
    ]),
]

CERTIFICADOS = [
    {
        "archivo": "cert-google-ciberseguridad.svg",
        "imagen": "certificados/google-ciberseguridad.jpg",
        "forma": "horizontal",
        "titulo": "Ciberseguridad de Google",
        "lineas": ["Certificado profesional · 8 cursos", "Coursera · marzo de 2026"],
        "plataforma": "coursera",
    },
    {
        "archivo": "cert-cisco-ciberseguridad.svg",
        "imagen": "certificados/cisco-intro-ciberseguridad.png",
        "forma": "insignia",
        "titulo": "Introduction to Cybersecurity",
        "lineas": ["Cisco Networking Academy", "Insignia verificada en Credly"],
        "plataforma": "credly",
    },
    {
        "archivo": "cert-cisco-sistemas-operativos.svg",
        "imagen": "certificados/cisco-sistemas-operativos.png",
        "forma": "insignia",
        "titulo": "Operating Systems Basics",
        "lineas": ["Cisco Networking Academy", "Insignia verificada en Credly"],
        "plataforma": "credly",
    },
]

BOTONES = [
    ("btn-linkedin.svg", "linkedin", "#3B8FE8", "LinkedIn", "darwin-burbano"),
    ("btn-correo.svg", "gmail", "#EA4335", "Correo", CORREO),
    ("btn-huggingface.svg", "huggingface", "#FFD21E", "Hugging Face", "EvoShell"),
    ("btn-demo.svg", None, ROSA, "Demo en vivo", "ECG Forecasting"),
]


# ── Utilidades ──────────────────────────────────────────────────────────────
def attr(texto: str) -> str:
    return escape(texto, {'"': "&quot;"})


def documento(w: int, h: int, etiqueta: str, cuerpo: str, defs: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{attr(etiqueta)}">\n'
        f"<defs>{defs}</defs>\n{cuerpo}\n</svg>\n"
    )


def tarjeta(w: int, h: int, uid: str, rx: int = 20) -> tuple[str, str]:
    """Fondo de tarjeta con trama de puntos y borde de gradiente giratorio."""
    defs = f"""
<linearGradient id="fondo{uid}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{FONDO_A}"/><stop offset="1" stop-color="{FONDO_B}"/>
</linearGradient>
<linearGradient id="borde{uid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="0">
  <stop offset="0" stop-color="{CIAN}"/><stop offset=".5" stop-color="{VIOLETA}"/><stop offset="1" stop-color="{ROSA}"/>
  <animateTransform attributeName="gradientTransform" type="rotate" values="0 {w / 2} {h / 2};360 {w / 2} {h / 2}" dur="10s" repeatCount="indefinite"/>
</linearGradient>
<pattern id="puntos{uid}" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#24305A"/></pattern>"""
    cuerpo = f"""
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}" fill="url(#fondo{uid})"/>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}" fill="url(#puntos{uid})" opacity=".55"/>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="{rx}" fill="none" stroke="url(#borde{uid})" stroke-width="1.5" opacity=".8"/>"""
    return defs, cuerpo


def resplandor(uid: str, desv: float = 3) -> str:
    return f"""
<filter id="{uid}" x="-50%" y="-50%" width="200%" height="200%">
  <feGaussianBlur stdDeviation="{desv}" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>"""


def tecleo(n: int, inicio: float, duracion: float, retener: float | None = None, borrar: float = 0.5):
    """Instantes (t, caracteres visibles) de un texto que se teclea y, si se pide, se borra."""
    puntos = [(0.0, 0)]
    for i in range(1, n + 1):
        puntos.append((inicio + i * duracion / n, i))
    if retener is not None:
        t1 = inicio + duracion + retener
        for k, i in enumerate(range(n - 1, -1, -1), 1):
            puntos.append((t1 + k * borrar / n, i))
    return puntos


def discreto(puntos, total: float, valor) -> tuple[str, str]:
    assert all(t < total for t, _ in puntos), "la animación excede su ciclo"
    tiempos = ";".join(f"{t / total:.4f}" for t, _ in puntos)
    valores = ";".join(f"{valor(c):.1f}" for _, c in puntos)
    return tiempos, valores


def texto_tecleado(uid, x, y, texto, tam, ancho_car, color, puntos, total, peso="400", familia=MONO):
    w = len(texto) * ancho_car
    tiempos, valores = discreto(puntos, total, lambda c: c * ancho_car)
    clip = (
        f'<clipPath id="t{uid}"><rect x="{x}" y="{y - tam * 1.1:.1f}" height="{tam * 1.6:.1f}" width="0">'
        f'<animate attributeName="width" values="{valores}" keyTimes="{tiempos}" dur="{total}s" '
        f'calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>'
    )
    txt = (
        f'<text x="{x}" y="{y}" clip-path="url(#t{uid})" font-family="{MONO if familia == MONO else familia}" '
        f'font-size="{tam}" font-weight="{peso}" fill="{color}" textLength="{w:.1f}" '
        f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{escape(texto)}</text>'
    )
    return clip, txt


def aparecer(inicio: float, total: float | None = None, dur: float = 0.5) -> str:
    """Opacidad de 0 a 1. Con `total`, se repite en ciclos de esa duración."""
    if total is None:
        return (
            f'<animate attributeName="opacity" from="0" to="1" begin="{inicio}s" dur="{dur}s" fill="freeze"/>'
        )
    return (
        f'<animate attributeName="opacity" values="0;1" keyTimes="0;{inicio / total:.4f}" '
        f'dur="{total}s" calcMode="discrete" repeatCount="indefinite"/>'
    )


def icono(slug: str, x: float, y: float, tam: float, color: str) -> str:
    escala = tam / 24
    return (
        f'<path transform="translate({x:.1f} {y:.1f}) scale({escala:.4f})" '
        f'd="{ICONOS[slug]}" fill="{color}"/>'
    )


def _picos_r() -> list[float]:
    """Instantes (s) de los picos R: máximos locales por encima de 0,6 mV."""
    x, fs = ECG["muestras"], ECG["frecuencia_hz"]
    picos, i = [], 1
    while i < len(x) - 1:
        if x[i] > 0.6 and x[i] >= x[i - 1] and x[i] >= x[i + 1]:
            picos.append(i / fs)
            i += int(0.25 * fs)  # periodo refractario
        i += 1
    return picos


PICOS_R = _picos_r()


def reposo(n: int) -> float:
    """Instante en el segmento TP (línea de reposo) que sigue al latido n."""
    a, b = PICOS_R[n], PICOS_R[n + 1]
    return a + 0.68 * (b - a)


def _muestra(t: float, suavizado: int = 0) -> float:
    x, fs = ECG["muestras"], ECG["frecuencia_hz"]
    pos = t * fs
    i = min(max(int(pos), 0), len(x) - 2)
    f = pos - i
    if suavizado:
        def m(j: int) -> float:
            v = x[max(0, j - suavizado): j + suavizado + 1]
            return sum(v) / len(v)
        return m(i) * (1 - f) + m(i + 1) * f
    return x[i] * (1 - f) + x[i + 1] * f


def trazo_real(x0: float, x1: float, base: float, px_s: float, px_mv: float, t0: float,
               atenuar: float = 0, escala: float = 1.0, suavizado: int = 0) -> str:
    """Trazado de la señal real entre x0 y x1: `px_s` píxeles por segundo y `px_mv` por milivoltio.

    `atenuar` lleva la señal a la línea base en los extremos (en píxeles), para que empalme con otros trazos.
    `suavizado` y `escala` imitan la salida de un modelo de previsión.
    """
    pts = []
    x = x0
    while True:
        t = t0 + (x - x0) / px_s
        v = _muestra(t, suavizado) * escala
        if atenuar:
            d = min(x - x0, x1 - x) / atenuar
            if d < 1:
                v *= max(d, 0) ** 2 * (3 - 2 * max(d, 0))
        pts.append((x, base - v * px_mv))
        if x >= x1:
            break
        x = min(x + px_s / ECG["frecuencia_hz"], x1)  # un punto por muestra: no se pierden los picos R
    return "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in pts)


def imagen_b64(ruta: Path, ancho: int, formato: str) -> str:
    img = Image.open(ruta)
    if img.width > ancho:
        img = img.resize((ancho, round(img.height * ancho / img.width)), Image.LANCZOS)
    buf = io.BytesIO()
    if formato == "JPEG":
        img.convert("RGB").save(buf, "JPEG", quality=82, optimize=True)
        tipo = "jpeg"
    elif formato == "WEBP":
        img.convert("RGBA").save(buf, "WEBP", quality=86, method=6)
        tipo = "webp"
    else:
        img.save(buf, "PNG", optimize=True)
        tipo = "png"
    return f"data:image/{tipo};base64," + base64.b64encode(buf.getvalue()).decode()


# ── Portada ─────────────────────────────────────────────────────────────────
def portada() -> str:
    w, h = 1200, 520
    rnd = random.Random(7)
    defs, cuerpo = tarjeta(w, h, "p", rx=24)
    defs += resplandor("brillo", 4) + resplandor("brilloSuave", 2)
    defs += f"""
<radialGradient id="auroraV"><stop offset="0" stop-color="{VIOLETA}" stop-opacity=".55"/><stop offset="1" stop-color="{VIOLETA}" stop-opacity="0"/></radialGradient>
<radialGradient id="auroraC"><stop offset="0" stop-color="{CIAN}" stop-opacity=".35"/><stop offset="1" stop-color="{CIAN}" stop-opacity="0"/></radialGradient>
<radialGradient id="auroraR"><stop offset="0" stop-color="{ROSA}" stop-opacity=".30"/><stop offset="1" stop-color="{ROSA}" stop-opacity="0"/></radialGradient>
<linearGradient id="gradNombre" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="900" y2="0" spreadMethod="repeat">
  <stop offset="0" stop-color="{CIAN}"/><stop offset=".35" stop-color="{TEXTO}"/><stop offset=".65" stop-color="{VIOLETA}"/><stop offset="1" stop-color="{CIAN}"/>
  <animateTransform attributeName="gradientTransform" type="translate" values="0 0;900 0" dur="7s" repeatCount="indefinite"/>
</linearGradient>
<clipPath id="revelar"><rect x="56" y="90" height="200" width="0">
  <animate attributeName="width" values="0;780" dur="1.4s" begin=".3s" fill="freeze" calcMode="spline" keySplines=".2 .7 .2 1"/>
</rect></clipPath>
<clipPath id="marcoPortada"><rect x="1" y="1" width="1198" height="518" rx="24"/></clipPath>
<clipPath id="avatar"><circle cx="960" cy="225" r="104"/></clipPath>
<linearGradient id="anillo" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CIAN}"/><stop offset="1" stop-color="{VIOLETA}"/></linearGradient>
<radialGradient id="halo"><stop offset=".55" stop-color="{CIAN}" stop-opacity=".18"/><stop offset="1" stop-color="{CIAN}" stop-opacity="0"/></radialGradient>"""

    # Auroras en movimiento
    cuerpo += f"""
<g clip-path="url(#marcoPortada)">
  <ellipse cx="260" cy="130" rx="460" ry="220" fill="url(#auroraV)"><animateTransform attributeName="transform" type="translate" values="0 0;90 40;0 0" dur="16s" repeatCount="indefinite"/></ellipse>
  <ellipse cx="930" cy="400" rx="420" ry="200" fill="url(#auroraC)"><animateTransform attributeName="transform" type="translate" values="0 0;-110 -30;0 0" dur="19s" repeatCount="indefinite"/></ellipse>
  <ellipse cx="700" cy="40" rx="320" ry="160" fill="url(#auroraR)"><animateTransform attributeName="transform" type="translate" values="0 0;-60 50;0 0" dur="13s" repeatCount="indefinite"/></ellipse>
</g>"""

    # Estrellas
    estrellas = []
    for _ in range(80):
        x, y = rnd.uniform(20, w - 20), rnd.uniform(20, h - 20)
        r = rnd.choice([0.6, 0.8, 1.0, 1.3])
        d, b = rnd.uniform(2.2, 6.5), rnd.uniform(0, 5)
        estrellas.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff"><animate attributeName="opacity" '
            f'values=".15;.95;.15" dur="{d:.1f}s" begin="{b:.1f}s" repeatCount="indefinite"/></circle>'
        )
    cuerpo += "\n<g>" + "".join(estrellas) + "</g>"

    # Etiqueta de estado
    cuerpo += f"""
<g font-family="{MONO}" font-size="13" letter-spacing="2">
  <rect x="64" y="52" width="330" height="32" rx="16" fill="{CIAN}" fill-opacity=".07" stroke="{CIAN}" stroke-opacity=".45"/>
  <circle cx="84" cy="68" r="4.5" fill="{VERDE}"><animate attributeName="opacity" values="1;.25;1" dur="1.4s" repeatCount="indefinite"/></circle>
  <text x="98" y="73" fill="{CIAN}">EVOSHELL :: SISTEMA EN LÍNEA</text>
</g>"""

    # Nombre con brillo, revelado y glitch
    def nombre(relleno: str, extra: str = "") -> str:
        return (
            f'<g font-family="{SANS}" font-weight="800" font-size="96" letter-spacing="3" fill="{relleno}" {extra}>'
            f'<text x="60" y="180">DARWIN</text><text x="60" y="276">BURBANO</text></g>'
        )

    glitch = (
        'values="0;0;.85;0;.7;0;0" keyTimes="0;.86;.875;.89;.905;.92;1" dur="6s" begin="1.8s" repeatCount="indefinite"'
    )
    cuerpo += f"""
<g clip-path="url(#revelar)">
  {nombre("url(#gradNombre)", 'filter="url(#brillo)" opacity=".55"')}
  <g opacity="0" transform="translate(-5 0)">{nombre(CIAN)}<animate attributeName="opacity" {glitch}/></g>
  <g opacity="0" transform="translate(5 2)">{nombre(ROSA)}<animate attributeName="opacity" {glitch}/></g>
  {nombre("url(#gradNombre)")}
</g>"""

    # Frases que se teclean y se borran
    total, x0, y0, tam, ac = 15.0, 98, 330, 24, 13.6
    clips, textos, cursor_pts = [], [], [(0.0, 0)]
    for i, frase in enumerate(FRASES_PORTADA):
        pts = tecleo(len(frase), 1.0 + i * 5, 1.7, retener=1.8, borrar=0.45)
        clip, txt = texto_tecleado(f"f{i}", x0, y0, frase, tam, ac, TEXTO, pts, total)
        clips.append(clip)
        textos.append(txt)
        cursor_pts += pts[1:]
    cursor_pts.sort(key=lambda p: p[0])
    tiempos, valores = discreto(cursor_pts, total, lambda c: x0 + 4 + c * ac)
    defs += "".join(clips)
    cuerpo += f"""
<text x="64" y="{y0}" font-family="{MONO}" font-size="{tam}" font-weight="700" fill="{CIAN}">&gt;</text>
{''.join(textos)}
<g><rect x="{x0}" y="{y0 - 21}" width="12" height="26" rx="2" fill="{CIAN}">
  <animate attributeName="x" values="{valores}" keyTimes="{tiempos}" dur="{total}s" calcMode="discrete" repeatCount="indefinite"/>
</rect><animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></g>"""

    # Etiquetas
    x = 64
    for i, (texto, color) in enumerate(ETIQUETAS_PORTADA):
        ancho = len(texto) * 7.6 + 30
        cuerpo += f"""
<g opacity="0" transform="translate(0 8)">
  <rect x="{x}" y="362" width="{ancho:.0f}" height="32" rx="16" fill="{color}" fill-opacity=".09" stroke="{color}" stroke-opacity=".5"/>
  <text x="{x + 15}" y="383" font-family="{MONO}" font-size="13" fill="{color}" textLength="{len(texto) * 7.6:.0f}">{escape(texto)}</text>
  {aparecer(1.5 + i * 0.18)}
  <animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" begin="{1.5 + i * 0.18}s" dur=".5s" fill="freeze"/>
</g>"""
        x += ancho + 12

    # Avatar con anillos orbitales y pulsos de latido
    foto = imagen_b64(ASSETS / "foto.png", 240, "WEBP")
    cx, cy = 960, 225
    cuerpo += f"""
<circle cx="{cx}" cy="{cy}" r="200" fill="url(#halo)"/>
<circle cx="{cx}" cy="{cy}" r="110" fill="none" stroke="{ROSA}" stroke-width="2">
  <animate attributeName="r" values="110;190" dur="1.6s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values=".6;0" dur="1.6s" repeatCount="indefinite"/>
</circle>
<circle cx="{cx}" cy="{cy}" r="110" fill="none" stroke="{ROSA}" stroke-width="1.5">
  <animate attributeName="r" values="110;175" dur="1.6s" begin=".28s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values=".45;0" dur="1.6s" begin=".28s" repeatCount="indefinite"/>
</circle>
<g><circle cx="{cx}" cy="{cy}" r="128" fill="none" stroke="{CIAN}" stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="3 9"/>
  <animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" dur="26s" repeatCount="indefinite"/></g>
<g><circle cx="{cx}" cy="{cy}" r="146" fill="none" stroke="{VIOLETA}" stroke-width="3" stroke-linecap="round" stroke-dasharray="140 60 40 90 20 70"/>
  <animateTransform attributeName="transform" type="rotate" values="360 {cx} {cy};0 {cx} {cy}" dur="34s" repeatCount="indefinite"/></g>"""
    for radio, color, dur, desde in ((128, CIAN, 9, 0), (146, ROSA, 13, 120), (166, VERDE, 17, 240)):
        cuerpo += f"""
<g><circle cx="{cx + radio}" cy="{cy}" r="4.5" fill="{color}" filter="url(#brilloSuave)"/>
  <animateTransform attributeName="transform" type="rotate" values="{desde} {cx} {cy};{desde + 360} {cx} {cy}" dur="{dur}s" repeatCount="indefinite"/></g>"""
    cuerpo += f"""
<image href="{foto}" xlink:href="{foto}" x="{cx - 104}" y="{cy - 104}" width="208" height="208" clip-path="url(#avatar)"/>
<circle cx="{cx}" cy="{cy}" r="105" fill="none" stroke="url(#anillo)" stroke-width="3"/>"""

    # Monitor de ECG con barrido
    ruta = trazo_real(40, w - 40, 474, 150, 40, reposo(0), atenuar=30)
    cuerpo += f"""
<text x="48" y="506" font-family="{MONO}" font-size="11" letter-spacing="2" fill="{TENUE}">ECG REAL · MIT-BIH 100 · MLII</text>
<path d="{ruta}" fill="none" stroke="#2A3A66" stroke-width="1.6" stroke-linejoin="round"/>
<path id="ecgPortada" d="{ruta}" pathLength="1000" fill="none" stroke="{ROSA}" stroke-width="2.6" stroke-linejoin="round"
  stroke-linecap="round" stroke-dasharray="110 1890" filter="url(#brillo)">
  <animate attributeName="stroke-dashoffset" values="110;-1000" dur="4.2s" repeatCount="indefinite"/>
</path>
<circle r="5" fill="#fff" filter="url(#brillo)">
  <animateMotion dur="4.2s" repeatCount="indefinite" keyPoints="0;1;1" keyTimes="0;.9174;1" calcMode="linear">
    <mpath href="#ecgPortada" xlink:href="#ecgPortada"/>
  </animateMotion>
</circle>"""
    etiqueta = "Darwin Burbano, ingeniero de sistemas. Backend y full stack, inteligencia artificial aplicada a ECG y seguridad de aplicaciones."
    return documento(w, h, etiqueta, cuerpo, defs)


# ── Encabezados de sección ──────────────────────────────────────────────────
GLIFOS = {
    "usuario": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    "maletin": '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 13h18"/>',
    "cubo": '<path d="M12 2l9 5v10l-9 5-9-5V7z"/><path d="M3 7l9 5 9-5M12 12v10"/>',
    "capas": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/><path d="M3 17.5l9 5 9-5"/>',
    "medalla": '<circle cx="12" cy="9" r="6"/><path d="M8.5 14.2 7 22l5-3 5 3-1.5-7.8"/>',
    "pulso": '<path d="M2 12h4l3-8 5 16 3-8h5"/>',
    "barras": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "documento": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    "personas": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 2.9-6 6.5-6s6.5 2.4 6.5 6"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14.4c2.1.8 3.5 2.8 3.5 5.6"/>',
    "camion": '<path d="M2 6h12v10H2zM14 10h4l3 3v3h-7"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "escudo": '<path d="M12 2l8 3v6c0 5-3.4 9.3-8 11-4.6-1.7-8-6-8-11V5z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
}


def encabezado(clave: str) -> str:
    titulo, subtitulo, glifo = SECCIONES[clave]
    w, h = 1200, 112
    defs, cuerpo = tarjeta(w, h, "e", rx=18)
    defs += f"""
<linearGradient id="barrido" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{CIAN}" stop-opacity="0"/><stop offset=".5" stop-color="{CIAN}"/><stop offset="1" stop-color="{CIAN}" stop-opacity="0"/>
</linearGradient>"""
    ruta = f"~/{clave}"
    ancho_ruta = len(ruta) * 8.4
    cuerpo += f"""
<rect x="26" y="26" width="60" height="60" rx="16" fill="{PANEL}" stroke="url(#bordee)" stroke-width="1.5"/>
<g transform="translate(38 38) scale(1.5)" fill="none" stroke="{CIAN}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{GLIFOS[glifo]}</g>
<g opacity="0" transform="translate(-14 0)">
  <text x="108" y="58" font-family="{SANS}" font-size="31" font-weight="700" fill="{TEXTO}">{escape(titulo)}</text>
  <text x="110" y="84" font-family="{MONO}" font-size="14" fill="{TENUE}">// {escape(subtitulo)}</text>
  {aparecer(0.15)}
  <animateTransform attributeName="transform" type="translate" from="-14 0" to="0 0" begin=".15s" dur=".6s" fill="freeze"/>
</g>
<g font-family="{MONO}" font-size="14" text-anchor="end">
  <text x="{1150 - ancho_ruta - 10:.0f}" y="62" fill="{TENUE}">$ cd</text>
  <text x="1150" y="62" fill="{CIAN}" textLength="{ancho_ruta:.0f}">{escape(ruta)}</text>
</g>
<rect x="1156" y="48" width="9" height="18" rx="1.5" fill="{CIAN}"><animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>
<line x1="108" y1="98" x2="1174" y2="98" stroke="{LINEA}" stroke-width="1"/>
<rect x="108" y="97" width="180" height="2" fill="url(#barrido)">
  <animate attributeName="x" values="-180;1180" dur="3.6s" repeatCount="indefinite"/>
</rect>"""
    return documento(w, h, f"Sección: {titulo}", cuerpo, defs)


# ── Terminal "sobre mí" ─────────────────────────────────────────────────────
def terminal() -> str:
    w, h, total = 1200, 384, 18.0
    defs, cuerpo = tarjeta(w, h, "t", rx=18)
    cuerpo += f"""
<path d="M19 1h1162a18 18 0 0 1 18 18v25H1V19A18 18 0 0 1 19 1z" fill="#0F1733"/>
<circle cx="30" cy="22" r="6.5" fill="{ROSA}"/><circle cx="52" cy="22" r="6.5" fill="{AMBAR}"/><circle cx="74" cy="22" r="6.5" fill="{VERDE}"/>
<text x="600" y="27" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{TENUE}">darwin@evoshell: ~</text>"""
    tam, ac, x, y0, paso = 17, 10.2, 34, 88, 32

    def y(i: int) -> int:
        return y0 + i * paso

    def comando(i: int, texto: str, inicio: float, dur: float) -> None:
        nonlocal defs, cuerpo
        clip, txt = texto_tecleado(f"c{i}", x + 22, y(i), texto, tam, ac, TEXTO, tecleo(len(texto), inicio, dur), total)
        defs += clip
        cuerpo += f"""
<g opacity="0"><text x="{x}" y="{y(i)}" font-family="{MONO}" font-size="{tam}" font-weight="700" fill="{CIAN}">$</text>{aparecer(inicio - 0.25, total)}</g>
{txt}"""

    def salida(i: int, contenido: str, inicio: float) -> None:
        nonlocal cuerpo
        cuerpo += f"""
<g opacity="0"><text x="{x}" y="{y(i)}" font-family="{MONO}" font-size="{tam}" fill="{TENUE}" xml:space="preserve">{contenido}</text>{aparecer(inicio, total)}</g>"""

    def vineta(texto: str) -> str:
        return f'<tspan fill="{VIOLETA}">›</tspan> <tspan fill="{TEXTO}">{escape(texto)}</tspan>'

    comando(0, "whoami", 0.7, 0.6)
    salida(1, f'<tspan fill="{TEXTO}" font-weight="700">Darwin David Burbano Guerrero</tspan> · Ingeniero de Sistemas, Universidad CESMAG', 1.6)
    comando(2, "cat enfoque.txt", 2.4, 1.0)
    salida(3, vineta("Software empresarial de punta a punta: datos, API, interfaz, pruebas y nube"), 3.7)
    salida(4, vineta("IA aplicada a señales biomédicas: previsión de latidos de ECG"), 3.9)
    salida(5, vineta("Seguridad de aplicaciones: OWASP ASVS, RLS y auditoría"), 4.1)
    comando(6, "ubicacion --estado", 4.9, 1.1)
    salida(7, "San Juan de Pasto, Colombia · abierto a oportunidades y colaboraciones", 6.3)
    cuerpo += f"""
<g opacity="0"><text x="{x}" y="{y(8)}" font-family="{MONO}" font-size="{tam}" font-weight="700" fill="{CIAN}">$</text>
  <rect x="{x + 22}" y="{y(8) - 15}" width="10" height="20" fill="{CIAN}"><animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>
  {aparecer(6.8, total)}</g>"""

    # Panel lateral con la ficha técnica
    filas = [
        ("rol", "full stack · ML"),
        ("backend", "NestJS · FastAPI"),
        ("datos", "PostgreSQL 18"),
        ("ia", "TensorFlow"),
        ("nube", "AWS · Docker"),
        ("foco", "seguridad web"),
    ]
    px = 880
    panel = f"""
<line x1="{px - 24}" y1="70" x2="{px - 24}" y2="350" stroke="{LINEA}"/>
<text x="{px}" y="{y(0)}" font-family="{MONO}" font-size="17" font-weight="700" fill="{CIAN}">evoshell</text>
<line x1="{px}" y1="{y(0) + 10}" x2="{px + 84}" y2="{y(0) + 10}" stroke="{CIAN}" stroke-opacity=".5"/>"""
    for i, (clave, valor) in enumerate(filas):
        yy = y(1) + i * 30
        panel += (
            f'<text x="{px}" y="{yy}" font-family="{MONO}" font-size="15" xml:space="preserve">'
            f'<tspan fill="{VIOLETA}" font-weight="700">{clave:<8}</tspan><tspan fill="{TEXTO}">{escape(valor)}</tspan></text>'
        )
    for i, color in enumerate((ROSA, AMBAR, VERDE, CIAN, VIOLETA, "#60A5FA", TEXTO, TENUE)):
        panel += f'<rect x="{px + i * 34}" y="{y(8) - 16}" width="28" height="18" rx="4" fill="{color}"/>'
    cuerpo += f'\n<g opacity="0">{panel}{aparecer(1.6, total)}</g>'

    etiqueta = (
        "Terminal: Darwin David Burbano Guerrero, Ingeniero de Sistemas de la Universidad CESMAG. "
        "Software empresarial de punta a punta; IA aplicada a señales biomédicas; seguridad de aplicaciones. "
        "San Juan de Pasto, Colombia, abierto a oportunidades y colaboraciones."
    )
    return documento(w, h, etiqueta, cuerpo, defs)


# ── Experiencia ─────────────────────────────────────────────────────────────
def experiencia() -> str:
    w, h, ciclo = 1200, 452, 6.0
    e = EXPERIENCIA
    defs, cuerpo = tarjeta(w, h, "x", rx=20)
    defs += resplandor("brilloX", 3)
    defs += f"""
<linearGradient id="gradCargo" gradientUnits="userSpaceOnUse" x1="104" y1="0" x2="520" y2="0">
  <stop offset="0" stop-color="{TEXTO}"/><stop offset="1" stop-color="{CIAN}"/>
</linearGradient>"""
    cuerpo += f"""
<rect x="32" y="30" width="56" height="56" rx="15" fill="{PANEL}" stroke="url(#bordex)" stroke-width="1.5"/>
<g transform="translate(42 40) scale(1.5)" fill="none" stroke="{CIAN}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{GLIFOS["maletin"]}</g>
<text x="106" y="58" font-family="{SANS}" font-size="28" font-weight="800" fill="url(#gradCargo)">{escape(e["cargo"])}</text>
<text x="107" y="82" font-family="{MONO}" font-size="13" fill="{TENUE}">{escape(e["lugar"])}</text>
{chip_estado(w, "ACTUAL · EN PRODUCCIÓN", VERDE)}
<text x="34" y="128" font-family="{SANS}" font-size="17" fill="{TEXTO}" opacity=".9">{escape(e["resumen"])}</text>
<text x="34" y="172" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="2" fill="{CIAN}">MÓDULOS A MI CARGO</text>
<line x1="210" y1="168" x2="{w - 34}" y2="168" stroke="{LINEA}"/>"""

    n = len(e["modulos"])
    x0, gap, y = 32, 14, 222
    ancho = (w - 2 * x0 - (n - 1) * gap) / n
    alto = 178
    centros = [x0 + i * (ancho + gap) + ancho / 2 for i in range(n)]
    bus_y = 200
    viaje = 0.8  # fracción del ciclo que tarda el pulso en recorrer el bus

    cuerpo += f'<line x1="{centros[0]:.1f}" y1="{bus_y}" x2="{centros[-1]:.1f}" y2="{bus_y}" stroke="#2A3866" stroke-width="2"/>'
    for i, (nombre, glifo, color, lineas) in enumerate(e["modulos"]):
        x = x0 + i * (ancho + gap)
        cx = centros[i]
        t = viaje * i / (n - 1)
        if i:
            claves = f"0;{max(t - 0.02, 0):.3f};{t:.3f};{min(t + 0.12, 0.99):.3f};1"
            realce = ".35;.35;1;.35;.35"
        else:
            claves = "0;.12;1"
            realce = "1;.35;.35"
        entrada = 0.2 + i * 0.12
        texto_lineas = "".join(
            f'<text x="{x + 20:.1f}" y="{y + 122 + k * 21}" font-family="{MONO}" font-size="12.5" fill="{TENUE}">'
            f'<tspan fill="{color}">›</tspan> {escape(linea)}</text>'
            for k, linea in enumerate(lineas)
        )
        cuerpo += f"""
<line x1="{cx:.1f}" y1="{bus_y}" x2="{cx:.1f}" y2="{y}" stroke="#2A3866" stroke-width="2"/>
<circle cx="{cx:.1f}" cy="{bus_y}" r="5" fill="{FONDO_B}" stroke="{color}" stroke-width="2"/>
<g opacity="0" transform="translate(0 12)">
  <rect x="{x:.1f}" y="{y}" width="{ancho:.1f}" height="{alto}" rx="16" fill="{PANEL}"/>
  <rect x="{x:.1f}" y="{y}" width="{ancho:.1f}" height="{alto}" rx="16" fill="{color}" opacity=".05"/>
  <rect x="{x:.1f}" y="{y}" width="{ancho:.1f}" height="{alto}" rx="16" fill="none" stroke="{color}" stroke-width="1.5" stroke-opacity=".35">
    <animate attributeName="stroke-opacity" values="{realce}" keyTimes="{claves}" dur="{ciclo}s" begin="1s" repeatCount="indefinite"/>
  </rect>
  <rect x="{x + 20:.1f}" y="{y}" width="{ancho - 40:.1f}" height="3" rx="1.5" fill="{color}"/>
  <rect x="{x + 20:.1f}" y="{y + 22}" width="46" height="46" rx="13" fill="{color}" fill-opacity=".1" stroke="{color}" stroke-opacity=".45"/>
  <g transform="translate({x + 28:.1f} {y + 30}) scale(1.25)" fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{GLIFOS[glifo]}</g>
  <text x="{x + 20:.1f}" y="{y + 96}" font-family="{SANS}" font-size="16.5" font-weight="700" fill="{TEXTO}">{escape(nombre)}</text>
  {texto_lineas}
  {aparecer(entrada, dur=0.5)}
  <animateTransform attributeName="transform" type="translate" from="0 12" to="0 0" begin="{entrada:.2f}s" dur=".5s" fill="freeze"/>
</g>"""
    recorrido = centros[-1] - centros[0]
    mover = (
        f'<animateTransform attributeName="transform" type="translate" values="0 0;{recorrido:.1f} 0;{recorrido:.1f} 0" '
        f'keyTimes="0;{viaje};1" dur="{ciclo}s" begin="1s" repeatCount="indefinite"/>'
    )
    cuerpo += f"""
<g filter="url(#brilloX)">
  <rect x="{centros[0] - 60:.1f}" y="{bus_y - 1.5}" width="60" height="3" rx="1.5" fill="{CIAN}" opacity=".7">{mover}</rect>
  <circle cx="{centros[0]:.1f}" cy="{bus_y}" r="5" fill="#fff">{mover}</circle>
</g>
<text x="34" y="{h - 26}" font-family="{MONO}" font-size="12.5" fill="{TENUE}"><tspan fill="{VIOLETA}">stack</tspan>  {escape(e["stack"])}</text>"""
    etiqueta = (
        f"{e['cargo']}. {e['lugar']}. {e['resumen']} Módulos a mi cargo: "
        + "; ".join(f"{m[0]}: {', '.join(m[3])}" for m in e["modulos"])
        + f". Stack: {e['stack']}."
    )
    return documento(w, h, etiqueta, cuerpo, defs)


# ── Cifras del ERP ──────────────────────────────────────────────────────────
def miles(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def cifras() -> str:
    w, h, total = 1200, 240, 14.0
    defs, cuerpo = tarjeta(w, h, "c", rx=18)
    defs += f"""
<linearGradient id="gradCifras" gradientUnits="userSpaceOnUse" x1="60" y1="0" x2="1140" y2="0">
  <stop offset="0" stop-color="{CIAN}"/><stop offset=".35" stop-color="{VIOLETA}"/><stop offset=".7" stop-color="{ROSA}"/><stop offset="1" stop-color="{AMBAR}"/>
</linearGradient>"""
    cuerpo += f"""
<text x="32" y="40" font-family="{MONO}" font-size="13" fill="{TENUE}"><tspan fill="{CIAN}">erp</tspan>.cifras()  <tspan fill="{VERDE}">● en producción</tspan></text>"""
    for col, (valor, final, etiqueta, nota) in enumerate(CIFRAS_ERP):
        cx = 150 + col * 300
        if col:
            cuerpo += f'<line x1="{cx - 150}" y1="76" x2="{cx - 150}" y2="212" stroke="{LINEA}"/>'
        pasos = 10
        valores = [round(valor * k / pasos) for k in range(pasos)] + [None]
        inicio = 0.5 + col * 0.2
        for k, v in enumerate(valores):
            texto = final if v is None else miles(v)
            t = inicio + k * 0.09
            if k == 0:
                anim = f'values="1;0" keyTimes="0;{(t + 0.09) / total:.4f}"'
                op = "1"
            elif v is None:
                anim = f'values="0;1" keyTimes="0;{t / total:.4f}"'
                op = "0"
            else:
                anim = f'values="0;1;0" keyTimes="0;{t / total:.4f};{(t + 0.09) / total:.4f}"'
                op = "0"
            cuerpo += (
                f'<text x="{cx}" y="138" text-anchor="middle" font-family="{SANS}" font-size="60" font-weight="800" '
                f'fill="url(#gradCifras)" opacity="{op}">{texto}<animate attributeName="opacity" {anim} '
                f'dur="{total}s" calcMode="discrete" repeatCount="indefinite"/></text>'
            )
        cuerpo += f"""
<text x="{cx}" y="178" text-anchor="middle" font-family="{SANS}" font-size="18" font-weight="600" fill="{TEXTO}">{escape(etiqueta)}</text>
<text x="{cx}" y="203" text-anchor="middle" font-family="{MONO}" font-size="12.5" fill="{TENUE}">{escape(nota)}</text>"""
    resumen = "Cifras del ERP: " + "; ".join(f"{f} {e}" for _, f, e, _ in CIFRAS_ERP)
    return documento(w, h, resumen, cuerpo, defs)


# ── Tarjetas de proyecto ────────────────────────────────────────────────────
def chip_estado(w: int, texto: str, color: str) -> str:
    ancho = len(texto) * 8.3 + 46
    x = w - 28 - ancho
    return f"""
<rect x="{x:.0f}" y="30" width="{ancho:.0f}" height="30" rx="15" fill="{color}" fill-opacity=".1" stroke="{color}" stroke-opacity=".55"/>
<circle cx="{x + 18:.0f}" cy="45" r="4" fill="{color}"/>
<circle cx="{x + 18:.0f}" cy="45" r="4" fill="none" stroke="{color}">
  <animate attributeName="r" values="4;11" dur="1.6s" repeatCount="indefinite"/><animate attributeName="opacity" values=".8;0" dur="1.6s" repeatCount="indefinite"/>
</circle>
<text x="{x + 32:.0f}" y="50" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1" fill="{color}">{escape(texto)}</text>"""


def proyecto_erp() -> str:
    w, h = 590, 420
    defs, cuerpo = tarjeta(w, h, "r", rx=20)
    defs += resplandor("brilloR", 2.5)
    cuerpo += f"""
<text x="28" y="56" font-family="{SANS}" font-size="27" font-weight="800" fill="{TEXTO}">ERP empresarial</text>
<text x="28" y="80" font-family="{MONO}" font-size="12.5" fill="{TENUE}">monolito modular · TypeScript de punta a punta</text>
{chip_estado(w, "EN PRODUCCIÓN", VERDE)}"""
    nodos = [
        (24, 172, 96, 56, "Usuarios", "3 tipos"),
        (150, 172, 106, 56, "Web", "React 19"),
        (286, 172, 106, 56, "API", "NestJS 12"),
        (432, 106, 134, 48, "PostgreSQL", "18 · RLS"),
        (432, 176, 134, 48, "Valkey", "8 · caché"),
        (432, 246, 134, 48, "S3", "soportes PDF"),
    ]
    rutas = {
        "p": "M72 200 H404 C 418 200, 418 130, 499 130",
        "v": "M72 200 H499",
        "s": "M72 200 H404 C 418 200, 418 270, 499 270",
    }
    for clave, d in rutas.items():
        cuerpo += f'<path id="ruta{clave}" d="{d}" fill="none" stroke="#33416E" stroke-width="1.5" stroke-dasharray="4 5"><animate attributeName="stroke-dashoffset" values="18;0" dur=".8s" repeatCount="indefinite"/></path>'
    for i, clave in enumerate(rutas):
        for j, (color, ida) in enumerate(((CIAN, True), (VIOLETA, False))):
            puntos = 'keyPoints="0;1"' if ida else 'keyPoints="1;0"'
            cuerpo += (
                f'<circle r="4" fill="{color}" filter="url(#brilloR)"><animateMotion dur="2.6s" begin="{i * 0.45 + j * 1.3:.2f}s" '
                f'repeatCount="indefinite" {puntos} keyTimes="0;1" calcMode="linear"><mpath href="#ruta{clave}" xlink:href="#ruta{clave}"/></animateMotion></circle>'
            )
    for x, y, nw, nh, nombre, detalle in nodos:
        cuerpo += f"""
<rect x="{x}" y="{y}" width="{nw}" height="{nh}" rx="11" fill="#0F1838" stroke="#2C3B6B"/>
<text x="{x + nw / 2}" y="{y + nh / 2 - 3}" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="700" fill="{TEXTO}">{nombre}</text>
<text x="{x + nw / 2}" y="{y + nh / 2 + 14}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{TENUE}">{detalle}</text>"""
    modulos = [("Comercial", CIAN), ("Logística", VIOLETA), ("Finanzas", AMBAR), ("Seguridad", VERDE)]
    ancho = (w - 56 - 3 * 10) / 4
    for i, (nombre, color) in enumerate(modulos):
        x = 28 + i * (ancho + 10)
        cuerpo += f"""
<rect x="{x:.1f}" y="318" width="{ancho:.1f}" height="34" rx="10" fill="{color}" fill-opacity=".08" stroke="{color}" stroke-opacity=".35">
  <animate attributeName="stroke-opacity" values=".35;1;.35;.35" keyTimes="0;.1;.25;1" dur="4s" begin="{i}s" repeatCount="indefinite"/>
</rect>
<text x="{x + ancho / 2:.1f}" y="340" text-anchor="middle" font-family="{SANS}" font-size="14" font-weight="600" fill="{color}">{nombre}</text>"""
    cuerpo += f'<text x="28" y="390" font-family="{MONO}" font-size="12.5" fill="{TENUE}">13 módulos · permisos por rol · auditoría de cada cambio</text>'
    etiqueta = "Proyecto ERP empresarial en producción: usuarios, web en React 19, API en NestJS 12, PostgreSQL 18, Valkey 8 y S3. Módulos comercial, logística, finanzas y seguridad."
    return documento(w, h, etiqueta, cuerpo, defs)


def proyecto_ecg() -> str:
    w, h = 590, 420
    defs, cuerpo = tarjeta(w, h, "g", rx=20)
    defs += resplandor("brilloG", 2.5)
    defs += f"""
<pattern id="rejillaMonitor" width="14" height="14" patternUnits="userSpaceOnUse"><path d="M14 0H0V14" fill="none" stroke="#14204A" stroke-width=".8"/></pattern>
<clipPath id="monitor"><rect x="24" y="100" width="542" height="172" rx="12"/></clipPath>
<clipPath id="prevision"><rect x="350" y="100" height="172" width="0">
  <animate attributeName="width" values="0;0;216;216;0" keyTimes="0;.3;.6;.95;1" dur="6s" repeatCount="indefinite"/>
</rect></clipPath>
<linearGradient id="estela" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CIAN}" stop-opacity="0"/><stop offset="1" stop-color="{CIAN}" stop-opacity=".25"/></linearGradient>
<linearGradient id="gradMetrica" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CIAN}"/><stop offset="1" stop-color="{ROSA}"/></linearGradient>"""
    cuerpo += f"""
<text x="28" y="56" font-family="{SANS}" font-size="27" font-weight="800" fill="{TEXTO}">FORECASTING-ECG</text>
<text x="28" y="80" font-family="{MONO}" font-size="12.5" fill="{TENUE}">trabajo de grado · Universidad CESMAG</text>
{chip_estado(w, "DEMO EN VIVO", ROSA)}
<rect x="24" y="100" width="542" height="172" rx="12" fill="#070C1E"/>
<rect x="24" y="100" width="542" height="172" rx="12" fill="url(#rejillaMonitor)"/>
<rect x="24" y="100" width="542" height="172" rx="12" fill="none" stroke="#1E2A4A"/>
<text x="38" y="122" font-family="{MONO}" font-size="10.5" letter-spacing="1" fill="{CIAN}">HISTORIAL</text>
<text x="295" y="122" text-anchor="middle" font-family="{MONO}" font-size="10.5" letter-spacing="1" fill="{VIOLETA}">CNN-GRU + ATENCIÓN</text>
<text x="552" y="122" text-anchor="end" font-family="{MONO}" font-size="10.5" letter-spacing="1" fill="{ROSA}">PREVISIÓN <tspan fill="#64748B">· REAL</tspan></text>"""
    t0, px_s = reposo(10), 85
    t_prev = t0 + (350 - 34) / px_s
    historial = trazo_real(34, 246, 214, px_s, 60, t0, atenuar=10)
    real_futuro = trazo_real(350, 560, 214, px_s, 60, t_prev, atenuar=10)
    prevision = trazo_real(350, 560, 214, px_s, 60, t_prev, atenuar=10, escala=0.9, suavizado=1)
    cuerpo += f"""
<path d="{historial}" fill="none" stroke="{CIAN}" stroke-width="2" stroke-linejoin="round" filter="url(#brilloG)"/>
<path d="{real_futuro}" fill="none" stroke="#64748B" stroke-width="1.4" stroke-opacity=".7" stroke-linejoin="round"/>
<g clip-path="url(#prevision)"><path d="{prevision}" fill="none" stroke="{ROSA}" stroke-width="2" stroke-dasharray="5 4" stroke-linejoin="round" filter="url(#brilloG)"/></g>"""
    columnas = [(264, 3), (295, 4), (326, 3)]
    neuronas = []
    for cx, n in columnas:
        neuronas.append([(cx, 190 + (i - (n - 1) / 2) * 22) for i in range(n)])
    for a, b in zip(neuronas, neuronas[1:]):
        for p in a:
            for q in b:
                cuerpo += f'<line x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}" stroke="{VIOLETA}" stroke-opacity=".22"/>'
    for c, col in enumerate(neuronas):
        for p in col:
            cuerpo += (
                f'<circle cx="{p[0]}" cy="{p[1]}" r="5.5" fill="{VIOLETA}"><animate attributeName="opacity" '
                f'values=".3;1;.3" dur="1.2s" begin="{c * 0.2}s" repeatCount="indefinite"/></circle>'
            )
    cuerpo += f"""
<g clip-path="url(#monitor)">
  <rect x="-60" y="100" width="60" height="172" fill="url(#estela)"><animate attributeName="x" values="-36;566" dur="6s" repeatCount="indefinite"/></rect>
</g>"""
    metricas = [("0.6797", "R² · validación LOPO"), ("0.8429", "correlación de forma"), ("123", "registros MIT-BIH + INCART")]
    for i, (valor, texto) in enumerate(metricas):
        cx = 115 + i * 180
        cuerpo += f"""
<text x="{cx}" y="320" text-anchor="middle" font-family="{SANS}" font-size="30" font-weight="800" fill="url(#gradMetrica)">{valor}</text>
<text x="{cx}" y="342" text-anchor="middle" font-family="{MONO}" font-size="11.5" fill="{TENUE}">{texto}</text>"""
    cuerpo += f'<text x="28" y="390" font-family="{MONO}" font-size="12.5" fill="{TENUE}">TensorFlow · FastAPI · React · Docker · Hugging Face</text>'
    etiqueta = "Proyecto FORECASTING-ECG, trabajo de grado: a partir del historial de latidos, una red CNN-GRU con atención prevé los latidos siguientes. R² 0.6797, correlación de forma 0.8429, 123 registros."
    return documento(w, h, etiqueta, cuerpo, defs)


# ── Matriz de tecnologías ───────────────────────────────────────────────────
def stack() -> str:
    tw, th, gap, fila_h, x0, y0 = 98, 88, 10, 104, 196, 24
    w, h = 1200, y0 + len(STACK) * fila_h + 12
    defs, cuerpo = tarjeta(w, h, "s", rx=20)
    defs += f"""
<linearGradient id="destello" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".16"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>"""
    recortes, piezas, k = [], [], 0
    for f, (grupo, items) in enumerate(STACK):
        y = y0 + f * fila_h
        piezas.append(
            f'<text x="30" y="{y + 40}" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1" fill="{CIAN}">{escape(grupo.upper())}</text>'
            f'<text x="30" y="{y + 62}" font-family="{MONO}" font-size="12" fill="{TENUE}">{len(items)} herramientas</text>'
        )
        for c, (nombre, slug, color, mono) in enumerate(items):
            x = x0 + c * (tw + gap)
            recortes.append(f'<rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="14"/>')
            if slug:
                marca = icono(slug, x + tw / 2 - 16, y + 14, 32, color)
            else:
                marca = (
                    f'<text x="{x + tw / 2}" y="{y + 40}" text-anchor="middle" font-family="{SANS}" font-size="22" '
                    f'font-weight="800" fill="{color}">{mono}</text>'
                )
            tam = 12 if len(nombre) <= 11 else 11
            t = 0.15 + k * 0.035
            piezas.append(f"""
<g opacity="0" transform="translate(0 10)">
  <rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="14" fill="{PANEL}" stroke="#22305C"/>
  <rect x="{x + 18}" y="{y + th - 3}" width="{tw - 36}" height="2" rx="1" fill="{color}" opacity=".7"/>
  {marca}
  <text x="{x + tw / 2}" y="{y + 70}" text-anchor="middle" font-family="{SANS}" font-size="{tam}" font-weight="600" fill="{TEXTO}">{escape(nombre)}</text>
  {aparecer(t, dur=0.45)}
  <animateTransform attributeName="transform" type="translate" from="0 10" to="0 0" begin="{t:.2f}s" dur=".45s" fill="freeze"/>
</g>""")
            k += 1
    defs += f'<clipPath id="baldosas">{"".join(recortes)}</clipPath>'
    cuerpo += "".join(piezas)
    cuerpo += f"""
<g clip-path="url(#baldosas)">
  <rect x="-300" y="0" width="220" height="{h}" fill="url(#destello)" transform="skewX(-20)">
    <animate attributeName="x" values="-300;1500;1500" keyTimes="0;.4;1" dur="7s" begin="2s" repeatCount="indefinite"/>
  </rect>
</g>"""
    etiqueta = "Stack tecnológico. " + " ".join(
        f"{g}: " + ", ".join(n for n, *_ in items) + "." for g, items in STACK
    )
    return documento(w, h, etiqueta, cuerpo, defs)


# ── Certificados ────────────────────────────────────────────────────────────
def certificado(i: int, datos: dict) -> str:
    w, h = 380, 452
    uid = f"k{i}"
    defs, cuerpo = tarjeta(w, h, uid, rx=20)
    defs += f"""
<linearGradient id="holo{uid}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".35" stop-color="{CIAN}" stop-opacity=".18"/>
  <stop offset=".5" stop-color="#fff" stop-opacity=".28"/><stop offset=".65" stop-color="{VIOLETA}" stop-opacity=".18"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<clipPath id="recorte{uid}"><rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="20"/></clipPath>
<clipPath id="foto{uid}"><rect x="20" y="20" width="340" height="200" rx="12"/></clipPath>"""
    ruta = ASSETS / datos["imagen"]
    cuerpo += f'<rect x="20" y="20" width="340" height="200" rx="12" fill="#0A1028" stroke="#22305C"/>'
    if datos["forma"] == "horizontal":
        img = imagen_b64(ruta, 680, "JPEG")
        alto = 340 * Image.open(ruta).height / Image.open(ruta).width
        cuerpo += f'<image href="{img}" xlink:href="{img}" x="20" y="{20 + (200 - alto) / 2:.1f}" width="340" height="{alto:.1f}" clip-path="url(#foto{uid})"/>'
    else:
        img = imagen_b64(ruta, 340, "WEBP")
        cuerpo += f"""
<circle cx="190" cy="120" r="88" fill="{CIAN}" opacity=".07"/>
<g><image href="{img}" xlink:href="{img}" x="105" y="35" width="170" height="170"/>
  <animateTransform attributeName="transform" type="translate" values="0 0;0 -5;0 0" dur="4s" repeatCount="indefinite"/></g>"""
    titulo = datos["titulo"]
    cuerpo += f"""
<text x="24" y="262" font-family="{SANS}" font-size="20" font-weight="800" fill="{TEXTO}">{escape(titulo)}</text>
<text x="24" y="290" font-family="{MONO}" font-size="12.5" fill="{TENUE}">{escape(datos["lineas"][0])}</text>
<text x="24" y="311" font-family="{MONO}" font-size="12.5" fill="{TENUE}">{escape(datos["lineas"][1])}</text>
<rect x="24" y="334" width="134" height="30" rx="15" fill="{VERDE}" fill-opacity=".1" stroke="{VERDE}" stroke-opacity=".55"/>
<path d="M38 349l5 5 9-10" fill="none" stroke="{VERDE}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
<text x="60" y="354" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1" fill="{VERDE}">VERIFICABLE</text>
<line x1="24" y1="390" x2="356" y2="390" stroke="{LINEA}"/>
{icono(datos["plataforma"], 24, 406, 20, "#CBD5E1")}
<g><text x="54" y="421" font-family="{SANS}" font-size="14" font-weight="600" fill="{CIAN}">Ver credencial  →</text>
  <animateTransform attributeName="transform" type="translate" values="0 0;5 0;0 0" dur="1.6s" repeatCount="indefinite"/></g>
<g clip-path="url(#recorte{uid})">
  <rect x="-260" y="-40" width="180" height="{h + 80}" fill="url(#holo{uid})" transform="rotate(18 190 226)">
    <animate attributeName="x" values="-260;560;560" keyTimes="0;.45;1" dur="5s" begin="{1 + i * 0.6:.1f}s" repeatCount="indefinite"/>
  </rect>
</g>"""
    etiqueta = f"Certificado: {titulo}. {datos['lineas'][0]}. {datos['lineas'][1]}."
    return documento(w, h, etiqueta, cuerpo, defs)


# ── Botones de contacto ─────────────────────────────────────────────────────
def boton(slug: str | None, color: str, titulo: str, detalle: str) -> str:
    w, h = 270, 76
    defs = f"""
<linearGradient id="bb" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{w}" y2="0">
  <stop offset="0" stop-color="{color}"/><stop offset=".5" stop-color="{VIOLETA}"/><stop offset="1" stop-color="{CIAN}"/>
  <animateTransform attributeName="gradientTransform" type="rotate" values="0 {w / 2} {h / 2};360 {w / 2} {h / 2}" dur="6s" repeatCount="indefinite"/>
</linearGradient>"""
    if slug:
        marca = icono(slug, 22, 24, 28, color)
    else:
        marca = f'<path d="M20 38h6l4-11 6 22 4-11h8" fill="none" stroke="{color}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
    cuerpo = f"""
<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="18" fill="{PANEL}"/>
<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="18" fill="{color}" opacity=".06"/>
<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="18" fill="none" stroke="url(#bb)" stroke-width="2">
  <animate attributeName="stroke-opacity" values=".55;1;.55" dur="2.4s" repeatCount="indefinite"/>
</rect>
<circle cx="36" cy="38" r="24" fill="{color}" opacity=".12"/>
{marca}
<text x="72" y="35" font-family="{SANS}" font-size="18" font-weight="700" fill="{TEXTO}">{escape(titulo)}</text>
<text x="72" y="56" font-family="{MONO}" font-size="12" fill="{TENUE}">{escape(detalle)}</text>"""
    return documento(w, h, f"{titulo}: {detalle}", cuerpo, defs)


# ── Cierre ──────────────────────────────────────────────────────────────────
def cierre() -> str:
    w, h = 1200, 300
    defs, cuerpo = tarjeta(w, h, "z", rx=22)
    defs += resplandor("brilloZ", 3)
    defs += f"""
<linearGradient id="gradCierre" gradientUnits="userSpaceOnUse" x1="360" y1="0" x2="840" y2="0">
  <stop offset="0" stop-color="{CIAN}"/><stop offset=".5" stop-color="{VIOLETA}"/><stop offset="1" stop-color="{ROSA}"/>
</linearGradient>"""
    izquierda = trazo_real(60, 556, 160, 110, 40, reposo(20), atenuar=40)
    corazon = "M600 142 C 590 116, 550 118, 553 148 C 556 172, 588 186, 600 202 C 612 186, 644 172, 647 148 C 650 118, 610 116, 600 142 Z"
    derecha = trazo_real(644, 1140, 160, 110, 30, reposo(14), atenuar=40)
    cuerpo += f"""
<text x="600" y="78" text-anchor="middle" font-family="{SANS}" font-size="38" font-weight="800" fill="url(#gradCierre)">¿Construimos algo juntos?</text>
<path d="{izquierda} L556 160" pathLength="1" fill="none" stroke="{CIAN}" stroke-width="2.2" stroke-linejoin="round" stroke-dasharray="1" stroke-dashoffset="1" filter="url(#brilloZ)">
  <animate attributeName="stroke-dashoffset" values="1;0" dur="1.3s" begin=".3s" fill="freeze"/>
</path>
<g>
  <path d="{corazon}" pathLength="1" fill="{ROSA}" fill-opacity="0" stroke="{ROSA}" stroke-width="2.4" stroke-dasharray="1" stroke-dashoffset="1" filter="url(#brilloZ)">
    <animate attributeName="stroke-dashoffset" values="1;0" dur=".9s" begin="1.6s" fill="freeze"/>
    <animate attributeName="fill-opacity" values="0;.85" dur=".5s" begin="2.5s" fill="freeze"/>
  </path>
  <animateTransform attributeName="transform" type="translate" additive="sum" values="0 0;-72 -19.2;0 0;-48 -12.8;0 0;0 0" keyTimes="0;.1;.2;.3;.42;1"
    dur="1.6s" begin="3s" repeatCount="indefinite"/>
  <animateTransform attributeName="transform" type="scale" additive="sum" values="1;1.12;1;1.08;1;1" keyTimes="0;.1;.2;.3;.42;1"
    dur="1.6s" begin="3s" repeatCount="indefinite"/>
</g>
<path d="{derecha}" pathLength="1" fill="none" stroke="{VIOLETA}" stroke-width="2.2" stroke-dasharray="1" stroke-dashoffset="1" filter="url(#brilloZ)">
  <animate attributeName="stroke-dashoffset" values="1;0" dur="1s" begin="2.5s" fill="freeze"/>
</path>
<text x="600" y="248" text-anchor="middle" font-family="{SANS}" font-size="17" fill="{TEXTO}">Gracias por visitar mi perfil</text>
<text x="600" y="274" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{TENUE}">{CORREO}  ·  {LINKEDIN}</text>"""
    return documento(w, h, f"¿Construimos algo juntos? Gracias por visitar mi perfil. {CORREO}", cuerpo, defs)


# ── Escritura ───────────────────────────────────────────────────────────────
def main() -> None:
    salida = {
        "portada.svg": portada(),
        "terminal.svg": terminal(),
        "experiencia.svg": experiencia(),
        "erp-cifras.svg": cifras(),
        "proyecto-erp.svg": proyecto_erp(),
        "proyecto-ecg.svg": proyecto_ecg(),
        "stack.svg": stack(),
        "cierre.svg": cierre(),
    }
    for clave in SECCIONES:
        salida[f"seccion-{clave}.svg"] = encabezado(clave)
    for i, datos in enumerate(CERTIFICADOS):
        salida[datos["archivo"]] = certificado(i, datos)
    for archivo, slug, color, titulo, detalle in BOTONES:
        salida[archivo] = boton(slug, color, titulo, detalle)
    for nombre, contenido in salida.items():
        (ASSETS / nombre).write_text(contenido, encoding="utf-8")
        print(f"{nombre:38} {len(contenido.encode()) / 1024:7.1f} KB")


if __name__ == "__main__":
    main()
