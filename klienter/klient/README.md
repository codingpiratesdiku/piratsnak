# klient

Det her en klient skrevet i Python til at forbinde til en chatserver.

Du skal have Python installeret for at køre serveren.  [Hent det
her.](https://www.python.org/downloads/)


## Opsætning

Til at starte med skal hente nogle afhængigheder:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Du skal kun køre det ovenstående en enkelt gang.

Resten af tiden kan du nøjes med at køre:

```sh
. .venv/bin/activate
python klient.py
```

Hvis du vil forbinde til en speciel server (for eksempel din egen eller
en vens), kan du køre `python klient.py <adresse>`, for eksempel `python
klient.py localhost` hvis du kører en server selv, eller `python
klient.py 1.2.3.4` hvis du ved at der kører en server på IP-adressen
1.2.3.4.
