using Delivery.Common.Models.AddressResolve;
using Delivery.Common.Models.DeliveryPricing;
using Delivery.Common.Requests;
using MediatR;

namespace Delivery.Common.Queries;

public class GetDeliveryPricesQuery : IRequest<IReadOnlyCollection<DeliveryPricingResult>>
{
    public DeliveryPricingRequest Request { get; private set; }
    
    public AddressShortModel From { get; private set; }
    
    public AddressShortModel To { get; private set; }

    public GetDeliveryPricesQuery(DeliveryPricingRequest request)
    {
        Request = request;
    }

    public void AddFormattedAddresses(AddressShortModel from, AddressShortModel to)
    {
        From = from;
        To = to;
    }
}