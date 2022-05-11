namespace Delivery.DHL.Models;

public record CalculatePriceItemModel
{
    public CalculatePriceElementModel Walk { get; init; }
    
    public CalculatePriceElementModel Click { get; init; }
    
    public CalculatePriceElementModel Call { get; init; }   
}