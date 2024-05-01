using Microsoft.Graph;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace GraphApiConsoleApp
{
    public class VDIMachineManager
    {
        private GraphServiceClient _graphClient;

        public VDIMachineManager(GraphServiceClient graphClient)
        {
            _graphClient = graphClient;
        }

        public async Task<List<Device>> GetAllVDIMachinesAsync()
        {
            try
            {
                // Assuming VDI machines have a specific attribute or prefix you can filter on.
                // Adjust the filter accordingly.
                var devices = await _graphClient.Devices
                    .Request()
                    .Filter("startswith(displayName, 'VDI')")
                    .GetAsync();

                return devices.CurrentPage; // Note: Handling pagination is recommended for production code.
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error retrieving VDI machines: {ex.Message}");
                return new List<Device>();
            }
        }
    }
}

