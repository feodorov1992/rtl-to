namespace Delivery.DHL.Models;

public record ErrorModel
{
    public string Code { get; init; }
    
    public string Message { get; init; }
}