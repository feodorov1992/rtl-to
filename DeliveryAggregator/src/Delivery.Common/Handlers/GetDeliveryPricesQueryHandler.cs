using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Queries;
using Delivery.Common.ServicesBase;
using MediatR;

namespace Delivery.Common.Handlers;

public class GetDeliveryPricesQueryHandler : IRequestHandler<GetDeliveryPricesQuery, IReadOnlyCollection<DeliveryPricingResult>>
{
    private readonly IDeliveryPricingService _deliveryPricingService;

    public GetDeliveryPricesQueryHandler(IDeliveryPricingService deliveryPricingService)
    {
        _deliveryPricingService = deliveryPricingService;
    }
    
    public async Task<IReadOnlyCollection<DeliveryPricingResult>> Handle(GetDeliveryPricesQuery request, CancellationToken cancellationToken)
    {
        return await _deliveryPricingService.GetDeliveryPrices(request.Request, request.From, request.To);
    }
}