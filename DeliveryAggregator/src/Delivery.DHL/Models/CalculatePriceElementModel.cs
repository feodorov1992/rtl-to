namespace Delivery.DHL.Models;

public record CalculatePriceElementModel
{
    public decimal Price { get; init; }
    
    public int TotalTransitDays { get; init; }
}