namespace Delivery.DHL.Models;

public record CalculatePriceResponseModel
{
    public ErrorModel[] Errors { get; init; }
    
    public CalculatePriceItemModel Success { get; init; }
}