using Delivery.Common.Exceptions;
using Delivery.DHL.Base;
using Delivery.DHL.Models;

namespace Delivery.DHL.Services;

public class CityResolveService : ICityResolveService
{
    private readonly IDhlClient _client;

    public CityResolveService(IDhlClient client)
    {
        _client = client;
    }

    public async Task<string> GetCityId(string postalCode)
    {
        var request = new AutoCompleteRequestModel
        {
            CountryCode = "RU",
            MaxCount = 100,
            RequestedEntity = "zip",
            Language = "ru",
            SearchString = postalCode
        };

        var result = await _client.ResolveCity(request);
        if (result is null)
            return null;

        if (result.Errors?.Any() == true)
            throw new CounterpartyClientException(string.Join(Environment.NewLine, result.Errors.Select(x => x.Message)));

        var resolved = result.Success?.FirstOrDefault();
        if (resolved is null)
            return null;

        return resolved.CityName;
    }
}