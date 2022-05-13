using Delivery.Common.Models.AddressResolve;
using Delivery.PEK.Base;
using Delivery.PEK.Models;
using Microsoft.Extensions.Caching.Memory;

namespace Delivery.PEK.Services;

public class TownsRepository : ITownsRepository
{
    private readonly IPekTownsClient _client;
    private readonly PekRegionResolver _resolver;

    public TownsRepository(IPekTownsClient client, PekRegionResolver resolver)
    {
        _client = client;
        _resolver = resolver;
    }

    public async Task<IReadOnlyCollection<PekTown>> GetAll()
    {
        return await _client.GetTowns();
    }

    public async Task<PekRegion> GetTown(AddressShortModel address)
    {
        var allTowns = await GetAll();
        return await _resolver.Resolve(address, allTowns);
    }
}