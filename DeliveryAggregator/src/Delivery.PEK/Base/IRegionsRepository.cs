using Delivery.PEK.Models;

namespace Delivery.PEK.Base;

public interface IRegionsRepository
{
    Task<IReadOnlyCollection<GeoRegion>> GetAll();
    Task<GeoRegion> GetByRegionName(string regionName);
}