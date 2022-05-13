using Delivery.Common.Models.AddressResolve;

namespace Delivery.Common.ServicesBase;

public interface IAddressResolveService
{
    Task<AddressShortModel> Resolve(string address);
}