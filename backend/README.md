# Chatbot Flask Universidad Javeriana

Este proyecto es un chatbot desarrollado con Flask que responde preguntas frecuentes sobre la Universidad Javeriana, usando una base de datos en JSON con preguntas y respuestas. Permite la normalización de texto para mejorar la búsqueda.

## Funcionamiento

- El chatbot recibe las preguntas del usuario vía una petición POST a la ruta `/chat`.
- Normaliza el texto para eliminar tildes y caracteres especiales, facilitando la comparación.
- Busca la mejor respuesta en la base de datos mediante tokens, considerando mínimos de palabras.
- Devuelve la respuesta personalizada y recomendaciones de preguntas relacionadas.
- Soporta usuarios autenticados con login, mostrando respuestas adicionales.

## Requerimientos

- Python 3.8 o superior
- Flask
- Librerías estándares: re, unicodedata, collections (incluidas en Python)

## Instalación

1. Clona el repositorio:  
   ```bash
   git clone https://github.com/tuusuario/chatbot-javeriana.git
   cd chatbot-javeriana
   ```

2. Crea y activa el entorno virtual (recomendado):  
   - Windows:  
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - Linux/macOS:  
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instala Flask:  
   ```bash
   pip install flask
   ```

## Uso

1. Ejecuta la aplicación Flask:  
   ```bash
   python app.py
   ```

2. Abre tu navegador y ve a [http://localhost:5000](http://localhost:5000).

3. Usa el chatbot desde la interfaz web o haciendo peticiones POST a `/chat` con JSON tipo:  
   ```json
   {
     "mensaje": "tu pregunta aquí"
   }
   ```

## Estructura del proyecto

- `app.py`: aplicación principal, rutas y lógica del chatbot.
- `faq.json`, `systems_engineering.json`: bases de datos de preguntas y respuestas.
- `templates/`: archivos HTML para la interfaz web.
- `static/`: recursos estáticos CSS, JS si los hay.

## Seguridad

- `app.secret_key` se usa para manejar sesiones seguras.
- Asegúrate de cambiar la clave por una segura en producción.

