using System.Net;
using Delivery.SDEK.Settings;
using Delivery.ZDE.Base;
using Delivery.ZDE.Models;
using Delivery.ZDE.Settings;
using Microsoft.Extensions.Options;
using Newtonsoft.Json;
using Serilog;

namespace Delivery.ZDE.HttpClients;

public class ZdeClient : IZdeClient
{
    private readonly HttpClient _client;
    private readonly ZdeApi _api;
    private readonly ApiSettings _apiSettings;

    public ZdeClient(HttpClient client, ZdeApi api, IOptions<ApiSettings> apiSettings)
    {
        _client = client;
        _api = api;
        _apiSettings = apiSettings.Value;
    }

    public async Task<PriceAddressResponseModel> GetPrice(PriceAddressRequestModel request)
    {
        var parameters = new Dictionary<string, object>
        {
            { "addr_from", request.From },
            { "addr_to", request.To },
            { "type", request.Type },
            { "weight", request.Weight },
            { "length", request.Length },
            { "width", request.Width },
            { "height", request.Height },
            { "quantity", request.Quantity },
            { "services", request.Services },
            { "user", _apiSettings.UserId },
            { "token", _apiSettings.ApiKey }
        };

        var content = new FormUrlEncodedContent(parameters.Where(x => x.Value is not null)
            .ToDictionary(k => k.Key, v => v.Value.ToString()));
        
        var result = await _client.GetAsync($"{_api.PriceAddress}?{await content.ReadAsStringAsync()}");

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
        var responseObject = JsonConvert.DeserializeObject<PriceAddressResponseModel>(response);
        if (responseObject == null)
            throw new HttpRequestException($"Failed to deserialize: {response}", null, HttpStatusCode.BadRequest);

        return responseObject;
    }
}