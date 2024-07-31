using System;
using System.DirectoryServices;

namespace VPNCheckApp
{
    class Program
    {
        static void Main(string[] args)
        {
            if (!IsVpnConnected())
            {
                Console.WriteLine("You must be connected to the VPN to run this application.");
                return;
            }

            // Your application logic here
            Console.WriteLine("VPN is connected. Application is running.");
        }

        private static bool IsVpnConnected()
        {
            try
            {
                // Connect to the Global Catalog on port 3268
                using (DirectoryEntry entry = new DirectoryEntry("GC://yourdomain.com")) // Replace with your actual domain
                {
                    // Search for any object in the Global Catalog
                    using (DirectorySearcher searcher = new DirectorySearcher(entry))
                    {
                        searcher.Filter = "(objectClass=*)";
                        searcher.PageSize = 1; // We only need one result to confirm connection

                        SearchResultCollection results = searcher.FindAll();
                        return results.Count > 0;
                    }
                }
            }
            catch (Exception ex)
            {
                // Log exception if necessary
                Console.WriteLine($"Error checking VPN connection: {ex.Message}");
                return false;
            }
        }
    }
}
