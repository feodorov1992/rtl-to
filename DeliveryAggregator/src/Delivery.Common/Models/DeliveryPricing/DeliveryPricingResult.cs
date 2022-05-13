namespace Delivery.Common.Models.DeliveryPricing;

public record DeliveryPricingResult
{
    public string CounterpartyId { get; init; }
    
    public int MinTime { get; init; }
    
    public int MaxTime { get; init; }
    
    public decimal Price { get; init; }
}