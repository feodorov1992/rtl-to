using Delivery.Common.Extensions;
using Delivery.PEK.Base;
using Delivery.PEK.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Serilog;

namespace Delivery.PEK.HttpClients;

public class PekTownsClient : IPekTownsClient
{
    private readonly HttpClient _client;
    private readonly PekTownsApi _api;

    public PekTownsClient(HttpClient client, PekTownsApi api)
    {
        _client = client;
        _api = api;
    }

    public async Task<IReadOnlyCollection<PekTown>> GetTowns()
    {
        var result = await _client.GetAsync($"{_api.Towns}");
        
        try
        {
            result.EnsureSuccessStatusCode();
        }
        catch (HttpRequestException e)
        {
            var contents = await result.Content.ReadAsStringAsync();
            Log.Error(e, contents);
            throw;
        }

        var response = await result.Content.ReadAsStringAsync();
        response = response.UnescapeUnicode();

        var towns = new List<PekTown>();
        
        var jObject = JsonConvert.DeserializeObject<JObject>(response);
        foreach (var propertyValue in jObject.Properties())
        {
            var regions = new List<PekRegion>();

            foreach (JProperty item in propertyValue.Values())
            {
                regions.Add(new PekRegion
                {
                    Id = Convert.ToInt32(item.Name),
                    Name = item.First?.ToString()
                });
            }

            towns.Add(new PekTown()
            {
                Name = propertyValue.Name,
                Regions = regions
            });
        }

        return towns;
    }
}