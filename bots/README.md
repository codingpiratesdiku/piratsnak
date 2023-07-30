# Bots

En bot er et program som man kan skrive til i chatten.  En bot kan for
eksempel hjælpe en med matematik eller finde information om Pokemon.

Man kan skrive en bot i et hvilket som helst programmeringssprog man har
lyst til, så længe det kan modtage og sende beskeder over internettet
via [TCP](https://en.wikipedia.org/wiki/Transmission_Control_Protocol).

Vi har lige nu bots i:

  - [Javascript](javascript)
  - [C#](csharp)

Klik på dem for at læse hvordan man sætter det op.


## Eksempel

I dette eksempel skriver `niels` sammen med to bots.

Til at starte med vil `niels` udregne 2 + 3. Det gør han ved at skrive `matbot 2 + 3`:

```
niels: matbot 2 + 3
```

Det regnestykke modtager `matbot` så, og svarer tilbage hvad resultatet er:

```
matbot: niels: 2 + 3 = 5
```

Bagefter vil `niels` spørge om noget information om en pokemon:

```
niels: pokebot pikachu
```

Det svarer `pokebot` tilbage på:

```
pokebot: niels: En pikachu er gennemsnitligt 40 cm høj.
```
