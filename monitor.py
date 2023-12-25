import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from main import main

class MyHandler(FileSystemEventHandler):
    # Dicionário para armazenar o último horário de modificação de cada arquivo
    last_modified_times: dict = {}  

    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Verifica se o evento é de modificação de arquivo
        if event.event_type == 'modified':
            file_path = event.src_path
            current_time = time.time()
            # Obtém o último horário de modificação do arquivo do dicionário, se existir
            last_modified_time = self.last_modified_times.get(file_path, 0)
            
            # Verifica se a modificação atual ocorreu dentro de um intervalo de 1 segundo da modificação anterior
            if current_time - last_modified_time > 1:
                print(f'Arquivo {file_path} foi modificado!')
                # Atualiza o último horário de modificação do arquivo no dicionário
                self.last_modified_times[file_path] = current_time
                main(file_path)

# Caminho para a pasta que você quer monitorar
with open('dir.txt') as arquivo:
    path = arquivo.read()

event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path, recursive=True)

print(f'Monitorando a pasta: {path}')
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()

observer.join()