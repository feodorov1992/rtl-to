using Newtonsoft.Json;

namespace Delivery.DHL.Models;

public record AutoCompleteItemModel
{
    public string CountryCode { get; init; }
    
    [JsonProperty("DctCityName")]
    public string CityName { get; init; }

    public string IataCode { get; init; }
    
    public string CommonAlias { get; init; }
    
    public string CityAlias { get; init; }
    
    public string PostalCode { get; init; }
    
    public string FacilityCode { get; init; }
    
    public string NonDhlCode { get; init; }
    
    public string WindowsTimeZoneId { get; init; }
    
    public int PostfixNeeded { get; init; }
    
    public int IsRpaAllowed { get; init; }
}