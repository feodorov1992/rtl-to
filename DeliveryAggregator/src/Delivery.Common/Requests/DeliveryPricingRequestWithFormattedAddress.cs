using Delivery.Common.Models.AddressResolve;

namespace Delivery.Common.Requests;

public record DeliveryPricingRequestWithFormattedAddress : DeliveryPricingRequest
{
    public AddressShortModel FormattedFromAddress { get; init; }
    
    public AddressShortModel FormattedToAddress { get; init; }
}