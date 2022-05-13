namespace Delivery.Common.Models.AddressResolve;

public record AddressShortModel
{
    public string FormattedAddress { get; init; }
    
    public string Region { get; init; }
    
    public string Country { get; init; }
    
    public string City { get; init; }
    
    public string Street { get; init; }
    
    public string House { get; init; }
    
    public string Flat { get; init; }
    
    public string KladrId { get; init; }
    
    public string CountryCodeIso { get; init; }
    
    public string District { get; init; }
    
    public string PostalCode { get; init; }
}