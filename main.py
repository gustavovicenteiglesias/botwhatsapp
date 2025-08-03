from fastapi import FastAPI, Request
import requests, os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
estado_usuarios = {}


@app.get("/webhook")
async def verify(request: Request):
    params = dict(request.query_params)
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == VERIFY_TOKEN:
        return int(params.get("hub.challenge"))
    return {"status": "error", "message": "Token inválido"}

@app.post("/webhook")
async def receive_message(payload: dict):
    try:
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages")
                if messages:
                    msg = messages[0]
                    phone = msg["from"]
                    text = msg["text"]["body"].strip().lower()

                    print(f"📩 Nuevo mensaje de {phone}: {text}")

                    # Verificar si el usuario está en el dict, si no, lo agregamos
                    estado_actual = estado_usuarios.get(phone, "inicio")

                    # Reset con la palabra 'menu'
                    if text == "menu":
                        estado_usuarios[phone] = "inicio"
                        send_text(phone,
                            "👋 ¡Volviste al menú principal!\n"
                            "Escribí:\n"
                            "1️⃣ si sos ingresante\n"
                            "2️⃣ si ya sos alumno")
                        continue

                    # Lógica según el estado
                    if estado_actual == "inicio":
                        if text == "1":
                            estado_usuarios[phone] = "submenu_ingresante"
                            send_text(phone,
                                "📝 Si sos ingresante, podés:\n"
                                "1. Ver fechas de inscripción\n"
                                "2. Ver documentación requerida\n"
                                "3. Consultar materias del primer cuatrimestre\n"
                                "Escribí 'menu' para volver al inicio.")
                        elif text == "2":
                            estado_usuarios[phone] = "submenu_alumno"
                            send_text(phone,
                                "🎓 Opciones para alumnos:\n"
                                "1. Consultar horarios\n"
                                "2. Solicitar certificado\n"
                                "3. Hablar con un asesor\n"
                                "Escribí 'menu' para volver al inicio.")
                        else:
                            send_text(phone,
                                "👋 ¡Hola! Bienvenido al canal de consultas.\n"
                                "Escribí:\n"
                                "1️⃣ si sos ingresante\n"
                                "2️⃣ si ya sos alumno")
                    elif estado_actual == "submenu_ingresante":
                        if text == "1":
                            send_text(phone, "📅 Fechas de inscripción: del 1 al 15 de marzo. Recordá subir tu documentación antes del cierre.")
                        elif text == "2":
                            send_text(phone, "🗂️ Documentación requerida: DNI, título secundario, foto 4x4, formulario de inscripción.")
                        elif text == "3":
                            send_text(phone, "📚 Materias del primer cuatrimestre: Introducción a la programación, Matemática I, Sistemas de información, Práctica profesional I.")
                        else:
                            send_text(phone, "❓ No entendí. Escribí '1', '2' o '3', o 'menu' para volver.")
                    elif estado_actual == "submenu_alumno":
                        if text == "1":
                            send_text(phone, "📆 Horarios de cursada: disponibles en https://unsada.edu.ar/horarios")
                        elif text == "2":
                            send_text(phone, "📄 Para solicitar certificados, escribí a alumnos@unsada.edu.ar o completá el formulario web.")
                        elif text == "3":
                            send_text(phone, "🧑‍💼 Un asesor se comunicará con vos a la brevedad. Si querés algo puntual, escribilo aquí.")
                        else:
                            send_text(phone, "❓ No entendí. Escribí '1', '2' o '3', o 'menu' para volver.")
        return {"status": "ok"}
    except Exception as e:
        print("❌ Error:", e)
        return {"status": "error", "message": str(e)}




def send_text(to: str, message: str):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    r = requests.post(url, headers=headers, json=data)
    print("➡️ Respuesta:", r.status_code, r.text)

