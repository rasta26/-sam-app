using System;
using System.Threading.Tasks;

namespace GraphApiConsoleApp
{
    class Program
    {
        static async Task Main(string[] args)
        {
            // Load configuration from secrets.json (as shown previously)
            
            var clientId = "..."; // Loaded from secrets.json
            var tenantId = "..."; // Loaded from secrets.json
            var clientSecret = "..."; // Loaded from secrets.json
            
            // Use the singleton to get the GraphServiceClient
            var graphClient = GraphClientSingleton.GetGraphClient(clientId, tenantId, clientSecret);
            var vdiManager = new VDIMachineManager(graphClient);

            // Fetch and output details about VDI machines
            var vdiMachines = await vdiManager.GetAllVDIMachinesAsync();
            foreach (var device in vdiMachines)
            {
                Console.WriteLine($"Device ID: {device.Id}, Name: {device.DisplayName}");
            }
        }
    }
}
