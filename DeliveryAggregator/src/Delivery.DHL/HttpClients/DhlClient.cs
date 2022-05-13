using System.Net;
using System.Net.Mime;
using System.Text;
using Delivery.DHL.Base;
using Delivery.DHL.Models;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using Serilog;

namespace Delivery.DHL.HttpClients;

public class DhlClient : IDhlClient
{
    private readonly HttpClient _client;
    private readonly DhlApi _api;

    public DhlClient(HttpClient client, DhlApi api)
    {
        _client = client;
        _api = api;
    }

    public async Task<AutoCompleteResponseModel> ResolveCity(AutoCompleteRequestModel request)
    {
        var requestJson = JsonConvert.SerializeObject(request, new JsonSerializerSettings
        {
            ContractResolver = new DefaultContractResolver
            {
                NamingStrategy = new SnakeCaseNamingStrategy()
            }
        });

        var requestContent = new StringContent(requestJson, Encoding.UTF8, MediaTypeNames.Application.Json);
        var result = await _client.PostAsync(_api.AutoComplete, requestContent);

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
        var responseObject = JsonConvert.DeserializeObject<AutoCompleteResponseModel>(response);
        
        if (responseObject == null)
            throw new HttpRequestException($"Failed to deserialize: {response}", null, HttpStatusCode.BadRequest);

        return responseObject;
    }

    public async Task<CalculatePriceResponseModel> Calculate(CalculatePriceRequestModel request)
    {
        var requestJson = JsonConvert.SerializeObject(request, new JsonSerializerSettings
        {
            ContractResolver = new DefaultContractResolver
            {
                NamingStrategy = new SnakeCaseNamingStrategy()
            }
        });

        var requestContent = new StringContent(requestJson, Encoding.UTF8, MediaTypeNames.Application.Json);
        var result = await _client.PostAsync(_api.Calculate, requestContent);

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
        var responseObject = JsonConvert.DeserializeObject<CalculatePriceResponseModel>(response, new JsonSerializerSettings
        {
            ContractResolver = new DefaultContractResolver
            {
                NamingStrategy = new SnakeCaseNamingStrategy()
            }
        });
        
        if (responseObject == null)
            throw new HttpRequestException($"Failed to deserialize: {response}", null, HttpStatusCode.BadRequest);

        return responseObject;
    }
}