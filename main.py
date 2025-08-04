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

                    estado_actual = estado_usuarios.get(phone, "inicio")

                    if text == "menu":
                        estado_usuarios[phone] = "inicio"
                        send_text(phone, "👋 Menú principal:\n1️⃣ Ingresante\n2️⃣ Alumno\n(Escribí 1 o 2)")
                        continue

                    if estado_actual == "inicio":
                        if text == "1":
                            estado_usuarios[phone] = "menu_ingresante"
                            send_text(phone, "📚 Menú ingresantes:\n1. ¿Qué carreras dictan?\n2. ¿Qué documentación se debe entregar?\n3. ¿Cómo me inscribo?\n4. ¿Hay carreras virtuales?\n5. Me quiero pasar desde otra universidad\n6. Me inscribí hace años y quiero volver\nEscribí el número de opción o 'menu' para volver.")
                        elif text == "2":
                            estado_usuarios[phone] = "menu_alumno"
                            send_text(phone, "🎓 Menú alumnos:\n1. Quiero cambiarme de carrera\nEscribí el número de opción o 'menu' para volver.")
                        else:
                            send_text(phone, "👋 Menú principal:\n1️⃣ Ingresante\n2️⃣ Alumno\n(Escribí 1 o 2)")

                    elif estado_actual == "menu_ingresante":
                        if text == "1":
                            send_text(phone, "Hola, en San Antonio de Areco se encuentra:\n- Tecnicatura y Licenciatura en Administración\n- Tecnicatura en Producción agropecuaria\n- Ingeniería en zootecnia\n- Analista en Informática\n- Licenciatura en informática\n- Enfermería Universitaria\n\nHola, en Baradero se encuentra:\n- Tecnicatura y Licenciatura en Administración\n- Tecnicatura y Licenciatura en Gestión Ambiental\n- Tecnicatura en Mantenimiento Industrial\n- Analista en Informática\n- Licenciatura en Fonoaudiología")
                        elif text == "2":
                            send_text(phone, "Debe presentar el formulario de preinscripción, junto con fotocopia de DNI (copia y original para certificar), Certificado analítico del Nivel secundario (copia y original para certificar). En caso de no tenerlo aún debe presentar certificado de título en trámite o Constancia de alumno regular y foto 4x4")
                        elif text == "3":
                            send_text(phone, "Debe ingresar a nuestra página web www.unsada.edu.ar e ingresar a ingreso2026")
                        elif text == "4":
                            send_text(phone, "No, por el momento solo tenemos carreras en modalidad presencial.")
                        elif text == "5":
                            send_text(phone, "Primero debes inscribirte y completar la inscripción para figurar cómo alumno/a.\nUna vez que eres alumno regular de la UNSAdA debes iniciar un expediente de solicitud de materias por equivalencias. En nuestra página www.unsada.edu.ar se encuentra la normativa vigente. Debes ir a Estudiantes > Guía de trámites > Pases y Equivalencias, imprimir el formulario Anexo II, completar y adjuntar Analítico, Plan y Programas de las materias que desea solicitar.\nLe recomiendo leer la Resolución 96/2018 para que esté al tanto de los tiempos del trámite. En el calendario académico también encuentra las fechas en que se inicia dicho trámite.")
                        elif text == "6":
                            send_text(phone, "Si se inscribió anteriormente, no debe volver a completar la preinscripción. Corrobore acercándose a alguna de las sedes para verificar que figura como alumno/a. Luego, en la fecha que figura en el calendario académico para el trámite de Reinscripción a la propuesta, debe ingresar a Guaraní con su mail institucional y cliquear en el cartel ‘Reinscribirme a la propuesta’.\nSi no recuerda su mail institucional y/o contraseña, debe solicitarla al mail alumnos@unsada.edu.ar y le enviaremos un recordatorio.")
                        else:
                            send_text(phone, "❓ No entendí. Escribí un número del 1 al 6 o 'menu' para volver.")

                    elif estado_actual == "menu_alumno":
                        if text == "1":
                            send_text(phone, "Si ya figura cómo alumno de la universidad, lo que debe hacer es entregar la planilla de simultaneidad o cambio de carrera que puede descargar de la página web www.unsada.edu.ar")
                        else:
                            send_text(phone, "❓ No entendí. Escribí '1' o 'menu' para volver.")

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

