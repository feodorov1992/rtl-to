namespace Delivery.DHL.Models;

public record DeliveryPieceModel
{
    public int Id { get; init; }
    
    public float Weight { get; init; }
    
    public int Type { get; init; }
    
    public float Width { get; init; }
    
    public float Height { get; init; }
    
    public float Depth { get; init; }
}