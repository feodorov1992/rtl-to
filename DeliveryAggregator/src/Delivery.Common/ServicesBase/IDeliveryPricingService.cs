using Delivery.Common.Models.AddressResolve;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Requests;

namespace Delivery.Common.ServicesBase;

public interface IDeliveryPricingService
{
    Task<IReadOnlyCollection<DeliveryPricingResult>> GetDeliveryPrices(DeliveryPricingRequest request,
        AddressShortModel from, AddressShortModel to);
}