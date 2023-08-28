# C#-bots

Sprog: [C#](https://learn.microsoft.com/en-us/dotnet/csharp/)

For at køre C#-bots skal du installere .NET.  [Hent det her.](https://dotnet.microsoft.com/en-us/download)

Du kan starte en bot ved at køre `dotnet run` i en terminal inde
fra dens mappe.  Eksempel:

```
cd pokebot
dotnet run
```

Hvis du vil forbinde til en speciel server (for eksempel din egen eller
en vens), kan du køre `dotnet run -- <adresse>`, for eksempel `dotnet
run -- localhost` hvis du kører en server selv, eller `dotnet run --
1.2.3.4` hvis du ved at der kører en server på IP-adressen 1.2.3.4.


## Liste over bots

| Bot | Beskrivelse |
| --- | ----------- |
| [`pokebot`](pokebot/Program.cs) | Henter information om en pokemon. |
