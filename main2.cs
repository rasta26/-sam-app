using Microsoft.Graph;
using System;
using System.Threading.Tasks;

class Program
{
    static async Task Main(string[] args)
    {
        var clientId = "{your-client-id}";
        var tenantId = "{your-tenant-id}";
        var clientSecret = "{your-client-secret}";
        string[] scopes = new string[] { "https://graph.microsoft.com/.default" };

        var authProvider = new CustomAuthenticationProvider(clientId, tenantId, clientSecret, scopes);
        
        // Initialize the GraphServiceClient with the custom authentication provider
        var graphClient = new GraphServiceClient(authProvider);

        // Example usage - Fetch users (adjust according to your needs, like listing devices)
        var users = await graphClient.Users
                                      .Request()
                                      .Select(u => new {
                                          u.DisplayName,
                                          u.Mail
                                      })
                                      .GetAsync();

        foreach (var user in users)
        {
            Console.WriteLine($"Name: {user.DisplayName}, Email: {user.Mail}");
        }
    }
}

