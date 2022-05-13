using System.Net;
using System.Net.Http.Headers;
using System.Net.Mime;
using System.Text;
using Delivery.SDEK.Base;
using Delivery.SDEK.Models;
using Delivery.SDEK.Settings;
using Microsoft.Extensions.Options;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using Serilog;

namespace Delivery.SDEK.HttpClients;

public class SdekClient : ISdekClient
{
    private readonly HttpClient _client;
    private readonly SdekApi _api;
    private readonly ApiSettings _settings;

    public SdekClient(HttpClient client, SdekApi api, IOptions<ApiSettings> settings)
    {
        _client = client;
        _api = api;
        _settings = settings.Value;
    }

    private async Task Authenticate()
    {
        var parameters = new[]
        {
            new KeyValuePair<string, string>("grant_type", "client_credentials"),
            new KeyValuePair<string, string>("client_id", _settings.Account),
            new KeyValuePair<string, string>("client_secret", _settings.Password)
        };

        var requestContent = new FormUrlEncodedContent(parameters);

        var result = await _client.PostAsync(_api.Auth, requestContent);

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
        var responseObject = JsonConvert.DeserializeObject<AuthModel>(response, new JsonSerializerSettings
        {
            ContractResolver = new DefaultContractResolver
            {
                NamingStrategy = new SnakeCaseNamingStrategy()
            }
        });
        
        if (responseObject == null)
            throw new HttpRequestException($"Failed to deserialize: {response}", null, HttpStatusCode.BadRequest);

        _client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", responseObject.AccessToken);
    }

    public async Task<TariffListResponseModel> GetPrices(TariffListRequestModel request)
    {
        await Authenticate();

        var json = JsonConvert.SerializeObject(request, new JsonSerializerSettings
        {
            ContractResolver = new DefaultContractResolver
            {
                NamingStrategy = new SnakeCaseNamingStrategy()
            }
        });

        var content = new StringContent(json, Encoding.UTF8, MediaTypeNames.Application.Json);
        
        var result = await _client.PostAsync(_api.TariffList, content);
        
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
        var responseObject = JsonConvert.DeserializeObject<TariffListResponseModel>(response, new JsonSerializerSettings
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