namespace Delivery.DHL.Models;

public record CalculatePriceRequestModel
{
    public string CityFrom { get; init; }
    
    public string CountryCodeFrom { get; init; }
    
    public string PostalCodeFrom { get; init; }
    
    public string CityTo { get; init; }
    
    public string CountryCodeTo { get; init; }
    
    public string PostalCodeTo { get; init; }
    
    public DeliveryPieceModel[] Pieces { get; init; }
    
    public string Date { get; init; }
    
    public string PickUpFromTime { get; init; }
    
    public string ShpWindowsTimeZoneId { get; init; }
    
    public string OfficeRoute { get; init; }
    
    public string Language { get; init; }
}