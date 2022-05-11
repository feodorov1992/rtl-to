using System.Net;
using Delivery.Common.Extensions;
using Delivery.PEK.Base;
using Delivery.PEK.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Serilog;

namespace Delivery.PEK.HttpClients;

public class PekCalcClient : IPekCalcClient
{
    private readonly HttpClient _client;
    private readonly PekCalcApi _api;

    public PekCalcClient(HttpClient client, PekCalcApi api)
    {
        _client = client;
        _api = api;
    }

    public async Task<PriceDeliveryResponseModel> Calculate(IReadOnlyList<PriceDeliveryRequestModel> packages, PekRegion from, PekRegion to)
    {
        var parameters = new List<KeyValuePair<string, object>>();

        for (int iPackage = 0; iPackage < packages.Count; iPackage++)
        {
            var package = packages[iPackage];
            parameters.Add(new($"places[{iPackage}][]", package.Width));
            parameters.Add(new($"places[{iPackage}][]", package.Length));
            parameters.Add(new($"places[{iPackage}][]", package.Height));
            parameters.Add(new($"places[{iPackage}][]", package.Width * package.Length * package.Height));
            parameters.Add(new($"places[{iPackage}][]", package.Weight));
        }
        
        parameters.Add(new("take[town]", from.Id));
        parameters.Add(new("deliver[town]", to.Id));

        var content = new FormUrlEncodedContent(parameters.Select(x => new KeyValuePair<string, string>(x.Key, x.Value.ToString())));
        
        var result = await _client.GetAsync($"{_api.Calculate}?{await content.ReadAsStringAsync()}");
        
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
        var responseObject = JsonConvert.DeserializeObject<PriceDeliveryResponseModel>(response);
        if (responseObject == null)
            throw new HttpRequestException($"Failed to deserialize: {response}", null, HttpStatusCode.BadRequest);

        return responseObject;
    }
}