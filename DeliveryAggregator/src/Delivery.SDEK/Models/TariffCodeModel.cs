namespace Delivery.SDEK.Models;

public record TariffCodeModel
{
    public int TariffCode { get; init; }
    
    public string TariffName { get; init; }
    
    public string TariffDescription { get; init; }
    
    public int DeliveryMode { get; init; }
    
    public decimal DeliverySum { get; init; }
    
    public int PeriodMin { get; init; }
    
    public int PeriodMax { get; init; }
}