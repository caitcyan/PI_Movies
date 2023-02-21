#Primero realizamos un pip install Deta, para manejar el drive. 
#Nos ubicamos en la carpeta donde tenemos nuestros archivos que queremos cargar.
from deta import Deta  # Import Deta
#Nos conectamos a Deta con nuestro data key.
deta = Deta("e0t3zaGELWHa_JjY9Bw5uJusD698dB1Qxqujkpo3h3SQy")
print(deta)
#Nos conectamos al drive creado
drive = deta.Drive("data")
#Con esto subimos el dataset data.csv
#drive.put('data.csv', path='./data.csv')
drive.put('new_data.csv', path='./new_data.csv')
#drive.put('data_aux.csv', path='./data_aux.csv')
#Realizamos un python upload_to_drive.py en nuestra terminal
