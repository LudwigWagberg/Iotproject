För att kunna starta applikationen, måste du ladda ned python. Gå till följande url. 
När du installerar python tryck i boxen (Add python.exe to PATH)
<https://www.python.org/downloads/>

Öppna en cmd terminal och gå till det stället där du vill att projektet ska skapas och skriv sedan kommando nedan
git clone https://github.com/ciphercraftsman/IoTermometer

Gå sedan ned i mappen (IoTermometer) som du klonade, kommandot nedan för att byta mapp
cd IoTermometer

Skriv sedan kommandon nedan så att scripten ska kunna starta
pip install -r requierments.txt

För att applikationen ska fungera behöver du starta 3 python filer, följ instruktioner nedan för att stara dem

För att starta mqtt_client.py skriv kommando nedan
python mqtt_client.py

För att starta main.py skriv kommando nedan
uvicorn main:app --reload --port

För att starta webbapi.py skriv kommando nedan
uvicorn apiwebb:app --host 0.0.0.0 --port 8001

Ladda sedan ned mosquitto, gå till följande url
https://mosquitto.org/download/

gå sedan till det ställe dör du laddade ned mosquitto. 
