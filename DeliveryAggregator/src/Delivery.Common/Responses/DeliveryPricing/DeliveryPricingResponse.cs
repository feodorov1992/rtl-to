namespace Delivery.Common.Responses.DeliveryPricing;

public record DeliveryPricingResponse
{
    public string CounterpartyId { get; init; }
    
    public int MinTime { get; init; }
    
    public int MaxTime { get; init; }
    
    public decimal Price { get; init; }
}