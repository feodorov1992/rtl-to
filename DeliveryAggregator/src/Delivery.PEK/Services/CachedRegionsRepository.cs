using Delivery.PEK.Base;
using Delivery.PEK.Models;
using Microsoft.Extensions.Caching.Memory;

namespace Delivery.PEK.Services;

public class CachedRegionsRepository : IRegionsRepository
{
    private readonly IRegionsRepository _repository;
    private readonly IMemoryCache _memoryCache;

    public CachedRegionsRepository(IRegionsRepository repository, IMemoryCache memoryCache)
    {
        _repository = repository;
        _memoryCache = memoryCache;
    }

    public async Task<IReadOnlyCollection<GeoRegion>> GetAll()
    {
        var items = await _repository.GetAll();

        foreach (var item in items)
            _memoryCache.Set(item.Name, item, TimeSpan.FromHours(1));

        return items;
    }

    public async Task<GeoRegion> GetByRegionName(string regionName)
    {
        var cached = _memoryCache.Get<GeoRegion>(regionName);
        if (cached is null)
        {
            await GetAll();
            cached = _memoryCache.Get<GeoRegion>(regionName);
        }

        return cached;
    }
}