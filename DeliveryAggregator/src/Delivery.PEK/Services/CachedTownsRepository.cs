using Delivery.Common.Models.AddressResolve;
using Delivery.PEK.Base;
using Delivery.PEK.Models;

namespace Delivery.PEK.Services;

public class CachedTownsRepository : ITownsRepository
{
    private readonly ITownsRepository _repository;
    private readonly PekRegionResolver _resolver;
    private IReadOnlyCollection<PekTown> _cached;

    public CachedTownsRepository(ITownsRepository repository, PekRegionResolver resolver)
    {
        _repository = repository;
        _resolver = resolver;
    }

    public async Task<IReadOnlyCollection<PekTown>> GetAll()
    {
        _cached ??= await _repository.GetAll();
        return _cached;
    }

    public async Task<PekRegion> GetTown(AddressShortModel address)
    {
        var allTowns = await GetAll();
        return await _resolver.Resolve(address, allTowns);
    }
}