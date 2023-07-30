using System.Net;
using System.Net.Http;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;

public class Program {
    private const string BotName = "pokebot";
    private const string Host = "localhost";
    private const int Port = 50008;

    private static readonly HttpClient HttpClient = new HttpClient();

    private static async Task<string> GetPokemonInfo(string pokemon) {
        try {
            var responseBody = await HttpClient.GetStringAsync(
                $"https://pokeapi.co/api/v2/pokemon/{pokemon}");
            var data = JsonNode.Parse(responseBody)!;
            var heightNode = data!["height"];
            if (heightNode == null) {
                return "Der gik noget galt med indlæsningen af højden.";
            }
            var height = 10 * (int)heightNode;
            return $"En {pokemon} er gennemsnitligt {height} cm høj.";
        }
        catch (HttpRequestException) {
            return $"Pokemonen {pokemon} kunne ikke findes.";
        }
        catch (JsonException) {
            return "Der gik noget galt med indlæsningen af dataen.";
        }
    }

    private static async Task ConnectAndLoop(string host, int port) {
        var ipHostInfo = await Dns.GetHostEntryAsync(host);
        var ipAddress = ipHostInfo.AddressList[1];
        var ipEndPoint = new IPEndPoint(ipAddress, port);
        using var client = new Socket(
            ipEndPoint.AddressFamily,
            SocketType.Stream,
            ProtocolType.Tcp);
        try {
            await client.ConnectAsync(ipEndPoint);
            while (true) {
                // Receive message.
                var buffer = new byte[1024];
                var received = await client.ReceiveAsync(buffer, SocketFlags.None);
                var response = Encoding.UTF8.GetString(buffer, 0, received);
                var splitText = response.Split(": ", 2);
                var userName = splitText[0];
                var userMessage = splitText[1];
                if (userMessage.StartsWith($"{BotName}: ")) {
                    userMessage = userMessage.Substring(BotName.Length + 2);
                    Console.WriteLine($"Received message from \"{userName}\": \"{userMessage}\"");

                    // Interact with PokeAPI.
                    var pokeData = await GetPokemonInfo(userMessage);

                    // Send message.
                    var message = $"{BotName}: {userName}: {pokeData}";
                    var messageBytes = Encoding.UTF8.GetBytes(message);
                    _ = await client.SendAsync(messageBytes, SocketFlags.None);
                }
            }
        } catch (Exception) {
            client.Shutdown(SocketShutdown.Both);
        }
    }

    public static async Task Main() {
        await ConnectAndLoop(Host, Port);
    }
}
