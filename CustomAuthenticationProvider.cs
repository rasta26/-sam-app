using Microsoft.Graph;
using Microsoft.Identity.Client;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;

namespace GraphApiConsoleApp
{
    public class CustomAuthenticationProvider : IAuthenticationProvider
    {
        private IConfidentialClientApplication _clientApplication;
        private string[] _scopes;

        public CustomAuthenticationProvider(string clientId, string tenantId, string clientSecret, string[] scopes)
        {
            _clientApplication = ConfidentialClientApplicationBuilder.Create(clientId)
                .WithTenantId(tenantId)
                .WithClientSecret(clientSecret)
                .Build();

            _scopes = scopes;
        }

        public async Task AuthenticateRequestAsync(HttpRequestMessage request)
        {
            var authResult = await _clientApplication.AcquireTokenForClient(_scopes).ExecuteAsync();
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", authResult.AccessToken);
        }
    }
}

