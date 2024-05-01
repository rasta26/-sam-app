using Microsoft.Graph;
using Microsoft.Identity.Client;
using System;

namespace GraphApiConsoleApp
{
    public class GraphClientSingleton
    {
        private static GraphServiceClient _graphClient = null;
        private static readonly object padlock = new object();

        public static GraphServiceClient GetGraphClient(string clientId, string tenantId, string clientSecret)
        {
            if (_graphClient == null)
            {
                lock (padlock)
                {
                    if (_graphClient == null)
                    {
                        IConfidentialClientApplication confidentialClientApplication = ConfidentialClientApplicationBuilder
                            .Create(clientId)
                            .WithTenantId(tenantId)
                            .WithClientSecret(clientSecret)
                            .Build();

                        // Create an authentication provider by passing in a client application and graph scopes.
                        ClientCredentialProvider authProvider = new ClientCredentialProvider(confidentialClientApplication);

                        _graphClient = new GraphServiceClient(authProvider);
                    }
                }
            }

            return _graphClient;
        }
    }
}

