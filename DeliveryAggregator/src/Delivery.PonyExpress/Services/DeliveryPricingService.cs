using Delivery.Common.Models.AddressResolve;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Requests;
using Delivery.Common.ServicesBase;
using Delivery.PonyExpress.UI_WebService;

namespace Delivery.PonyExpress.Services;

public class DeliveryPricingService : IDeliveryPricingService
{
    private readonly IUI_Service _ponyService;

    public DeliveryPricingService(IUI_Service ponyService)
    {
        _ponyService = ponyService;
    }

    public Task<IReadOnlyCollection<DeliveryPricingResult>> GetDeliveryPrices(DeliveryPricingRequest request,
        AddressShortModel from, AddressShortModel to)
    {
        throw new NotImplementedException();
    }
}