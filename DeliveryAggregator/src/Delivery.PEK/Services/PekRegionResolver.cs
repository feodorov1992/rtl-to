using Delivery.Common.Models.AddressResolve;
using Delivery.PEK.Base;
using Delivery.PEK.Models;

namespace Delivery.PEK.Services;

public class PekRegionResolver
{
    private readonly IRegionsRepository _regionsRepository;

    public PekRegionResolver(IRegionsRepository regionsRepository)
    {
        _regionsRepository = regionsRepository;
    }
    
    public async Task<PekRegion> Resolve(AddressShortModel address, IReadOnlyCollection<PekTown> towns)
    {
        var flattened = towns.SelectMany(x => x.Regions.Select(i => new
        {
            Region = i,
            Parent = x
        }));
        
        var regions = flattened.Where(x => x.Region.Name.Contains(address.City)).ToList();

        if (regions.Any() == false)
            return null;

        if (regions.Count == 1)
            return regions.First().Region;
        
        var withDistrict = regions.Where(x => x.Region.Name.Contains(address.District)).ToList();
        if (regions.Count == 1)
            return withDistrict.First().Region;

        var geoRegion = await _regionsRepository.GetByRegionName(address.Region);
        if (geoRegion is not null)
        {
            var withCapital = withDistrict.Where(x => x.Parent.Name.Equals(geoRegion.Capital, StringComparison.InvariantCultureIgnoreCase))
                .ToList();
            if (withCapital.Count == 1)
                return withCapital.First().Region;
        }

        var fullCoincidence = regions.Where(x => x.Region.Name == address.City).ToList();
        if (fullCoincidence.Count == 1)
            return fullCoincidence.First().Region;

        return withDistrict.FirstOrDefault()?.Region 
               ?? fullCoincidence.FirstOrDefault()?.Region 
               ?? regions.FirstOrDefault()?.Region;
    }
}