using Microsoft.Identity.Client;
using Newtonsoft.Json.Linq;
using System.IO;

namespace GraphApiConsoleApp
{
    class Program
    {
        static void Main(string[] args)
        {
            // Load the secrets
            var secrets = JObject.Parse(File.ReadAllText("secrets.json"));

            var clientId = secrets["clientId"].ToString();
            var tenantId = secrets["tenantId"].ToString();
            var clientSecret = secrets["clientSecret"].ToString();

            ConnectToGraph(clientId, tenantId, clientSecret);
        }

        static void ConnectToGraph(string clientId, string tenantId, string clientSecret)
        {
            IConfidentialClientApplication app = ConfidentialClientApplicationBuilder.Create(clientId)
                .WithClientSecret(clientSecret)
                .WithAuthority($"https://login.microsoftonline.com/{tenantId}")
                .Build();

            // Add scopes required for your application.
            string[] scopes = { "https://graph.microsoft.com/.default" };

            var authResult = app.AcquireTokenForClient(scopes).ExecuteAsync().Result;

            // Output the access token to verify the connection
            System.Console.WriteLine($"Access Token: {authResult.AccessToken}");
        }
    }
}

