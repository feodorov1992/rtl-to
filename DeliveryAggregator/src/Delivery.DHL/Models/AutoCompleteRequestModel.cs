namespace Delivery.DHL.Models;

public record AutoCompleteRequestModel
{
    public string CountryCode { get; init; }
    
    public int MaxCount { get; init; }
    
    public string RequestedEntity { get; init; }
    
    public string SearchString { get; init; }
    
    public string Language { get; init; }
}