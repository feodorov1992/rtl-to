using Delivery.Common.Models.AddressResolve;
using Delivery.PEK.Models;

namespace Delivery.PEK.Base;

public interface ITownsRepository
{
    Task<IReadOnlyCollection<PekTown>> GetAll();
    Task<PekRegion> GetTown(AddressShortModel address);
}